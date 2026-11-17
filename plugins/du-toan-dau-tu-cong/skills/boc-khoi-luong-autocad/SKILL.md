---
name: boc-khoi-luong-autocad
description: Bóc khối lượng tự động từ bản vẽ AutoCAD (DWG, DXF). Đo chiều dài, diện tích (polyline kín, hatch), đếm block theo layer, rồi ánh xạ sang công tác và mã định mức và xuất Excel có công thức. Dùng khi người dùng có file .dwg hoặc .dxf và cần bảng khối lượng.
---

# Bóc khối lượng từ AutoCAD

Script: `scripts/dxf_takeoff.py` trong thư mục của skill này. Cần `pip install ezdxf openpyxl`.

## Bước 1: Chuẩn bị file
- File .dxf đọc trực tiếp.
- File .dwg cần một trong hai cách: (a) người dùng mở AutoCAD, chạy SAVEAS và chọn định dạng DXF; hoặc (b) cài ODA File Converter (miễn phí) hoặc LibreDWG (`dwg2dxf`), sau đó script tự chuyển.
- Mỗi lần chạy chỉ đo Model space. Nếu bản vẽ có nhiều tầng hoặc hạng mục trong cùng một file, đề nghị người dùng tách file hoặc dùng layer riêng cho từng phần.

## Bước 2: Khảo sát
```
python3 <skill_dir>/scripts/dxf_takeoff.py khao-sat banve.dxf
```
Đọc kết quả, rồi báo cho người dùng:
- Đơn vị bản vẽ. Nếu là "mm (giả định)", hỏi lại và kiểm tra bằng một kích thước đã biết, ví dụ một trục hoặc nhịp đọc từ sheet "Kich thuoc".
- Danh sách layer với tổng dài và tổng diện tích, và danh sách block với số lượng.
- Layer có polyline hở. Những layer này không tính được diện tích, cần người vẽ đóng kín hoặc hatch lại.
- Các đối tượng trên layer 0.

## Bước 3: Lập file cấu hình ánh xạ (hỏi người dùng những gì bản vẽ 2D không có)
```json
{
  "don_vi_ban_ve": "mm",
  "cong_tac": [
    {"ma_hieu": "AE.xxxxx", "ten": "Xây tường gạch dày 220, cao 3,3 m", "layer": "TUONG-220",
     "dai_luong": "chieu_dai", "he_so": "0.22*3.3", "dien_giai": "dày 0,22 x cao 3,3", "don_vi": "m3"},
    {"ten": "Lát nền gạch 600x600", "layer": "SAN-*", "dai_luong": "dien_tich", "don_vi": "m2"},
    {"ten": "Cửa đi D1", "block": "D1", "dai_luong": "so_luong", "don_vi": "bộ"}
  ]
}
```
- `dai_luong`: `chieu_dai` (m), `dien_tich` (m²) hoặc `so_luong` (đếm block).
- `layer` và `block` chỉ dùng ký tự đại diện `*` và `?`.
- `he_so` chỉ gồm số và các phép + - * / ( ). Dùng nó cho các kích thước còn thiếu trên mặt bằng: chiều cao, chiều dày, tiết diện, số mặt trát.
- `ma_hieu` lấy theo định mức TT 38/2026. Nếu không chắc, để trống và ghi chú lại. Không đoán mã hiệu.
- Bản vẽ 2D không cho biết chiều cao, mác bê tông hay cốt thép. Những thông số này phải lấy từ mặt cắt, thuyết minh hoặc hỏi người dùng.

## Bước 4: Bóc và kiểm tra
```
python3 <skill_dir>/scripts/dxf_takeoff.py boc banve.dxf --config cau_hinh.json --out khoi_luong.xlsx
```
Excel gồm các sheet: `Thong tin` (đơn vị, cảnh báo), `Dien giai` (công thức `=Giá trị đo × Hệ số`), `Doi tuong` (từng đối tượng, có handle để tìm lại trong CAD), `Theo layer` (SUMIF), `Block`, `Text`, `Kich thuoc`.

Sau khi chạy, luôn làm các bước sau:
1. Đọc cảnh báo. Mọi dòng "KHÔNG có đối tượng" và mọi "diện tích = 0" phải được giải thích.
2. Đối chiếu 2–3 khối lượng lớn nhất với kích thước ghi trên bản vẽ (sheet `Kich thuoc` hoặc bản PDF).
3. Kiểm tra việc khấu trừ. Script KHÔNG tự trừ lỗ cửa hay phần giao nhau giữa tường và cột. Thêm dòng trừ riêng (hệ số âm), hoặc ghi rõ phần chưa trừ.
4. Nhắc người dùng: đường vẽ trùng hoặc chồng lên nhau sẽ bị đếm hai lần. Nên chạy lệnh OVERKILL trong AutoCAD trước khi bóc.

Kết quả chuyển sang skill `lap-du-toan`.
