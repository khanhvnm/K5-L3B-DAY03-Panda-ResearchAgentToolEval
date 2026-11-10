# Báo cáo cá nhân — VuNamKhanh-2A202604112

## 1. Thông tin thành viên

- Họ tên: Vũ Nam Khánh
- MSSV: `2A202604112`
- Email: -
- GitHub: `khanhvnm`
- Nhóm: **Panda** (`K5-L3B-DAY03-Panda-ResearchAgentToolEval`)

## 2. Phần việc phụ trách

- Thiết kế và hiện thực hóa 2 tool mới mở rộng nguồn tra cứu cho agent: `github_search` và `hackernews` (bao gồm cả `tool.py` và `TOOL.md` theo đúng chuẩn contract trong `starter_v0/tools/README.md`).
- Rà soát và vá lỗi kiểm tra tham số đầu vào (input validation & clamping) cho 2 tool tìm kiếm/đọc web có sẵn: `lookup` (`starter_v0/tools/lookup/tool.py`) và `fetch` (`starter_v0/tools/fetch/tool.py`).

## 3. Đóng góp cụ thể

- **Xây dựng tool mới `github_search` (`starter_v0/tools/github_search/`):**
  - Gọi GitHub REST API (`https://api.github.com/search/repositories`) tìm kiếm repository mã nguồn mở theo `query`, hỗ trợ sắp xếp theo `stars` hoặc `updated` và giới hạn `limit` (`1..20`).
  - Hỗ trợ tùy chọn `GITHUB_TOKEN` nếu có trong môi trường, tự động chuẩn hóa mô tả `None` thành chuỗi rỗng, và bắt mọi lỗi HTTP (như `403 rate limit`) để trả về error dict chuẩn thay vì raise exception.
- **Xây dựng tool mới `hackernews` (`starter_v0/tools/hackernews/`):**
  - Gọi Algolia Hacker News API (`hn.algolia.com/api/v1/search` cho `sort_by="relevance"` và `search_by_date` cho `sort_by="date"`), không cần API key.
  - Lọc bỏ các hit thiếu `title` hoặc `objectID`, tự động tạo fallback URL về `news.ycombinator.com/item?id=...` khi bài thảo luận không có link ngoài.
- **Vá lỗi trong `starter_v0/tools/lookup/tool.py` (Bug #3) và `starter_v0/tools/fetch/tool.py` (Bug #4):**
  - Trong `lookup`: chặn `query` rỗng hoặc sai kiểu trước khi gọi Tavily API để không làm tốn credit vô ích; lọc `topic` theo `{"general", "news"}` và `timeframe` theo `{"day", "week", "month", "year"}` (bỏ qua giá trị ngoài enum như `"today"` để tránh lỗi HTTP 400 từ Tavily); clamp `max_results` trong khoảng `1..20` và hỗ trợ ép kiểu khi model truyền số dạng chuỗi `"5"`.
  - Trong `fetch`: kiểm tra chặt `url` phải bắt đầu bằng `http://` hoặc `https://` trước khi gửi POST request tới Firecrawl.

## 4. Bằng chứng

- **File phụ trách & commit:**
  - [`starter_v0/tools/github_search/tool.py`](../../starter_v0/tools/github_search/tool.py) & [`starter_v0/tools/github_search/TOOL.md`](../../starter_v0/tools/github_search/TOOL.md)
  - [`starter_v0/tools/hackernews/tool.py`](../../starter_v0/tools/hackernews/tool.py) & [`starter_v0/tools/hackernews/TOOL.md`](../../starter_v0/tools/hackernews/TOOL.md)
  - [`starter_v0/tools/lookup/tool.py`](../../starter_v0/tools/lookup/tool.py)
  - [`starter_v0/tools/fetch/tool.py`](../../starter_v0/tools/fetch/tool.py)
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng trợ lý AI để tra cứu cấu trúc JSON trả về của Algolia HN API và GitHub Search API, cũng như viết docstring/frontmatter `TOOL.md`.
  - **Cách tự kiểm tra:** Chạy `pytest tests/test_tool_contract.py` để xác nhận chữ ký hàm và frontmatter `TOOL.md` hợp lệ; chạy `pytest tests/test_tools_todo.py -k "github_search or hackernews or lookup or fetch"` đảm bảo tất cả unit test (happy path, input rỗng/sai kiểu, lỗi HTTP 403/500) đều PASS mà không gọi mạng thật.

## 5. Tự đánh giá

- Hoàn thành đầy đủ 100% nhiệm vụ được giao (~15% khối lượng nhóm). Hiểu rõ nguyên tắc thiết kế tool cho LLM: không bao giờ tin tưởng tuyệt đối vào kiểu dữ liệu hoặc khoảng giá trị mà model sinh ra, luôn validate & clamp trước khi gọi API bên ngoài và trả về error dict có cấu trúc để agent xử lý tiếp.
