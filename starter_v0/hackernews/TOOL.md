---
name: hackernews
track: bonus
kind: live_api
provider: Hacker News (Algolia HN Search API)
requires_env: []
inputs: [query, sort_by, limit]
outputs: [items]
side_effect: false
---
# hackernews

Tìm kiếm các bài viết và thảo luận công nghệ trên Hacker News (sử dụng Algolia HN Search API miễn phí, không cần khóa API). Mỗi kết quả trả về gồm `title`, `url` (đường dẫn bài viết gốc hoặc trang thảo luận HN), `discussion_url`, `summary` (điểm số/số bình luận/tác giả) và `date`.

- `sort_by=relevance` (mặc định: độ liên quan/nổi bật) hoặc `date` (mới nhất).
- `limit` được giới hạn an toàn trong khoảng `1..20`; giá trị không hợp lệ tự động đưa về `5`.
- Từ khóa `query` rỗng sẽ trả về dict báo lỗi ngay mà **không** gọi mạng.
- Chỉ sử dụng khi người dùng nhắc trực tiếp tới Hacker News / HN / `news.ycombinator.com`.
