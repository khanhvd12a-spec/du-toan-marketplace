---
name: lap-du-toan
description: Lập dự toán xây dựng công trình cho dự án đầu tư công theo NĐ 206/2026/NĐ-CP, TT 36/2026/TT-BXD và định mức TT 38/2026/TT-BXD, từ bảng khối lượng và giá địa phương. Dùng khi cần lập dự toán, đơn giá chi tiết, tổng hợp chi phí xây dựng, thiết bị, quản lý dự án, tư vấn, chi phí khác và dự phòng.
---

# Lập dự toán xây dựng

## Bước 0: Chọn chế độ pháp lý (bắt buộc)
Hỏi ngày phê duyệt tổng mức đầu tư hoặc dự toán. Nếu dự án duyệt trước 01/7/2026, đối chiếu quy định chuyển tiếp: có thể vẫn áp dụng NĐ 10/2021 + TT 11/2021 + TT 12/2021. Nếu không, áp dụng NĐ 206/2026 + TT 36/2026 + TT 38/2026 + TT 37/2026. Ghi chế độ đã chọn ở đầu thuyết minh. Xem chi tiết trong `can-cu-phap-ly`.

## Đầu vào
- Bảng khối lượng, lấy từ `boc-khoi-luong`, `boc-khoi-luong-autocad` hoặc do người dùng cung cấp.
- Địa điểm, thời điểm lập giá, loại và cấp công trình, nguồn vốn, tổng mức đầu tư đã duyệt.
- Công bố giá vật liệu, đơn giá nhân công, giá ca máy của tỉnh. Không tự đặt giá. Giá nào chưa có thì ghi "CHƯA CÓ GIÁ" và tô màu ô đó.

## Quy trình
1. Gán mã định mức theo TT 38/2026 (hoặc TT 12/2021 nếu áp dụng chế độ cũ). Công tác chưa có định mức thì ghi rõ và đề xuất vận dụng định mức tương tự hoặc lập định mức mới theo thủ tục.
2. Lập đơn giá chi tiết: hao phí vật liệu, nhân công, máy theo định mức, nhân với giá địa phương.
3. Tính chi phí xây dựng theo cấu trúc của TT 36/2026 (hoặc TT 11/2021):
   - Chi phí trực tiếp: vật liệu, nhân công, máy.
   - Chi phí gián tiếp: chi phí chung, nhà tạm, công việc không xác định được khối lượng từ thiết kế. Từ TT 36/2026, áp dụng hệ số vùng núi, biên giới, hải đảo theo quy định mới.
   - Thu nhập chịu thuế tính trước.
   - Thuế GTGT theo thuế suất hiện hành.
   Tất cả tỷ lệ % và hệ số phải tra theo bảng hoặc phụ lục của thông tư, và ghi số hiệu bảng trong sheet `Can cu`. Tuyệt đối không dùng tỷ lệ nhớ sẵn.
4. Tổng hợp dự toán: chi phí xây dựng, thiết bị, quản lý dự án, tư vấn, chi phí khác, dự phòng (gồm dự phòng khối lượng phát sinh và dự phòng trượt giá theo chỉ số giá).
5. Kiểm tra: dự toán không vượt tổng mức đầu tư đã duyệt. Nếu vượt, cảnh báo và nêu thủ tục điều chỉnh.

## Đầu ra
File Excel dùng công thức, không ghi số cứng, gồm các sheet `Tong hop`, `Chi phi XD`, `Don gia chi tiet`, `Gia VL-NC-MTC`, `Can cu`, kèm thuyết minh nêu căn cứ, giả định và các điểm cần xác nhận. Ghi chú: "Bản nháp hỗ trợ; người có chứng chỉ định giá xây dựng kiểm tra, ký."
