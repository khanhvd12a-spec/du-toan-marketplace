---
name: tham-dinh-du-toan
description: Thẩm định, thẩm tra dự toán xây dựng công trình đầu tư công theo Luật Xây dựng 135/2025, NĐ 217/2026 và NĐ 206/2026. Dùng khi cần kiểm tra khối lượng so với bản vẽ, việc áp dụng định mức, đơn giá và cách tính chi phí, và lập báo cáo hoặc thông báo kết quả thẩm định.
---

# Thẩm định dự toán

## Xác định ai thẩm định (xem `can-cu-phap-ly`)
- Từ 01/7/2026, theo NĐ 217/2026 (Điều 41, theo nguồn thứ cấp), chủ đầu tư thẩm định và phê duyệt thiết kế triển khai sau thiết kế cơ sở cùng dự toán. Thẩm tra là bắt buộc trong các trường hợp tại khoản 5 Điều 26 và khoản 3 Điều 29 Luật 135/2025, gồm công trình thuộc Phụ lục IV NĐ 217/2026.
- Dự án đã được cơ quan chuyên môn thẩm định trước 01/7/2026 nhưng chưa phê duyệt: áp dụng quy định chuyển tiếp.
- Nói rõ vai trò của người dùng: chủ đầu tư, đơn vị thẩm tra hay cơ quan chuyên môn.

## Nội dung kiểm tra
1. Khối lượng chủ yếu có phù hợp với thiết kế không. Lấy mẫu các công tác chiếm khoảng 80% chi phí trước. Nếu có file CAD, đo lại bằng skill `boc-khoi-luong-autocad`.
2. Việc áp dụng định mức (TT 38/2026 hoặc định mức cũ theo chế độ chuyển tiếp) và giá vật liệu, nhân công, máy có đúng thời điểm và địa phương không.
3. Tỷ lệ chi phí gián tiếp, thu nhập chịu thuế tính trước, VAT, dự phòng có đúng TT 36/2026 không.
4. Cộng dồn và công thức Excel có đúng không. Có dòng trùng lặp không.
5. Dự toán có nằm trong tổng mức đầu tư đã duyệt không.

## Cách làm
- Giao subagent `tham-dinh-vien` rà soát độc lập.
- Mỗi phát hiện ghi: vị trí (sheet/dòng), giá trị đề nghị, giá trị thẩm định, chênh lệch (đồng), căn cứ điều khoản. Phân biệt "sai chắc chắn" và "cần làm rõ".
- Sắp xếp theo chênh lệch tuyệt đối, giảm dần.

## Đầu ra
- Bảng so sánh: Hạng mục | Giá trị đề nghị | Giá trị thẩm định | Tăng (+) / Giảm (−) | Lý do.
- Dự thảo báo cáo thẩm tra (Mẫu số 11) hoặc thông báo kết quả thẩm định (Mẫu số 12) theo NĐ 217/2026. Nếu không có mẫu gốc, dựng theo bố cục: căn cứ, nội dung, kết quả, kiến nghị, và ghi chú "đối chiếu mẫu gốc".
