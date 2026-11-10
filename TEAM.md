# Team — Panda

## Thông tin nhóm

- Tên nhóm: **Panda**
- Lớp: **L3B**
- Repo nhóm: `K5-L3B-DAY03-Panda-ResearchAgentToolEval`
- URL repo: https://github.com/khanhvnm/K5-L3B-DAY03-Panda-ResearchAgentToolEval
- Nhánh nộp: `main`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò | Tỷ trọng đóng góp |
| --: | ------ | ---- | ----- | ------ | ------- | :---------------: |
|   1 | Vũ Nam Khánh | 2A202604112 | - | `khanhvnm` | Thành viên | 15% |
|   2 | Nguyễn Ánh Dương | 2A202604087 | - | `nganhduong123` | Thành viên | 14% |
|   3 | Nguyễn Tuấn Anh | 2A202604089 | - | `TuanAnhNg131` | Thành viên | 15% |
|   4 | Phùng Quang Trà | 2A202604094 | - | `phungtr` | Trưởng nhóm | 15% |
|   5 | Đinh Hoàng Phong | 2A202604090 | - | `Phog2811` | Thành viên (Core Dev) | 27% |
|   6 | Phạm Duy Thành | 2A202604075 | - | `thanhtey1234` | Thành viên | 14% |

## Cá nhân

Báo cáo riêng của từng thành viên trong `report/team/`:

- [`report/team/2A202604090_DinhHoangPhong.md`](report/team/2A202604090_DinhHoangPhong.md)
- [`report/team/2A202604094_PhungQuangTra.md`](report/team/2A202604094_PhungQuangTra.md)
- [`report/team/2A202604112_VuNamKhanh.md`](report/team/2A202604112_VuNamKhanh.md)
- [`report/team/2A202604087_NguyenAnhDuong.md`](report/team/2A202604087_NguyenAnhDuong.md)
- [`report/team/2A202604089_NguyenTuanAnh.md`](report/team/2A202604089_NguyenTuanAnh.md)
- [`report/team/2A202604075_PhamDuyThanh.md`](report/team/2A202604075_PhamDuyThanh.md)

---

## DinhHoangPhong-2A202604090

### Phần việc phụ trách

- Thiết kế và tối ưu vòng lặp `system_prompt.md` + `tools.yaml` qua 4 phiên bản (`v0` → `v1` → `v2` → `v3`).
- Đăng ký hệ thống 14 tool trong `starter_v0/tools/__init__.py` và cấu hình adapter `starter_v0/providers/gemini_provider.py`.
- Chạy đánh giá thực nghiệm Base Eval (`v0`–`v3`) và Extension Eval (`v3`), lưu trữ `version_log.csv` và phân tích `analysis/all_runs.csv`.

### Đóng góp cụ thể

- Loại bỏ toàn bộ chỉ dẫn xấu của starter (`v1`), xây dựng bảng routing, quy ước tham số (`v2`), tách rõ ranh giới xác nhận `clarify(response_type="yes_no")` trước khi gửi Telegram và tích hợp 4 tool mới (`v3`), đưa `case_accuracy` từ `0.60` lên `1.00` (20/20).
- Lưu snapshot đầy đủ tại `starter_v0/artifacts/versions/v0..v3/`.

### Bằng chứng

- `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/artifacts/versions/`
- `starter_v0/tools/__init__.py`, `starter_v0/providers/gemini_provider.py`
- `starter_v0/runs/v0_B_base_*.json` → `starter_v0/runs/v3_B_base_*.json`, `starter_v0/runs/v3_B_extension_*.json`, `starter_v0/analysis/all_runs.csv`

---

## PhungQuangTra-2A202604094

### Phần việc phụ trách

- Trưởng nhóm: điều phối phân công trong `TEAM.md` và biên soạn báo cáo tổng hợp `report/team/group_report.md` (Phần A + Phần B).
- Kiểm toán và vá lỗi guardrail bảo mật cho 2 tool hành động/trình bày: `send` và `format`.

### Đóng góp cụ thể

- Vá lỗi nghiêm trọng trong `starter_v0/tools/send/tool.py`: thay `if not confirmed:` bằng `if confirmed is not True:` để chặn trường hợp model truyền chuỗi `"false"` hoặc `"no"` (truthy trong Python) làm gửi nhầm tin lên Telegram.
- Vá lỗi trong `starter_v0/tools/format/tool.py`: chuẩn hóa phần tử chuỗi/loại bỏ `None` trong `items`, không sinh link rỗng khi thiếu `url`.
- Tổng hợp số liệu thực nghiệm từ `runs/*.json`, `version_log.csv` và `transcripts/` vào `report/team/group_report.md`.

### Bằng chứng

- `TEAM.md`, `report/team/group_report.md`
- `starter_v0/tools/send/tool.py`, `starter_v0/tools/format/tool.py`

---

## VuNamKhanh-2A202604112

### Phần việc phụ trách

- Phát triển 2 tool mới mở rộng nguồn dữ liệu công nghệ: `github_search` và `hackernews` (kèm `TOOL.md` đúng contract).
- Vá lỗi kiểm tra tham số đầu vào (input validation & clamping) cho 2 tool web: `lookup` và `fetch`.

### Đóng góp cụ thể

- Xây dựng `starter_v0/tools/github_search/tool.py` + `TOOL.md` (tìm repo GitHub qua REST API theo `stars`/`updated`, xử lý rate-limit trả error dict).
- Xây dựng `starter_v0/tools/hackernews/tool.py` + `TOOL.md` (tìm bài thảo luận Hacker News qua Algolia API theo `relevance`/`date`).
- Sửa `starter_v0/tools/lookup/tool.py` (chặn `query` rỗng trước khi gọi Tavily tránh tốn credit, lọc `topic`/`timeframe` theo enum hợp lệ, clamp `max_results` trong `1..20`) và `starter_v0/tools/fetch/tool.py` (chỉ cho phép URL `http://` hoặc `https://`).

### Bằng chứng

- `starter_v0/tools/github_search/tool.py`, `starter_v0/tools/github_search/TOOL.md`
- `starter_v0/tools/hackernews/tool.py`, `starter_v0/tools/hackernews/TOOL.md`
- `starter_v0/tools/lookup/tool.py`, `starter_v0/tools/fetch/tool.py`

---

## NguyenAnhDuong-2A202604087

### Phần việc phụ trách

- Phát triển 2 tool mới phục vụ tra cứu kiến thức nền và thời gian thực: `wikipedia` và `current_time` (kèm `TOOL.md` đúng contract).
- Vá lỗi xử lý chuỗi `@handle` và slice âm `limit` cho 2 tool X/Twitter: `timeline` và `social_search`.

### Đóng góp cụ thể

- Xây dựng `starter_v0/tools/wikipedia/tool.py` + `TOOL.md` (gọi Wikipedia REST API đa ngôn ngữ `en`/`vi`, URL-encode tiêu đề an toàn) và `starter_v0/tools/current_time/tool.py` + `TOOL.md` (trả về ngày, giờ, thứ hiện tại theo `utc_offset_hours` hoàn toàn offline).
- Sửa `starter_v0/tools/timeline/tool.py` (tự động `.lstrip("@")` ở `screenname`, chặn handle rỗng không gọi mạng, clamp `limit` trong `1..20` tránh lỗi slice âm `items[:-2]`) và `starter_v0/tools/social_search/tool.py` (kiểm tra `query` rỗng, chuẩn hóa `search_type`, clamp `limit`).

### Bằng chứng

- `starter_v0/tools/wikipedia/tool.py`, `starter_v0/tools/wikipedia/TOOL.md`
- `starter_v0/tools/current_time/tool.py`, `starter_v0/tools/current_time/TOOL.md`
- `starter_v0/tools/timeline/tool.py`, `starter_v0/tools/social_search/tool.py`

---

## NguyenTuanAnh-2A202604089

### Phần việc phụ trách

- Thiết kế bộ 10 case đánh giá của nhóm trong `starter_v0/data/eval_group.json` (5 single-turn + 5 multi-turn) và chạy đánh giá `--suite group`.
- Hoàn thiện toàn bộ Unit Test Suite trong `starter_v0/tests/test_tools_todo.py` và fixture kiểm thử `starter_v0/tests/conftest.py`.

### Đóng góp cụ thể

- Viết 10 case `G01`–`G05` và `GM01`–`GM05` kiểm tra routing tới 4 tool mới, chuyển nguồn dữ liệu qua nhiều lượt, gom tham số nhiều lượt và ranh giới xác nhận `send(confirmed=true)` (đạt `10/10 PASS`).
- Điền đầy đủ 14 stub TODO của các tool có sẵn, viết 12 regression test cho 6 bug phát hiện được và 19 unit test cho 4 tool mới → toàn bộ `pytest` đạt **139 passed, 0 failed, 0 skipped**.

### Bằng chứng

- `starter_v0/data/eval_group.json`, `starter_v0/runs/v3_B_group_gemini_20261110T153621028288.json`
- `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/conftest.py`

---

## PhamDuyThanh-2A202604075

### Phần việc phụ trách

- Xây dựng giao diện người dùng Streamlit (`starter_v0/app.py`), trang poster giới thiệu (`report/team/poster.html`) và các script tiện ích triển khai Cloudflare Tunnel (`starter_v0/scripts/`).
- Thực hiện các phiên chạy Live Chat đa lượt và thu thập bằng chứng `starter_v0/transcripts/*.transcript.json`.

### Đóng góp cụ thể

- Phát triển `starter_v0/app.py` dùng chung vòng lặp `run_model_tool_loop` với `chat.py`, hỗ trợ chọn phiên bản artifact `v0`–`v3`, hiển thị trực quan từng bước gọi tool và tự động lưu transcript.
- Viết `starter_v0/scripts/serve_tunnel.py`, `starter_v0/scripts/run_all.py`, `starter_v0/scripts/log_version.py`, cập nhật `starter_v0/requirements.txt` và thiết kế `report/team/poster.html`.
- Chạy và ghi nhận các phiên hội thoại thực tế trong `starter_v0/transcripts/`.

### Bằng chứng

- `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/.env.example`, `starter_v0/env_loader.py`
- `starter_v0/scripts/serve_tunnel.py`, `starter_v0/scripts/run_all.py`, `starter_v0/scripts/log_version.py`
- `starter_v0/transcripts/*.transcript.json`, `report/team/poster.html`
