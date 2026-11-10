---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# github_search

Tìm kiếm các kho mã nguồn mở công khai trên GitHub (`/search/repositories`). Hoạt động trực tiếp không cần khóa API (có thể đặt thêm biến môi trường tùy chọn `GITHUB_TOKEN` để nâng giới hạn tần suất gọi).

- `sort=stars` (mặc định: sắp xếp theo số sao giảm dần) hoặc `updated` (mới cập nhật gần đây).
- `limit` được giới hạn trong khoảng `1..20`; giá trị không hợp lệ tự động đưa về `5`.
- Từ khóa `query` rỗng sẽ trả về dict báo lỗi ngay mà **không** gọi mạng.
- Chỉ sử dụng khi người dùng hỏi tìm repo GitHub / dự án mã nguồn mở / thư viện code.
