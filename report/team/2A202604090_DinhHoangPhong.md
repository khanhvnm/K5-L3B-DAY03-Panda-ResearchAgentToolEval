# Báo cáo cá nhân — DinhHoangPhong-2A202604090

## 1. Thông tin thành viên

- Họ tên: Đinh Hoàng Phong
- MSSV: `2A202604090`
- Email: phong28112004fpt@gmail.com
- GitHub: `Phog2811`
- Nhóm: **Panda** (`K5-L3B-DAY03-Panda-ResearchAgentToolEval`)

## 2. Phần việc phụ trách

- Phụ trách chính vòng lặp tối ưu `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml` qua 4 phiên bản (`v0` → `v1` → `v2` → `v3`).
- Đăng ký toàn bộ 14 tool (10 tool gốc + 4 tool mới của nhóm) trong `starter_v0/tools/__init__.py` và đồng bộ schema sang chuẩn OpenAI function calling.
- Cải tiến `starter_v0/providers/gemini_provider.py` để xử lý retry/fallback khi gặp giới hạn rate-limit tạm thời (`429`/`503`) nhằm đảm bảo mọi run có `provider_error_cases == 0`.
- Thực thi bộ đánh giá Base Eval (`v0`–`v3`) và Extension Eval (`v3`), lưu trữ `starter_v0/artifacts/version_log.csv`, snapshot `starter_v0/artifacts/versions/v0..v3/` và bảng phân tích `starter_v0/analysis/all_runs.csv`.

## 3. Đóng góp cụ thể

- **Phiên bản `v0` (Baseline):** Chạy bộ `data/eval_base.json` trên prompt và tool declaration nguyên bản của starter, đạt `case_accuracy = 0.60` (12/20). Phân tích toàn bộ 8 case FAIL và phân nhóm nguyên nhân: chỉ dẫn xấu cố ý trong prompt (ép gọi 1 tool, tự đoán handle/URL, gửi Telegram không xin phép) và mô tả tool/args mơ hồ.
- **Phiên bản `v1` (`system_prompt.md`):** Giả thuyết rằng loại bỏ chỉ dẫn xấu và thêm quy tắc `clarify` khi thiếu thông tin + từ chối câu ngoài phạm vi sẽ giải quyết các lỗi `missing_info`, `out_of_scope`, `unnecessary_tool`. Kết quả: `R08`, `R09`, `R10`, `R11` chuyển từ FAIL sang PASS; `tool_routing_accuracy` tăng từ `0.70` lên `0.90`, `case_accuracy` tăng lên `0.65` (13/20).
- **Phiên bản `v2` (`tools.yaml`):** Giả thuyết rằng viết lại `description` từng tool theo cấu trúc `USE WHEN / DO NOT USE WHEN` kèm quy ước tham số chặt chẽ (`screenname` không `@`, `query` chỉ lấy từ khóa gốc không tự mở rộng, `topic=news`, `timeframe`, `search_type=Top|Latest`) sẽ sửa `wrong_tool` và `wrong_arg_value`. Kết quả: `case_accuracy` tăng vọt từ `0.65` lên **`0.95` (19/20)**, `multiturn_accuracy` đạt `1.00`.
- **Phiên bản `v3` (`system_prompt.md` + `tools.yaml`):** Tách rõ quy tắc bắt buộc gọi `clarify(response_type="yes_no")` cho mọi yêu cầu gửi/đăng Telegram (kể cả khi user mới nói `"bản tin này"`), bổ sung bảng routing và khai báo 4 tool mới (`hackernews`, `github_search`, `wikipedia`, `current_time`). Kết quả: `R12_confirm_before_send` PASS; đạt **`1.00` (20/20)** trên Base Eval và **`1.00` (10/10)** trên Extension Eval.

## 4. Bằng chứng

- **File phụ trách & commit:**
  - [`starter_v0/artifacts/system_prompt.md`](../../starter_v0/artifacts/system_prompt.md)
  - [`starter_v0/artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml)
  - [`starter_v0/artifacts/version_log.csv`](../../starter_v0/artifacts/version_log.csv)
  - `starter_v0/artifacts/versions/` (`README.md`, `v0/`, `v1/`, `v2/`, `v3/`)
  - [`starter_v0/tools/__init__.py`](../../starter_v0/tools/__init__.py)
  - [`starter_v0/providers/gemini_provider.py`](../../starter_v0/providers/gemini_provider.py)
  - `starter_v0/runs/v0_B_base_gemini_20261110T150231415716.json`
  - `starter_v0/runs/v1_B_base_gemini_20261110T152357017662.json`
  - `starter_v0/runs/v2_B_base_gemini_20261110T152457433892.json`
  - `starter_v0/runs/v3_B_base_gemini_20261110T153554881404.json`
  - `starter_v0/runs/v3_B_extension_gemini_20261110T153651074202.json`
  - [`starter_v0/analysis/all_runs.csv`](../../starter_v0/analysis/all_runs.csv)
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng Gemini / Antigravity hỗ trợ rà soát wording tiếng Anh trong `system_prompt.md` và `tools.yaml`, và tổng hợp bảng phân tích log từ `runs/*.json`.
  - **Cách tự kiểm tra:** Chạy trực tiếp `pytest tests/test_tool_contract.py` để đảm bảo đồng bộ giữa `tools.yaml` và `tools/__init__.py`; kiểm tra từng file `runs/v0..v3_*.json` đảm bảo `provider_error_cases == 0`, `measured_cases == total_cases`, và đối chiếu mã băm `prompt_hash` / `tools_hash` khớp 100% với `version_log.csv`.

## 5. Tự đánh giá

- Hoàn thành đầy đủ nhiệm vụ cốt lõi và đóng góp ~27% tổng khối lượng dự án nhóm. Nắm vững sự khác biệt giữa lỗi hành vi ở tầng `system_prompt.md` (boundary, scope, multi-turn) và lỗi định tuyến/tham số ở tầng `tools.yaml` (`USE WHEN / DO NOT USE WHEN`, quy ước kiểu dữ liệu và giá trị enum).
