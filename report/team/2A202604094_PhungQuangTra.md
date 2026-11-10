# Báo cáo cá nhân — PhungQuangTra-2A202604094

## 1. Thông tin thành viên

- Họ tên: Phùng Quang Trà
- MSSV: `2A202604094`
- Email: traquangphung@gmail.com
- Vai trò: Trưởng nhóm — Nhóm **Panda** (`K5-L3B-DAY03-Panda-ResearchAgentToolEval`)

## 2. Phần việc phụ trách

- Điều phối phân công công việc cho 6 thành viên trong [`TEAM.md`](../../TEAM.md) và tổng hợp báo cáo nhóm [`report/team/group_report.md`](group_report.md) (Phần A giới thiệu agent + Phần B phân tích bằng chứng thực nghiệm).
- Rà soát an toàn và vá lỗi xử lý đầu vào cho 2 tool hành động/trình bày kết quả: `send` (`starter_v0/tools/send/tool.py`) và `format` (`starter_v0/tools/format/tool.py`).

## 3. Đóng góp cụ thể

- **Vá lỗi guardrail trong `starter_v0/tools/send/tool.py` (Bug #1):**
  - Trong bản code starter gốc, điều kiện kiểm tra xác nhận được viết là `if not confirmed:`. Khi model truyền chuỗi `confirmed="false"` hoặc `"no"` (thay vì kiểu boolean `False`), Python đánh giá chuỗi khác rỗng là `True`, dẫn đến việc tool **vẫn gửi tin thật lên Telegram** dù chưa được phép.
  - Đã sửa thành kiểm tra kiểu nghiêm ngặt `if confirmed is not True:`: chỉ giá trị boolean `True` mới được gửi; mọi giá trị khác (kể cả chuỗi `"false"`, `"no"`, `"true"`) đều trả `status: needs_confirmation` và không gọi mạng.
- **Vá lỗi chuẩn hóa dữ liệu trong `starter_v0/tools/format/tool.py` (Bug #5):**
  - Khi model truyền `items` có chứa phần tử kiểu `str` hoặc `None` (ví dụ `items=["Tin 1", None]`), code gốc gọi `item.get(...)` gây lỗi `AttributeError: 'str' object has no attribute 'get'`. Ngoài ra, khi `url` chỉ chứa khoảng trắng (ví dụ `"url": "   "`), hàm `_src` vẫn coi là có URL và sinh link rỗng `[VnExpress](   )`.
  - Đã sửa dòng `items = items or []` thành bước chuẩn hóa: lọc bỏ `None` và bọc mọi phần tử không phải dict thành `{"title": str(item)}` trước khi render.
  - Trong `_src`, `url` được ép về chuỗi và `strip()` trước khi dùng, nên khi thiếu `url` (`None`, `""` hoặc chỉ có khoảng trắng) sẽ không sinh link rỗng mà chỉ hiện tên nguồn.
- **Biên soạn [`TEAM.md`](../../TEAM.md) và [`report/team/group_report.md`](group_report.md):**
  - Tổng hợp đầy đủ Phần A (mô tả agent, bảng 14 tool, câu hỏi mẫu, hướng dẫn chạy UI) và Phần B (bảng B1 Version Evidence `v0`→`v3`, B2 Failure Analysis 8 case lỗi của `v0`, B3 10 case Eval nhóm, B4 5 lượt Live Chat, B5a/B5 Required & Bonus Evidence, và B6 Reflection).

## 4. Bằng chứng

- **File phụ trách & commit:**
  - Commit kỹ thuật `fix(tools): harden send confirmation and format item/url handling`:
    - [`starter_v0/tools/send/tool.py`](../../starter_v0/tools/send/tool.py): `if not confirmed:` → `if confirmed is not True:`
    - [`starter_v0/tools/format/tool.py`](../../starter_v0/tools/format/tool.py): `items = items or []` → bỏ `None`, bọc phần tử không phải dict thành `{"title": str(item)}`; `_src`: `url` được `strip()` để không sinh link rỗng khi thiếu `url`
  - Commit tài liệu `docs(report): fill TEAM.md, group report and personal report`:
    - [`TEAM.md`](../../TEAM.md), [`report/team/group_report.md`](group_report.md)
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng trợ lý AI hỗ trợ định dạng bảng Markdown trong `group_report.md` và rà soát các trường hợp biên (edge cases) của hàm `send_telegram` và `render_digest`.
  - **Cách tự kiểm tra:** Chạy `pytest tests/test_tools_todo.py -k "send or format"` để kiểm chứng các test `test_send_with_string_false_does_not_send`, `test_format_accepts_plain_string_and_null_items` và `test_format_item_without_url_has_no_empty_link` đều PASS; đối chiếu mọi số liệu trong `group_report.md` với các file `runs/*.json` và `version_log.csv`.

## 5. Tự đánh giá

- Hoàn thành tốt vai trò Trưởng nhóm và phần việc kỹ thuật (~15% khối lượng nhóm). Hiểu rõ lý do vì sao guardrail cho hành động có tác dụng phụ (`send`) cần được bảo vệ ở cả 2 lớp: lớp prompt/tool declaration (`clarify(response_type="yes_no")`) và lớp code Python (`confirmed is True`).
