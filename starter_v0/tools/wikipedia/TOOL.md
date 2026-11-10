---
name: wikipedia
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [title, lang]
outputs: [items]
side_effect: false
---
# wikipedia

Lấy phần tóm tắt mở đầu của một bài viết bách khoa toàn thư Wikipedia theo tên chủ đề (`/api/rest_v1/page/summary/<title>`), dùng cho các câu hỏi kiến thức nền tảng, định nghĩa khái niệm hoặc tiểu sử ("X là gì?", "Y là ai?").

- `lang`: `en` (mặc định) hoặc `vi` (tiếng Việt); các giá trị ngoài danh sách tự động đưa về `en`.
- `title` rỗng sẽ trả về dict báo lỗi ngay mà **không** gọi mạng.
- Khi trang không tồn tại (HTTP 404), hàm trả về dict báo lỗi (`HTTPError`), không làm dừng chương trình.
- Không dùng cho tin tức thời sự nóng (dùng `lookup`) hoặc câu hỏi về chính bản thân Agent.
