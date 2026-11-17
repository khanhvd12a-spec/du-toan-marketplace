# du-toan-dau-tu-cong

Plugin Claude Code hỗ trợ bóc khối lượng (từ PDF và AutoCAD), lập và thẩm định dự toán xây dựng, và tra cứu trình tự thủ tục đầu tư công tại Việt Nam. Căn cứ pháp lý được rà soát ngày 17/11/2026.

## Lệnh
| Lệnh | Việc |
|---|---|
| `/du-toan-dau-tu-cong:boc-khoi-luong <bản vẽ PDF>` | Bóc khối lượng từ PDF hoặc ảnh |
| `/du-toan-dau-tu-cong:boc-khoi-luong-cad <file.dwg/.dxf> [cấu hình.json]` | Bóc khối lượng tự động từ AutoCAD |
| `/du-toan-dau-tu-cong:lap-du-toan <khối lượng> <tỉnh> <thời điểm>` | Lập dự toán |
| `/du-toan-dau-tu-cong:tham-dinh <file dự toán>` | Thẩm định độc lập |
| `/du-toan-dau-tu-cong:thu-tuc <nhóm dự án> <bước>` | Tra cứu trình tự thủ tục |

## Yêu cầu
- Python 3.10+ với `pip install ezdxf openpyxl`
- File DWG: lưu sang DXF trong AutoCAD, hoặc cài ODA File Converter hay LibreDWG

## Lưu ý
- Mọi kết quả là bản nháp. Người có chứng chỉ hành nghề định giá xây dựng phải kiểm tra và ký.
- `skills/can-cu-phap-ly/SKILL.md` ghi mức tin cậy của từng văn bản. Các dòng có mức tin cậy Thấp cần đối chiếu với văn bản gốc.
