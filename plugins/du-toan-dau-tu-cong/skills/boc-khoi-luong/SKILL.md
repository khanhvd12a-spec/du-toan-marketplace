---
name: boc-khoi-luong
description: Đo bóc khối lượng công trình xây dựng từ bản vẽ thiết kế dạng PDF hoặc ảnh, theo hướng dẫn đo bóc hiện hành của Bộ Xây dựng. Dùng khi cần lập bảng khối lượng, bảng tính diễn giải hoặc kiểm tra khối lượng theo bản vẽ. Nếu có file AutoCAD (DWG/DXF), dùng skill boc-khoi-luong-autocad.
---

# Bóc khối lượng từ bản vẽ (PDF, ảnh)

Có file DWG/DXF thì ưu tiên skill `boc-khoi-luong-autocad`, vì đo từ hình học chính xác hơn đọc ảnh. Skill này dùng để bổ sung kích thước chỉ có trên bản vẽ in (chiều cao, chiều dày, mác vật liệu) và để kiểm tra chéo.

## Đầu vào
- Bộ bản vẽ, danh mục bản vẽ, thuyết minh, chỉ dẫn kỹ thuật.
- Phạm vi bóc: hạng mục, bước thiết kế (TKCS, TKKT, TKBVTC).
Thiếu thì hỏi trước khi bóc.

## Quy tắc đo bóc (xem `can-cu-phap-ly`, mục "Đo bóc khối lượng")
- Hướng dẫn đo bóc hiện hành theo một nguồn là QĐ 1041/QĐ-BXD ngày 26/6/2026; trước đó là Phụ lục VI TT 13/2021. Văn bản này có mức tin cậy Thấp: nếu người dùng có văn bản gốc, áp dụng theo văn bản gốc.
- Khối lượng chia theo công trình → hạng mục → bộ phận kết cấu → công tác, theo trình tự thi công.
- Đơn vị tính khớp với đơn vị của định mức TT 38/2026 cho mã công tác dự kiến.
- Khấu trừ phần giao nhau, lỗ cửa và các chi tiết chôn sẵn theo quy tắc của hướng dẫn. Ghi rõ đã trừ những gì.
- Mỗi dòng ghi số hiệu bản vẽ nguồn và công thức diễn giải (số lượng × dài × rộng × cao).
- Kích thước không đọc được hoặc mâu thuẫn giữa các bản vẽ: đánh dấu "CẦN XÁC NHẬN", không giả định.

## Đầu ra (Excel, Python + openpyxl)
- `Dien giai`: STT | Mã hiệu | Tên công tác | Bản vẽ | Diễn giải | SL | Dài | Rộng | Cao | Khối lượng (công thức) | Đơn vị | Ghi chú
- `Tong hop`: tổng theo mã công tác (SUMIF)
- `Can xac nhan`: danh sách câu hỏi cho đơn vị thiết kế
Ghi chú cuối: "Bản nháp hỗ trợ; cần kỹ sư định giá kiểm tra."
