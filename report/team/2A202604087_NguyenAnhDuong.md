# Báo cáo cá nhân — NguyenAnhDuong-2A202604087

## 1. Thông tin thành viên

- Họ tên: Nguyễn Ánh Dương
- MSSV: `2A202604087`
- Email: -
- GitHub: `nganhduong123`
- Nhóm: **Panda** (`K5-L3B-DAY03-Panda-ResearchAgentToolEval`)

## 2. Phần việc phụ trách

- Phát triển 2 tool mới cho agent: `wikipedia` (tra cứu tóm tắt bách khoa toàn thư đa ngôn ngữ) và `current_time` (xem ngày, giờ, thứ hiện tại theo múi giờ) kèm tài liệu `TOOL.md` đúng contract.
- Kiểm tra và vá lỗi xử lý tham số biên cho 2 tool mạng xã hội X/Twitter: `timeline` (`starter_v0/tools/timeline/tool.py`) và `social_search` (`starter_v0/tools/social_search/tool.py`).

## 3. Đóng góp cụ thể

- **Xây dựng tool mới `wikipedia` (`starter_v0/tools/wikipedia/`):**
  - Gọi Wikimedia REST API (`/api/rest_v1/page/summary/{title}`), hỗ trợ ngôn ngữ `en` và `vi` (mặc định fallback về `en` nếu model truyền mã ngôn ngữ ngoài enum).
  - Sử dụng `urllib.parse.quote` để mã hóa an toàn các tiêu đề có dấu cách hoặc ký tự đặc biệt (như `"C++"` hay `"Alan Turing"`), xử lý lỗi HTTP 404 (trang không tồn tại) và lỗi mạng thành error dict chuẩn.
- **Xây dựng tool mới `current_time` (`starter_v0/tools/current_time/`):**
  - Tính toán ngày (`date`), giờ (`time`), thứ tiếng Anh/tiếng Việt (`weekday`, `weekday_vi`) và chuỗi `iso` dựa trên `utc_offset_hours` (mặc định `+7` cho giờ Việt Nam), hoạt động hoàn toàn offline không tốn quota mạng.
  - Kiểm tra biên `utc_offset_hours` trong khoảng `-12..14`; nếu model truyền chuỗi không ép kiểu được thì fallback về `7`, nếu ngoài khoảng `-12..14` thì trả về error dict.
- **Vá lỗi trong `starter_v0/tools/timeline/tool.py` và `starter_v0/tools/social_search/tool.py` (Bug #2 & Bug #6):**
  - Trong `timeline`: tự động `.strip().lstrip("@")` cho `screenname` (phòng trường hợp model truyền `"@sama"`) và trả về error dict ngay nếu handle rỗng mà không gọi RapidAPI.
  - Trong cả `timeline` và `social_search`: sửa lỗi cắt mảng `[:limit]` khi `limit <= 0` (trước đây `limit=-2` làm Python cắt `items[:-2]` trả về 4 phần tử đầu thay vì báo lỗi/clamp). Đã viết hàm `_clamp_limit` giới hạn `limit` an toàn trong khoảng `1..20`.

## 4. Bằng chứng

- **File phụ trách & commit:**
  - [`starter_v0/tools/wikipedia/tool.py`](../../starter_v0/tools/wikipedia/tool.py) & [`starter_v0/tools/wikipedia/TOOL.md`](../../starter_v0/tools/wikipedia/TOOL.md)
  - [`starter_v0/tools/current_time/tool.py`](../../starter_v0/tools/current_time/tool.py) & [`starter_v0/tools/current_time/TOOL.md`](../../starter_v0/tools/current_time/TOOL.md)
  - [`starter_v0/tools/timeline/tool.py`](../../starter_v0/tools/timeline/tool.py)
  - [`starter_v0/tools/social_search/tool.py`](../../starter_v0/tools/social_search/tool.py)
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng trợ lý AI để tham khảo endpoint REST v1 của Wikipedia và cách xử lý múi giờ `datetime.timezone` trong Python chuẩn.
  - **Cách tự kiểm tra:** Chạy `pytest tests/test_tool_contract.py` và `pytest tests/test_tools_todo.py -k "wikipedia or current_time or timeline or social_search"`. Tất cả các test (bao gồm `test_timeline_non_positive_limit_never_returns_slice_from_end` và `test_timeline_strips_at_sign_from_handle`) đều PASS.

## 5. Tự đánh giá

- Hoàn thành tốt toàn bộ phần việc được phân công (~14% khối lượng nhóm). Nhận thức rõ tầm quan trọng của việc chuẩn hóa tham số đầu vào (như bỏ ký tự `@` và clamp `limit`) để hệ thống hoạt động bền vững ngay cả khi LLM sinh đối số hơi lệch chuẩn.
