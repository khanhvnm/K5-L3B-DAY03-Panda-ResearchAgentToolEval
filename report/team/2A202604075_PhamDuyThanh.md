# Báo cáo cá nhân — PhamDuyThanh-2A202604075

## 1. Thông tin thành viên

- Họ tên: Phạm Duy Thành
- MSSV: `2A202604075`
- Email: -
- GitHub: `thanhtey1234`
- Nhóm: **Panda** (`K5-L3B-DAY03-Panda-ResearchAgentToolEval`)

## 2. Phần việc phụ trách

- Xây dựng giao diện người dùng bằng Streamlit ([`starter_v0/app.py`](../../starter_v0/app.py)), cập nhật [`starter_v0/requirements.txt`](../../starter_v0/requirements.txt), [`starter_v0/.env.example`](../../starter_v0/.env.example), [`starter_v0/env_loader.py`](../../starter_v0/env_loader.py) và thiết kế trang poster giới thiệu [`report/team/poster.html`](poster.html).
- Viết bộ script tự động hóa và mở Cloudflare Tunnel trong `starter_v0/scripts/` (`serve_tunnel.py`, `run_all.py`, `log_version.py`).
- Thực hiện các phiên hội thoại Live Chat nhiều lượt và ghi nhận bằng chứng trong `starter_v0/transcripts/*.transcript.json`.

## 3. Đóng góp cụ thể

- **Phát triển giao diện Streamlit (`starter_v0/app.py`):**
  - Tái sử dụng trực tiếp hàm `run_model_tool_loop` từ `chat.py` để đảm bảo hành vi trên UI giống hệt CLI.
  - Cho phép người dùng chọn provider (`gemini`, `openrouter`, `openai`, `anthropic`, `ollama`), chọn phiên bản artifact (`v0`, `v1`, `v2`, `v3`) để so sánh trực tiếp trước/sau khi tối ưu, cung cấp các nút bấm câu hỏi mẫu 1-click, hiển thị chi tiết từng lệnh gọi tool (`tool_calls`) cùng kết quả JSON trả về, và tự động lưu mọi lượt hội thoại vào `starter_v0/transcripts/ui_*.transcript.json`.
- **Xây dựng các script hỗ trợ (`starter_v0/scripts/`) và Poster (`report/team/poster.html`):**
  - `serve_tunnel.py`: Tự động khởi chạy Streamlit ở cổng `8501` kèm `cloudflared tunnel` và trích xuất URL public `https://*.trycloudflare.com` để các nhóm khác dùng thử ngay.
  - `log_version.py` & `run_all.py`: Hỗ trợ tự động đọc hash/metric từ file run JSON để ghi vào `version_log.csv` và xuất `analysis/all_runs.csv`.
  - Thiết kế `report/team/poster.html` trình bày trực quan 14 tool, câu hỏi mẫu và 3 lớp guardrail của nhóm Panda.
- **Thực hiện Live Chat & thu thập Transcript (`starter_v0/transcripts/`):**
  - Chạy phiên hội thoại 5 lượt liên tiếp [`v3_gemini_20261110T153848310732.transcript.json`](../../starter_v0/transcripts/v3_gemini_20261110T153848310732.transcript.json) và các phiên thử nghiệm trên giao diện `ui_*.transcript.json`, bao phủ đầy đủ các kịch bản: tra cứu repo GitHub thật, phát hiện thiếu URL để hỏi lại (`clarify`), tra cứu Wikipedia tiếng Việt, chặn yêu cầu đăng Telegram để hỏi xác nhận `yes_no`, và thực thi `send(confirmed=true)` sau khi người dùng đồng ý.

## 4. Bằng chứng

- **File phụ trách & commit:**
  - [`starter_v0/app.py`](../../starter_v0/app.py)
  - [`starter_v0/requirements.txt`](../../starter_v0/requirements.txt), [`starter_v0/.env.example`](../../starter_v0/.env.example), [`starter_v0/env_loader.py`](../../starter_v0/env_loader.py)
  - [`starter_v0/scripts/serve_tunnel.py`](../../starter_v0/scripts/serve_tunnel.py), [`starter_v0/scripts/run_all.py`](../../starter_v0/scripts/run_all.py), [`starter_v0/scripts/log_version.py`](../../starter_v0/scripts/log_version.py)
  - `starter_v0/transcripts/*.transcript.json` (7 file transcript)
  - [`report/team/poster.html`](poster.html)
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng trợ lý AI để hỗ trợ viết bố cục CSS cho `poster.html` và xử lý `st.session_state` trong Streamlit `app.py`.
  - **Cách tự kiểm tra:** Dùng `streamlit.testing.v1.AppTest` và mở trực tiếp `http://localhost:8501` cùng link Cloudflare Tunnel để thử nghiệm các câu hỏi mẫu; kiểm tra cấu trúc JSON của các file trong `starter_v0/transcripts/` đảm bảo lưu đầy đủ `tool_calls`, `tool_results` và `artifact_version`.

## 5. Tự đánh giá

- Hoàn thành tốt toàn bộ phần việc giao diện, triển khai dùng thử và kiểm thử hội thoại sống (~14% khối lượng nhóm), đáp ứng đầy đủ tiêu chí C6 trong Rubric.
