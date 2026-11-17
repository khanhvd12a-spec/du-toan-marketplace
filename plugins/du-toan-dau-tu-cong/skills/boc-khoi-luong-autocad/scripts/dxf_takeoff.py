#!/usr/bin/env python3
"""Bóc khối lượng từ bản vẽ AutoCAD (DXF; DWG qua bộ chuyển đổi).

Hai chế độ:
  khao-sat : liệt kê layer, block, đơn vị bản vẽ, cảnh báo -> để lập file cấu hình
  boc      : đo theo file cấu hình (layer/block -> công tác) và xuất Excel có công thức

Ví dụ:
  python3 dxf_takeoff.py khao-sat banve.dxf
  python3 dxf_takeoff.py boc banve.dxf --config cau_hinh.json --out khoi_luong.xlsx

Yêu cầu: pip install ezdxf openpyxl
DWG: cần ODA File Converter (ezdxf.addons.odafc) hoặc LibreDWG (dwg2dxf).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

try:
    import ezdxf
    from ezdxf import path as ezpath
except ImportError:  # pragma: no cover
    sys.exit("Thiếu thư viện ezdxf. Cài bằng: pip install ezdxf openpyxl")

# $INSUNITS -> hệ số đổi 1 đơn vị bản vẽ ra mét
INSUNITS_TO_M = {1: 0.0254, 2: 0.3048, 4: 0.001, 5: 0.01, 6: 1.0, 14: 0.1}
UNIT_NAME_TO_M = {"mm": 0.001, "cm": 0.01, "dm": 0.1, "m": 1.0, "inch": 0.0254, "ft": 0.3048}
FLATTEN_TOL = 0.5  # sai số xấp xỉ cung/spline, theo đơn vị bản vẽ

DAI_LUONG = {"chieu_dai", "dien_tich", "so_luong"}
SAFE_EXPR = re.compile(r"^[0-9\.\s\+\-\*/\(\)]+$")


# ---------------------------------------------------------------- đọc file
def load_doc(src: Path):
    if src.suffix.lower() == ".dxf":
        return ezdxf.readfile(src)
    if src.suffix.lower() != ".dwg":
        sys.exit(f"Không hỗ trợ định dạng {src.suffix}. Dùng .dxf hoặc .dwg")
    try:
        from ezdxf.addons import odafc
        if odafc.is_installed():
            return odafc.readfile(str(src))
    except Exception:
        pass
    if shutil.which("dwg2dxf"):
        out = Path(tempfile.mkdtemp()) / (src.stem + ".dxf")
        subprocess.run(["dwg2dxf", "-o", str(out), str(src)], check=True, capture_output=True)
        return ezdxf.readfile(out)
    sys.exit(
        "Không đọc được DWG: chưa có bộ chuyển đổi.\n"
        "Cách 1: trong AutoCAD dùng SAVEAS -> chọn AutoCAD DXF.\n"
        "Cách 2: cài ODA File Converter (miễn phí) hoặc LibreDWG (dwg2dxf)."
    )


def unit_factor(doc, override: str | None, warnings: list) -> tuple[float, str]:
    if override:
        if override not in UNIT_NAME_TO_M:
            sys.exit(f"Đơn vị '{override}' không hợp lệ. Chọn: {', '.join(UNIT_NAME_TO_M)}")
        return UNIT_NAME_TO_M[override], override
    code = doc.header.get("$INSUNITS", 0)
    if code in INSUNITS_TO_M:
        name = {1: "inch", 2: "ft", 4: "mm", 5: "cm", 6: "m", 14: "dm"}[code]
        return INSUNITS_TO_M[code], name
    warnings.append(
        "Bản vẽ không khai báo đơn vị ($INSUNITS=0). Đang GIẢ ĐỊNH mm. "
        "Kiểm tra một kích thước đã biết rồi chạy lại với --don-vi."
    )
    return 0.001, "mm (giả định)"


# ---------------------------------------------------------------- đo hình học
def flatten_pts(e):
    p = ezpath.make_path(e)
    return [(v.x, v.y) for v in p.flattening(FLATTEN_TOL)]


def poly_len(pts, closed=False):
    s = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    if closed and len(pts) > 2 and pts[0] != pts[-1]:
        s += math.dist(pts[-1], pts[0])
    return s


def shoelace(pts):
    n = len(pts)
    if n < 3:
        return 0.0
    return abs(sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))) / 2


def hatch_area(h):
    total = 0.0
    for bp in h.paths:
        try:
            p = ezpath.from_hatch_boundary_path(bp, ocs=h.ocs(), elevation=h.dxf.elevation.z)
            pts = [(v.x, v.y) for v in p.flattening(FLATTEN_TOL)]
        except Exception:
            continue
        a = shoelace(pts)
        external = bp.path_type_flags & (1 | 16)  # EXTERNAL | OUTERMOST
        total += a if external else -a
    return abs(total)


def measure(e):
    """Trả về (chiều dài, diện tích, kín?) theo đơn vị bản vẽ."""
    t = e.dxftype()
    if t == "LINE":
        return e.dxf.start.distance(e.dxf.end), 0.0, False
    if t in ("LWPOLYLINE", "POLYLINE"):
        if t == "POLYLINE" and (e.is_poly_face_mesh or e.is_polygon_mesh):
            return 0.0, 0.0, False
        closed = bool(e.closed) if t == "LWPOLYLINE" else e.is_closed
        pts = flatten_pts(e)
        length = poly_len(pts, closed)
        return length, (shoelace(pts) if closed else 0.0), closed
    if t == "CIRCLE":
        r = e.dxf.radius
        return 2 * math.pi * r, math.pi * r * r, True
    if t in ("ARC", "ELLIPSE", "SPLINE"):
        pts = flatten_pts(e)
        closed = t == "SPLINE" and e.closed
        return poly_len(pts), (shoelace(pts) if closed else 0.0), closed
    if t == "HATCH":
        return 0.0, hatch_area(e), True
    return 0.0, 0.0, False


def block_name(ins):
    name = ins.dxf.name
    if name.startswith("*U"):  # block động -> lấy tên gốc
        try:
            br = ins.doc.blocks.get(name).block_record
            xd = br.get_xdata("AcDbBlockRepBTag") if br.has_xdata("AcDbBlockRepBTag") else None
            if xd:
                for code, val in xd:
                    if code == 1005:
                        return ins.doc.entitydb[val].dxf.name
        except Exception:
            pass
    return name


# ---------------------------------------------------------------- duyệt bản vẽ
def collect(doc, explode_blocks: bool):
    rows, texts, dims, blocks = [], [], [], defaultdict(int)

    def visit(e, layer_override=None, depth=0):
        layer = e.dxf.layer
        if layer == "0" and layer_override:
            layer = layer_override  # đối tượng trên layer 0 trong block lấy layer của block
        t = e.dxftype()
        if t == "INSERT":
            blocks[(layer, block_name(e))] += 1
            if explode_blocks and depth < 8:
                try:
                    for ve in e.virtual_entities():
                        visit(ve, layer, depth + 1)
                except Exception:
                    pass
            return
        if t in ("TEXT", "MTEXT"):
            txt = e.plain_text() if t == "MTEXT" else e.dxf.text
            texts.append((layer, txt.strip(), round(e.dxf.insert.x, 1), round(e.dxf.insert.y, 1)))
            return
        if t == "DIMENSION":
            try:
                m = e.get_measurement()
                val = m if isinstance(m, (int, float)) else abs(m)
            except Exception:
                val = None
            dims.append((layer, e.dxf.get("text", ""), val))
            return
        try:
            length, area, closed = measure(e)
        except Exception:
            return
        if length or area:
            rows.append({"handle": e.dxf.get("handle", "(trong block)"), "type": t, "layer": layer,
                         "length": length, "area": area, "closed": closed, "in_block": depth > 0})

    for e in doc.modelspace():
        visit(e)
    return rows, texts, dims, blocks


# ---------------------------------------------------------------- xuất Excel
def write_xlsx(out, rows, texts, dims, blocks, k, unit_label, warnings, config, src):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    bold = Font(bold=True)
    head_fill = PatternFill("solid", fgColor="DDEBF7")

    def sheet(title, header, widths=None):
        ws = wb.create_sheet(title)
        ws.append(header)
        for c in ws[1]:
            c.font, c.fill = bold, head_fill
            c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.freeze_panes = "A2"
        for i, w in enumerate(widths or [], 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        return ws

    wb.remove(wb.active)

    # --- đối tượng chi tiết (nguồn cho mọi công thức)
    wo = sheet("Doi tuong", ["Handle", "Loại", "Layer", "Dài (m)", "Diện tích (m²)", "Kín", "Trong block"],
               [12, 12, 22, 12, 14, 6, 10])
    for r in rows:
        wo.append([r["handle"], r["type"], r["layer"], round(r["length"] * k, 4),
                   round(r["area"] * k * k, 4), "x" if r["closed"] else "", "x" if r["in_block"] else ""])
    n_obj = len(rows) + 1
    rng = lambda col: f"'Doi tuong'!${col}$2:${col}${max(n_obj, 2)}"

    # --- tổng hợp theo layer (công thức SUMIF về sheet Doi tuong)
    wl = sheet("Theo layer", ["Layer", "Số đối tượng", "Tổng dài (m)", "Tổng diện tích (m²)"], [26, 12, 14, 18])
    for i, layer in enumerate(sorted({r["layer"] for r in rows}), start=2):
        wl.append([layer, f'=COUNTIF({rng("C")},A{i})', f'=SUMIF({rng("C")},A{i},{rng("D")})',
                   f'=SUMIF({rng("C")},A{i},{rng("E")})'])

    wb_ = sheet("Block", ["Layer", "Tên block", "Số lượng"], [22, 30, 10])
    for (layer, name), cnt in sorted(blocks.items()):
        wb_.append([layer, name, cnt])
    n_blk = len(blocks) + 1

    wt = sheet("Text", ["Layer", "Nội dung", "X", "Y"], [20, 50, 12, 12])
    for t in texts:
        wt.append(list(t))
    wd = sheet("Kich thuoc", ["Layer", "Text ghi đè", "Giá trị đo (đv bản vẽ)"], [20, 20, 20])
    for d in dims:
        wd.append(list(d))

    # --- diễn giải khối lượng theo cấu hình
    if config:
        ws = sheet("Dien giai", ["STT", "Mã hiệu", "Tên công tác", "Nguồn (layer/block)", "Đại lượng đo",
                                 "Giá trị đo", "Hệ số", "Diễn giải hệ số", "Khối lượng", "Đơn vị", "Ghi chú"],
                   [5, 12, 34, 22, 12, 12, 10, 26, 12, 8, 30])
        for i, ct in enumerate(config.get("cong_tac", []), start=1):
            r = i + 1
            dl = ct.get("dai_luong", "chieu_dai")
            if dl not in DAI_LUONG:
                warnings.append(f"Công tác '{ct.get('ten')}': dai_luong '{dl}' không hợp lệ")
                continue
            note = ct.get("ghi_chu", "")
            if dl == "so_luong":
                pat = ct.get("block", "*")
                lay = ct.get("layer", "*")
                src_lbl = f"block {pat}" + ("" if lay == "*" else f" / layer {lay}")
                val = sum(c for (l, n), c in blocks.items() if fnmatch.fnmatchcase(n, pat) and fnmatch.fnmatchcase(l, lay))
                if not val:
                    note = (note + "; " if note else "") + "KHÔNG tìm thấy block khớp"
                measured = (f'=SUMIFS(Block!$C$2:$C${max(n_blk, 2)},Block!$B$2:$B${max(n_blk, 2)},"{pat}",'
                            f'Block!$A$2:$A${max(n_blk, 2)},"{lay}")')
            else:
                pat = ct.get("layer")
                if not pat:
                    warnings.append(f"Công tác '{ct.get('ten')}': thiếu 'layer'")
                    continue
                src_lbl = f"layer {pat}"
                col = "D" if dl == "chieu_dai" else "E"
                measured = f'=SUMIF({rng("C")},"{pat}",{rng(col)})'
                matched = [x for x in rows if fnmatch.fnmatchcase(x["layer"], pat)]
                if not matched:
                    note = (note + "; " if note else "") + "KHÔNG có đối tượng trên layer này"
                if dl == "dien_tich" and matched and not any(x["closed"] for x in matched):
                    note = (note + "; " if note else "") + "layer không có đường kín/hatch -> diện tích = 0"
            he_so = str(ct.get("he_so", "1"))
            if not SAFE_EXPR.match(he_so):
                warnings.append(f"Công tác '{ct.get('ten')}': hệ số '{he_so}' chỉ được chứa số và + - * / ( )")
                he_so = "1"
            ws.append([i, ct.get("ma_hieu", ""), ct.get("ten", ""), src_lbl, dl, measured, f"={he_so}",
                       ct.get("dien_giai", ""), f"=F{r}*G{r}", ct.get("don_vi", ""), note])
            ws.cell(row=r, column=9).font = bold
        wb.move_sheet("Dien giai", offset=-len(wb.sheetnames) + 1)

    wi = sheet("Thong tin", ["Mục", "Giá trị"], [28, 80])
    wi.append(["File bản vẽ", str(src)])
    wi.append(["Đơn vị bản vẽ", unit_label])
    wi.append(["Hệ số đổi ra mét", k])
    wi.append(["Sai số xấp xỉ cung", f"{FLATTEN_TOL} đơn vị bản vẽ"])
    wi.append(["Lưu ý", "Chỉ đo Model space. Kết quả là bản nháp; cần đối chiếu bản vẽ và người có chứng chỉ kiểm tra."])
    for w in warnings:
        wi.append(["CẢNH BÁO", w])
    wb.move_sheet("Thong tin", offset=-len(wb.sheetnames) + 1)
    wb.save(out)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("che_do", choices=["khao-sat", "boc"])
    ap.add_argument("file")
    ap.add_argument("--config", help="file JSON ánh xạ layer/block -> công tác (chế độ boc)")
    ap.add_argument("--out", help="file Excel đầu ra")
    ap.add_argument("--don-vi", choices=list(UNIT_NAME_TO_M), help="ghi đè đơn vị bản vẽ")
    ap.add_argument("--khong-tach-block", action="store_true", help="không đo hình học bên trong block")
    a = ap.parse_args()

    src = Path(a.file)
    doc = load_doc(src)
    warnings: list[str] = []
    config = None
    if a.config:
        config = json.loads(Path(a.config).read_text(encoding="utf-8"))
    k, unit_label = unit_factor(doc, a.don_vi or (config or {}).get("don_vi_ban_ve"), warnings)
    rows, texts, dims, blocks = collect(doc, not a.khong_tach_block)

    open_area_layers = {r["layer"] for r in rows if r["type"] in ("LWPOLYLINE", "POLYLINE") and not r["closed"]}
    if any(r["layer"] == "0" for r in rows):
        warnings.append("Có đối tượng vẽ trên layer 0 - dễ bị bỏ sót khi ánh xạ công tác.")

    if a.che_do == "khao-sat":
        by_layer = defaultdict(lambda: [0, 0.0, 0.0, 0])
        for r in rows:
            s = by_layer[r["layer"]]
            s[0] += 1; s[1] += r["length"] * k; s[2] += r["area"] * k * k; s[3] += r["closed"]
        print(f"Đơn vị bản vẽ: {unit_label} (1 đv = {k} m)")
        print(f"\n{'Layer':30} {'Số ĐT':>6} {'Dài (m)':>12} {'DT kín (m²)':>12} {'Số kín':>6}")
        for layer, (n, L, A, c) in sorted(by_layer.items()):
            print(f"{layer[:30]:30} {n:>6} {L:>12.2f} {A:>12.2f} {c:>6}")
        print(f"\n{'Layer':24} {'Block':30} {'SL':>5}")
        for (layer, name), cnt in sorted(blocks.items()):
            print(f"{layer[:24]:24} {name[:30]:30} {cnt:>5}")
        print(f"\nText: {len(texts)} | Dim: {len(dims)}")
        if open_area_layers:
            print("Layer có polyline hở (không tính được diện tích):", ", ".join(sorted(open_area_layers)))
        for w in warnings:
            print("CẢNH BÁO:", w)
        if a.out:
            write_xlsx(a.out, rows, texts, dims, blocks, k, unit_label, warnings, None, src)
            print("Đã ghi", a.out)
        return

    if not config:
        sys.exit("Chế độ 'boc' cần --config. Chạy 'khao-sat' trước để biết layer/block.")
    out = a.out or str(src.with_name(src.stem + "_khoi_luong.xlsx"))
    write_xlsx(out, rows, texts, dims, blocks, k, unit_label, warnings, config, src)
    print("Đã ghi", out)
    for w in warnings:
        print("CẢNH BÁO:", w)


if __name__ == "__main__":
    main()
