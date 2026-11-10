# Báo cáo cá nhân — NguyenTuanAnh-2A202604089

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tuấn Anh
- MSSV: `2A202604089`
- Email: -
- GitHub: `TuanAnhNg131`
- Nhóm: **Panda** (`K5-L3B-DAY03-Panda-ResearchAgentToolEval`)

## 2. Phần việc phụ trách

- Thiết kế bộ 10 case đánh giá của nhóm trong [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json) (5 single-turn + 5 multi-turn) và chạy kiểm chứng tạo file bằng chứng [`starter_v0/runs/v3_B_group_gemini_20261110T153621028288.json`](../../starter_v0/runs/v3_B_group_gemini_20261110T153621028288.json).
- Hoàn thiện toàn bộ bộ Unit Test & Regression Test trong [`starter_v0/tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py) cùng cấu hình fixture [`starter_v0/tests/conftest.py`](../../starter_v0/tests/conftest.py) để đạt mục tiêu Challenge: **0 failed, 0 skipped** trên toàn bộ suite.

## 3. Đóng góp cụ thể

- **Thiết kế 10 case trong `starter_v0/data/eval_group.json` (đạt 10/10 PASS ở `v3`):**
  - **5 Single-turn (`G01`–`G05`):** Kiểm tra định tuyến chính xác tới cả 4 tool mới của nhóm (`G01_github_routing` với `sort="stars"`, `G02_hackernews_routing`, `G03_current_time_routing`, `G04_wikipedia_routing` với `title="Alan Turing"`) và 1 case kiểm tra từ chối câu hỏi dịch thuật ngoài phạm vi (`G05_out_of_scope_translation` → `no_tool: true`).
  - **5 Multi-turn (`GM01`–`GM05`):** Kiểm tra hội thoại 3 lượt phức tạp: không gọi lại tool của lượt đầu khi lượt cuối hỏi câu meta sau lời cảm ơn (`GM01`), gom tham số `sort="updated"` và `limit=3` qua 3 lượt cho `github_search` (`GM02`), hỏi lại handle bị thiếu rồi ánh xạ `"Yann LeCun"` → `"ylecun"` kèm `limit=4` (`GM03`), gọi `send(confirmed=true)` ngay sau khi người dùng xác nhận ở lượt 3 (`GM04`), và chuyển nguồn từ Twitter sang Hacker News trong khi giữ nguyên chủ đề `"Claude"` (`GM05`).
- **Hoàn thiện Unit Test Suite trong `starter_v0/tests/test_tools_todo.py` & `conftest.py`:**
  - Cập nhật `ENV_KEYS` trong `conftest.py` (thêm `GITHUB_TOKEN`) để môi trường test hoàn toàn cô lập và offline.
  - Điền đầy đủ 14 test stub có sẵn của starter (cho `clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`).
  - Viết thêm 12 regression test bắt 6 lỗi biên trong các tool có sẵn (`confirmed="false"`, `limit=-2`, `query=""`, `timeframe="today"`, `url="ftp://..."`, `items=["str", None]`, `screenname="@sama"`).
  - Viết 19 unit test (happy path, bad input, network/HTTP error) cho 4 tool mới (`hackernews`, `github_search`, `wikipedia`, `current_time`).
  - Kết quả chạy `pytest`: **`139 passed, 0 failed, 0 skipped`** trong `0.44s`.

## 4. Bằng chứng

- **File phụ trách & commit:**
  - [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json)
  - [`starter_v0/runs/v3_B_group_gemini_20261110T153621028288.json`](../../starter_v0/runs/v3_B_group_gemini_20261110T153621028288.json)
  - [`starter_v0/tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py)
  - [`starter_v0/tests/conftest.py`](../../starter_v0/tests/conftest.py)
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng trợ lý AI để gợi ý các mẫu dữ liệu mock HTTP response cho `fake_http` và kiểm tra schema JSON của `eval_group.json`.
  - **Cách tự kiểm tra:** Chạy `pytest -v` (kiểm tra 139 test xanh, 0 skipped) và chạy `python run_eval.py --provider gemini --version v3 --suite group --eval-cases data/eval_group.json` để xác nhận cả 10 case trong `eval_group.json` đều chạy mượt và đạt `case_accuracy = 1.0`.

## 5. Tự đánh giá

- Hoàn thành xuất sắc phần việc kiểm thử và đánh giá (~15% khối lượng nhóm), giúp nhóm đạt cả điểm chính (C4, C5) lẫn điểm Bonus Test Challenge. Phân biệt rõ vai trò của **Eval** (đo khả năng chọn tool và truyền tham số của LLM) và **Unit Test** (đo tính đúng đắn và an toàn của code Python bên trong mỗi tool).
