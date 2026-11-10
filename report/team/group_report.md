# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì. Poster HTML tương ứng: [`poster.html`](poster.html).
> - **Phần B (mục 3–8)** — chi tiết và bằng chứng, dựa trên log thật (`starter_v0/artifacts/version_log.csv`, `starter_v0/runs/*.json`, `starter_v0/analysis/all_runs.csv`, `starter_v0/transcripts/*.transcript.json`).

## 1. Thông tin nhóm

- Tên nhóm: **Panda** (`K5-L3B-DAY03-Panda-ResearchAgentToolEval`)
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
  1. Vũ Nam Khánh (`2A202604112` — `khanhvnm`)
  2. Nguyễn Ánh Dương (`2A202604087` — `nganhduong123`)
  3. Nguyễn Tuấn Anh (`2A202604089` — `TuanAnhNg131`)
  4. Phùng Quang Trà (`2A202604094` — `phungtr` — Trưởng nhóm)
  5. Đinh Hoàng Phong (`2A202604090` — `Phog2811`)
  6. Phạm Duy Thành (`2A202604075` — `thanhtey1234`)
- Provider/model dùng cho v0–v3: `gemini` (`gemini-3.5-flash` / `gemini-3.5-flash-lite`) & hỗ trợ tương thích `openrouter`

---

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin trên web theo chủ đề/khung thời gian, lấy bài đăng X/Twitter (theo tài khoản hoặc theo từ khóa), đọc và tóm tắt một URL, tìm/đọc paper arXiv, tra policy nội bộ, tra GitHub / Hacker News / Wikipedia, trả lời ngày giờ, trình bày thành digest, và gửi lên Telegram **chỉ sau khi người dùng xác nhận**. Khi thiếu thông tin (không rõ tài khoản, không có URL) agent chủ động hỏi lại thay vì đoán; với câu hỏi ngoài phạm vi (toán, code, dịch thuật) agent lịch sự từ chối và không gọi tool.

**Cách chạy UI:**

```bash
cd starter_v0
streamlit run app.py
# Hoặc chạy kèm Cloudflare Tunnel tự động:
python scripts/serve_tunnel.py
```

Dependency UI đã thêm vào [`starter_v0/requirements.txt`](../../starter_v0/requirements.txt): `streamlit>=1.30.0`.

**Link dùng thử (deploy):**

- URL (Cloudflare Tunnel): https://pot-this-matched-adjustment.trycloudflare.com (Local: `http://localhost:8501`)

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin (`text`/`choice`) hoặc xin xác nhận `yes_no` trước khi gửi | không |
| `timeline` | Lấy bài đăng gần đây của MỘT tài khoản X/Twitter (handle không `@`) | không |
| `social_search` | Tìm bài đăng X/Twitter theo từ khóa (`Latest` / `Top`) | không |
| `lookup` | Tìm kiếm web / tin tức qua Tavily (`topic=news|general`, `timeframe=day|week|month|year`) | không |
| `fetch` | Đọc nội dung toàn văn một URL cụ thể qua Firecrawl | không |
| `format` | Trình bày danh sách item đã có thành bản tin markdown digest | không |
| `send` | Gửi nội dung lên kênh Telegram, chỉ thực thi khi `confirmed=true` | không |
| `policy` | Tìm kiếm quy định trong company policy nội bộ (local markdown) | không |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv theo chủ đề | không |
| `paper_text` | Tải PDF arXiv và trích xuất văn bản cục bộ | không |
| **`hackernews`** | Tìm bài viết và thảo luận trên Hacker News qua Algolia API (không cần key) | **có** |
| **`github_search`** | Tìm repository mã nguồn mở trên GitHub theo số sao (`stars`) hoặc mới cập nhật (`updated`) | **có** |
| **`wikipedia`** | Lấy tóm tắt bài viết Wikipedia (`en`/`vi`) cho định nghĩa và kiến thức nền | **có** |
| **`current_time`** | Xem ngày, giờ, thứ hiện tại theo múi giờ (hoạt động offline) | **có** |

### A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?` → `lookup(query="AI", topic="news", timeframe="day")`
2. `Lấy 5 tweet mới nhất của Sam Altman` → `timeline(screenname="sama", limit=5)`
3. `Tóm tắt 5 tweet mới nhất giúp mình` → agent **hỏi lại** tài khoản nào (`clarify(response_type="text")`)
4. `Đăng bản tin này lên Telegram giúp mình` → agent **xin xác nhận** trước (`clarify(response_type="yes_no")`), không tự gửi
5. `Có repo GitHub nào hay về RAG không? Cho mình vài repo nhiều sao nhất.` → `github_search(query="RAG", sort="stars")`
6. `Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?` → từ chối lịch sự, không gọi tool

---

## 3. Giải pháp

- **Cải tiến `starter_v0/artifacts/system_prompt.md`:**
  - Loại bỏ hoàn toàn các chỉ dẫn xấu cố ý trong bản starter (ép gọi đúng 1 tool, tự chọn tài khoản nổi tiếng khi thiếu handle, tự đoán URL khi thiếu link, tự gửi Telegram không cần xác nhận).
  - Thiết lập bảng phân tuyến (Routing) rõ ràng theo bản chất công việc thay vì chỉ bắt từ khóa bề mặt; bổ sung quy tắc ánh xạ tên riêng sang handle không có `@` (`Sam Altman` → `sama`, `Elon Musk` → `elonmusk`, `Andrej Karpathy` → `karpathy`, `Yann LeCun` → `ylecun`, `Demis Hassabis` → `demishassabis`).
  - Thiết lập quy tắc hội thoại nhiều lượt (Multi-turn): chỉ thực thi yêu cầu ở lượt cuối, kế thừa ngữ cảnh từ các lượt trước, ưu tiên thông tin đính chính mới nhất và cho phép gọi nhiều tool song song trong cùng một lượt khi câu hỏi có nhiều nhu cầu.
  - Bắt buộc mọi yêu cầu gửi/đăng lên Telegram đều phải gọi `clarify(response_type="yes_no")` trước, kể cả khi người dùng mới nói `"bản tin này"` mà chưa đưa toàn văn.
- **Cải tiến `starter_v0/artifacts/tools.yaml`:**
  - Viết lại toàn bộ `description` của 14 tool theo cấu trúc `USE WHEN ... / DO NOT USE WHEN ...` để phân định rõ ranh giới giữa các cặp tool dễ nhầm (`timeline` vs `social_search`, `lookup` vs `fetch`, `papers` vs `paper_text`, `lookup` vs `hackernews`/`github_search`/`wikipedia`).
  - Chuẩn hóa mô tả tham số: `query` chỉ giữ đúng từ khóa chủ đề gốc (không tự nối thêm `"news"`, `"today"`, `"artificial intelligence"`), quy ước rõ `topic=news`, `timeframe=day|week|month|year`, `search_type=Top|Latest`, và đặt `required` cho `response_type` của `clarify` cũng như `policy_area` của `policy`.
- **Mở rộng 4 tool mới & vá 6 lỗi trong code của tool có sẵn:**
  - Thêm 4 tool mới (`hackernews`, `github_search`, `wikipedia`, `current_time`) có kiểm tra kiểu dữ liệu đầu vào chặt chẽ và luôn trả về error dict thay vì raise exception.
  - Phát hiện qua unit test và sửa 6 lỗi biên trong code của các tool có sẵn (`send`, `timeline`, `social_search`, `lookup`, `fetch`, `format`).

---

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ [`starter_v0/artifacts/version_log.csv`](../../starter_v0/artifacts/version_log.csv) và `starter_v0/runs/*.json`. Tất cả các file run đều đạt `provider_error_cases == 0` và `measured_cases == total_cases`. Bản lưu từng version nằm ở `starter_v0/artifacts/versions/v0..v3/`.

| Version | Changed Artifact | Hypothesis | Metric Before (`case_accuracy`) | Metric After (`case_accuracy`) | `tool_routing` / `arg` / `multiturn` | Run File |
|---|---|---|---:|---:|---|---|
| `v0` | `baseline` | Đo hành vi chưa tối ưu: prompt xấu cố ý + mô tả tool mơ hồ | — | **0.60** (12/20) | `0.70` / `0.60` / `0.8333` | [`v0_B_base_gemini_20261110T150231415716.json`](../../starter_v0/runs/v0_B_base_gemini_20261110T150231415716.json) |
| `v1` | `system_prompt.md` | Bỏ chỉ dẫn xấu (đoán thay vì hỏi, gửi không cần xác nhận, ép 1 bước); thêm luật clarify & confirm sẽ sửa nhóm `missing_info`, `out_of_scope`, `unnecessary_tool` | 0.60 | **0.65** (13/20) | `0.90` / `0.65` / `0.5000` | [`v1_B_base_gemini_20261110T152357017662.json`](../../starter_v0/runs/v1_B_base_gemini_20261110T152357017662.json) |
| `v2` | `tools.yaml` | Viết lại description mọi tool (`USE WHEN / DO NOT USE`) + convention args (handle không `@`, `query` gốc, `topic=news`, `timeframe`, `Top`) sẽ sửa `wrong_tool` và `wrong_arg_value` | 0.65 | **0.95** (19/20) | `1.00` / `0.95` / `1.0000` | [`v2_B_base_gemini_20261110T152457433892.json`](../../starter_v0/runs/v2_B_base_gemini_20261110T152457433892.json) |
| `v3` | `system_prompt.md + tools.yaml` | Bảng routing, ép `clarify(response_type="yes_no")` cho mọi yêu cầu gửi/đăng Telegram kể cả khi chưa đưa toàn văn, luật multi-turn/parallel + thêm 4 tool mới giúp đạt 1.00 mà không làm rớt routing cũ | 0.95 | **1.00** (20/20) | `1.00` / `1.00` / `1.0000` | [`v3_B_base_gemini_20261110T153554881404.json`](../../starter_v0/runs/v3_B_base_gemini_20261110T153554881404.json) |

Tổng hợp kết quả `v3` trên cả 3 bộ eval:
- **Base (`data/eval_base.json`):** `20/20` PASS (`1.00`) — [`v3_B_base_gemini_20261110T153554881404.json`](../../starter_v0/runs/v3_B_base_gemini_20261110T153554881404.json)
- **Group (`data/eval_group.json`):** `10/10` PASS (`1.00`) — [`v3_B_group_gemini_20261110T153621028288.json`](../../starter_v0/runs/v3_B_group_gemini_20261110T153621028288.json)
- **Extension (`data/eval_research_extension.json`):** `10/10` PASS (`1.00`) — [`v3_B_extension_gemini_20261110T153651074202.json`](../../starter_v0/runs/v3_B_extension_gemini_20261110T153651074202.json)

### B2. Failure Analysis

Toàn bộ 8 case FAIL của baseline `v0` ([`v0_B_base_gemini_20261110T150231415716.json`](../../starter_v0/runs/v0_B_base_gemini_20261110T150231415716.json)) và cách khắc phục qua `v1` → `v2` → `v3`:

| Case ID | Failure Type | Actual Tool Calls (`v0`) | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_tool` (`wrong_arg_value`) | `lookup(query="AI news artificial intelligence", topic="news", timeframe="day")` | Model tự mở rộng `query` thay vì giữ đúng từ khóa `"AI"` | Quy định rõ trong `tools.yaml` (`v2`): `query` chỉ lấy đúng từ khóa chủ đề gốc → **PASS từ v2** |
| `R08_out_of_scope` | `out_of_scope` (`unexpected_tool_call`) | `lookup(query="nguyên hàm của x^2")` | Câu hỏi toán học ngoài phạm vi nhưng vẫn gọi `lookup` do prompt starter ép gọi tool | Bỏ chỉ dẫn ép gọi tool trong `system_prompt.md` (`v1`) + thêm mục `# Scope` → **PASS từ v1** |
| `R09_no_tool_capability` | `unnecessary_tool` (`unexpected_tool_call`) | `policy(query="nhiệm vụ và khả năng của trợ lý nghiên cứu", policy_area="all")` | Câu hỏi meta "bạn là gì, làm được gì" nhưng lại gọi `policy` | Bỏ chỉ dẫn ép gọi tool (`v1`) + quy định trả lời trực tiếp câu hỏi meta → **PASS từ v1** |
| `R10_missing_handle` | `missing_info` (`missing_tool_call`) | `timeline(screenname="sama", limit=5)` | Thiếu tên tài khoản nhưng tự đoán `sama` do prompt starter bảo "pick a well-known account like Sam Altman" | Xóa chỉ dẫn đoán mò, bắt buộc gọi `clarify(response_type="text")` khi thiếu handle (`v1`) → **PASS từ v1** |
| `R11_missing_url` | `missing_info` (`missing_tool_call`) | `fetch(url="https://openai.com/index/learning-to-reason-with-llms/")` | User nói "bài viết này" không kèm link, model tự bịa URL do prompt starter bảo "assume a likely URL" | Bắt buộc gọi `clarify(response_type="text")` khi thiếu URL (`v1`) → **PASS từ v1** |
| `R12_confirm_before_send` | `wrong_boundary` | `v0`: `send(text="Bản tin...", confirmed=True)`; `v1`–`v2`: `clarify(response_type="text")` | `v0` tự gửi luôn không hỏi; `v1`–`v2` đã gọi `clarify` nhưng dùng `response_type="text"` thay vì `"yes_no"` | Trong `v3`, quy định mọi yêu cầu đăng/gửi Telegram phải gọi `clarify(response_type="yes_no")` trước → **PASS ở v3** |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `lookup(query="AI news today", topic="news", timeframe="day")` (thiếu `social_search`) | Prompt `v0` ép "Pick one tool" nên bỏ sót `social_search`, đồng thời dư `"news today"` trong `query` | `v1` bỏ giới hạn 1 tool (gọi song song `lookup` + `social_search`); `v2` chuẩn hóa `query="AI"` → **PASS từ v2** |
| `M02_carryover_timeframe` | `wrong_arg_value` | `lookup(query="robotics AI news", topic="news", timeframe="day")` | Lượt 3 nói "Chỉ tìm robotics thôi" nhưng model vẫn nối `"AI news"` từ lượt 1 vào `query` | `tools.yaml` (`v2`) ghi rõ khi user nói "chỉ tìm X thôi" thì `query` chỉ lấy đúng `"X"` → **PASS từ v2** |

### B3. Team Eval Cases

10 case trong [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json) (5 single-turn `G01`–`G05` + 5 multi-turn `GM01`–`GM05`), kết quả từ [`v3_B_group_gemini_20261110T153621028288.json`](../../starter_v0/runs/v3_B_group_gemini_20261110T153621028288.json) (**10/10 PASS**):

| Case ID | What It Tests | Expected Tool/Behavior | Actual Call (`v3`) | Result |
|---|---|---|---|---|
| `G01_github_routing` (Single) | Hỏi repo mở nhiều sao nhất về RAG → route tới tool mới `github_search` với `sort=stars` | `github_search(sort="stars")` | `github_search(query="RAG", sort="stars", limit=5)` | **PASS** |
| `G02_hackernews_routing` (Single) | Nhắc đích danh Hacker News → route tới `hackernews` (không nhầm sang `social_search`/`lookup`) | `hackernews()` | `hackernews(query="LLM agents", sort_by="relevance", limit=5)` | **PASS** |
| `G03_current_time_routing` (Single) | Hỏi trực tiếp ngày/giờ/thứ → `current_time` (không gọi `lookup`) | `current_time()` | `current_time(utc_offset_hours=7)` | **PASS** |
| `G04_wikipedia_routing` (Single) | Kiến thức nền/tiểu sử có nhắc Wikipedia → `wikipedia` với `title="Alan Turing"` | `wikipedia(title="Alan Turing")` | `wikipedia(title="Alan Turing", lang="vi")` | **PASS** |
| `G05_out_of_scope_translation` (Single) | Dịch thuật không thuộc phạm vi research → từ chối, không gọi tool nào | `no_tool: true` (`refuse`) | `[]` | **PASS** |
| `GM01_no_tool_after_thanks` (Multi, 3 turns) | Lượt cuối là câu hỏi meta sau khi đã cảm ơn → trả lời thẳng, không gọi lại `lookup` của lượt 1 | `no_tool: true` (`answer_without_tool`) | `[]` | **PASS** |
| `GM02_github_sort_and_limit` (Multi, 3 turns) | Gom `"mới cập nhật"` (`sort="updated"` ở lượt 2) + `"Lấy 3 repo"` (`limit=3` ở lượt 3) cho `github_search` | `github_search(sort="updated", limit=3)` | `github_search(query="RAG", sort="updated", limit=3)` | **PASS** |
| `GM03_clarify_then_handle_limit` (Multi, 3 turns) | Thiếu handle ở lượt 1 → bổ sung `"Yann LeCun"` ở lượt 2 (`ylecun` không `@`) + `limit=4` ở lượt 3 | `timeline(screenname="ylecun", limit=4)` | `timeline(screenname="ylecun", limit=4)` | **PASS** |
| `GM04_send_after_user_confirms` (Multi, 3 turns) | Đã có xác nhận rõ ở lượt cuối → gọi `send(confirmed=true)`, không hỏi lại lần nữa | `send(confirmed=true)` | `send(text="Họp team lúc 9h sáng mai", confirmed=true)` | **PASS** |
| `GM05_switch_twitter_to_hackernews` (Multi, 3 turns) | User chuyển nguồn từ Twitter sang Hacker News ở lượt 2, giữ chủ đề `"Claude"` ở lượt 3 | `hackernews()` | `hackernews(query="Claude", sort_by="relevance", limit=5)` | **PASS** |

### B4. Live Chat Evidence

Trích từ phiên chạy thật [`starter_v0/transcripts/v3_gemini_20261110T153848310732.transcript.json`](../../starter_v0/transcripts/v3_gemini_20261110T153848310732.transcript.json) (5 lượt liên tiếp):

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---:|---|---|---|---|
| 1 | `Tìm giúp mình 3 repo GitHub nhiều sao nhất về RAG` | `github_search(query="RAG", sort="stars", limit=3)` | `v3+p6ac479ebc767+t27d0eee1478d` | `answered`: Trả về 3 repo thật từ GitHub API (`langgenius/dify` 160.8k⭐, `open-webui/open-webui` 158.3k⭐, `langchain-ai/langchain` 149.3k⭐) kèm URL |
| 2 | `Tóm tắt bài viết này hộ mình` | `clarify(question="Bạn vui lòng cung cấp đường dẫn (URL) của bài viết cần tóm tắt nhé!", response_type="text")` | `v3+p6ac479ebc767+t27d0eee1478d` | `waiting_for_user`: Phát hiện thiếu URL, tạm dừng chờ user bổ sung thay vì tự bịa link |
| 3 | `À mình muốn xem tóm tắt Wikipedia về Alan Turing` | `wikipedia(title="Alan Turing", lang="vi")` | `v3+p6ac479ebc767+t27d0eee1478d` | `answered`: Gọi Wikipedia REST API tiếng Việt, tóm tắt tiểu sử & Phép thử Turing kèm link nguồn |
| 4 | `Đăng bản tin tóm tắt về Alan Turing này lên Telegram giúp mình` | `clarify(question="Bạn có chắc chắn muốn đăng bản tin tóm tắt về Alan Turing này lên Telegram không?", response_type="yes_no")` | `v3+p6ac479ebc767+t27d0eee1478d` | `waiting_for_user`: Chặn hành động gửi, hỏi xác nhận `yes_no` trước |
| 5 | `Có, mình xác nhận, gửi đi` | `send(confirmed=true, text="Dưới đây là tóm tắt thông tin về **Alan Turing**...")` | `v3+p6ac479ebc767+t27d0eee1478d` | `answered`: Sau khi user xác nhận mới gọi `send(confirmed=true)` với đúng nội dung bản tin |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`hackernews`, `github_search`, `wikipedia`, `current_time`) | `starter_v0/tools/{hackernews,github_search,wikipedia,current_time}/` (`tool.py` + `TOOL.md`), `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml` | Cả 4 tool đều có `TOOL.md` đúng frontmatter contract, pass `test_tool_contract.py` và đạt 100% routing/args trên `eval_group.json` | Kiểm tra tham số rỗng/sai kiểu trước khi gọi mạng; bắt mọi `RequestException` và trả về error dict thay vì raise |
| Unit test tool mới (≥ 3 test/tool) | [`starter_v0/tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py) (`pytest`: **139 passed, 0 failed, 0 skipped**) | 19 test riêng cho 4 tool mới (happy path, bad input, rate-limit/network error) + hoàn thành toàn bộ stub test của tool có sẵn | Fixture `block_network` trong `conftest.py` chặn mọi kết nối HTTP thật khi chạy test |
| UI (lệnh chạy + link dùng thử) | [`starter_v0/app.py`](../../starter_v0/app.py), [`starter_v0/scripts/serve_tunnel.py`](../../starter_v0/scripts/serve_tunnel.py), `starter_v0/transcripts/ui_*.transcript.json` | Chạy `streamlit run app.py`, chọn được version `v0`–`v3`, hiển thị trực tiếp từng tool call/result, tự lưu transcript | Hiển thị nguyên trạng kết quả/lỗi của tool, không che giấu lỗi khi thiếu key hoặc API lỗi |

- **Tổng số test đã viết/chạy:** `139 passed, 0 failed, 0 skipped` (trong đó `test_tools_todo.py` có 45 test cases bao gồm parameterized tests).
- **Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được:** Trong `send(text, confirmed)`, code gốc viết `if not confirmed:`. Nếu model truyền chuỗi `confirmed="false"` hoặc `"no"`, Python coi chuỗi khác rỗng là `True` nên **vẫn gửi tin thật lên Telegram**! Bộ `run_eval.py` chỉ kiểm tra xem model gọi hàm gì trên các case chuẩn, không phát hiện được lỗi kiểu dữ liệu bên trong hàm `send_telegram`. Unit test `test_send_with_string_false_does_not_send` đã bắt được lỗi này và nhóm đã sửa thành `if confirmed is not True:`.

### B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Hơn 3 tool mới (4 tool do nhóm tự viết) | `starter_v0/tools/{hackernews,github_search,wikipedia,current_time}/`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/data/eval_group.json` | 4 tool mới (`hackernews`, `github_search`, `wikipedia`, `current_time`), mỗi tool có `TOOL.md`, đăng ký đầy đủ, có 4–7 unit test/tool và có case kiểm tra trong `eval_group.json` (`G01`–`G04`, `GM02`, `GM05`) | Mô tả rõ trong `tools.yaml` chỉ gọi khi người dùng nêu đúng nguồn để không làm nhiễu routing của 10 tool gốc |
| Test challenge (`0 skipped` + 6 regression tests cho bug trong tool có sẵn) | [`starter_v0/tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py) | Toàn bộ suite đạt **`139 passed, 0 failed, 0 skipped`**; phát hiện và sửa **6 bug** trong các tool có sẵn kèm regression test | Giữ nguyên chữ ký hàm để tương thích ngược 100% với `test_tool_contract.py` |

**Chi tiết 6 bug phát hiện và sửa trong các tool có sẵn (Challenge+):**

| # | Tool | Input biên từ model | Hành vi cũ (trước khi sửa) | Cách sửa | Regression test trong `tests/test_tools_todo.py` |
|---:|---|---|---|---|---|
| 1 | `send` | `confirmed="false"` / `"no"` (chuỗi) | `if not confirmed:` coi chuỗi khác rỗng là `True` → **vẫn gửi tin thật** lên Telegram | Kiểm tra chặt `if confirmed is not True:` | `test_send_with_string_false_does_not_send` |
| 2 | `timeline`, `social_search` | `limit=-2` (trên 6 tweet) | Slice âm `items[:-2]` trả 4 tweet thay vì báo lỗi/clamp | Clamp `max(1, min(int(limit or 5), 20))` | `test_timeline_non_positive_limit_never_returns_slice_from_end` |
| 3 | `lookup` | `query=""`, `max_results=-3`, `timeframe="today"` | Vẫn gọi Tavily với query rỗng (tốn credit) hoặc gửi `timeframe`/`max_results` ngoài enum gây HTTP 400 | Chặn `query` rỗng trước khi gọi mạng; lọc theo `VALID_TOPICS`/`VALID_TIMEFRAMES`; clamp `max_results` `1..20` | `test_lookup_empty_query_does_not_spend_api_credit`, `test_lookup_clamps_max_results_and_accepts_numeric_string`, `test_lookup_drops_out_of_enum_timeframe_and_topic` |
| 4 | `fetch` | `url=""` hoặc `"ftp://..."` | Vẫn gửi POST sang Firecrawl và trả về 1 item rỗng giả | Kiểm tra `url` phải bắt đầu bằng `http://` hoặc `https://` trước khi gọi mạng | `test_fetch_rejects_non_http_url_without_request` |
| 5 | `format` | `items=["chuỗi", None]` | `AttributeError: 'str' object has no attribute 'get'` | Chuẩn hóa phần tử chuỗi thành `{"title": str(item)}` và lọc bỏ `None` | `test_format_accepts_plain_string_and_null_items` |
| 6 | `timeline` | `screenname="@sama"` hoặc `"  "` | Gửi nguyên `@sama` hoặc chuỗi rỗng lên RapidAPI | Tự `.lstrip("@")`, trả error dict nếu rỗng mà không gọi mạng | `test_timeline_strips_at_sign_from_handle`, `test_timeline_empty_handle_returns_error_without_request` |

---

## 5. Khó khăn và cách xử lý

- **Khó khăn 1 — Nhầm lẫn giữa `clarify(response_type="text")` và `clarify(response_type="yes_no")` ở case `R12_confirm_before_send`:**
  - Ở `v1` và `v2`, khi user nói `"Đăng bản tin này lên Telegram giúp mình"` mà chưa kèm nội dung bản tin, model gọi `clarify(response_type="text")` để xin nội dung thay vì xin xác nhận `yes_no`.
  - **Cách xử lý:** Trong `v3`, nhóm quy định rõ trong cả `system_prompt.md` và `tools.yaml` rằng mọi yêu cầu mang tính chất gửi/đăng/xuất bản lên Telegram đều phải ưu tiên kiểm tra ranh giới an toàn bằng `clarify(response_type="yes_no")` trước tiên. Kết quả `R12` chuyển từ FAIL sang PASS ở `v3`.
- **Khó khăn 2 — Giới hạn tần suất gọi API (HTTP 429 / Quota) khi chạy liên tiếp nhiều bộ eval:**
  - Khi chạy 20 case `base` + 10 case `group` + 10 case `extension`, đôi lúc endpoint của model trả lỗi tạm thời `429 RESOURCE_EXHAUSTED` hoặc `503 UNAVAILABLE`.
  - **Cách xử lý:** Bổ sung cơ chế fallback thử lại qua danh sách model tương đương trong `starter_v0/providers/gemini_provider.py` khi gặp mã lỗi tạm thời `429`/`503`, đồng thời cấu hình đầy đủ bộ key dự phòng (`OPENROUTER_API_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`) để mọi file run đều có `provider_error_cases == 0`.

---

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và 6 báo cáo cá nhân:

| STT | Thành viên | MSSV | Báo cáo cá nhân | Phần việc chính |
| --: | --- | --- | --- | --- |
| 1 | Đinh Hoàng Phong | `2A202604090` | [`2A202604090_DinhHoangPhong.md`](2A202604090_DinhHoangPhong.md) | Tối ưu `system_prompt.md` & `tools.yaml` (`v0`→`v3`), đăng ký `tools/__init__.py`, chạy eval `base` & `extension` |
| 2 | Phùng Quang Trà | `2A202604094` | [`2A202604094_PhungQuangTra.md`](2A202604094_PhungQuangTra.md) | Trưởng nhóm; tổng hợp `TEAM.md`, `group_report.md`, vá lỗi guardrail tool `send` và `format` |
| 3 | Vũ Nam Khánh | `2A202604112` | [`2A202604112_VuNamKhanh.md`](2A202604112_VuNamKhanh.md) | Viết 2 tool mới (`github_search`, `hackernews`) + vá lỗi input validation cho `lookup`, `fetch` |
| 4 | Nguyễn Ánh Dương | `2A202604087` | [`2A202604087_NguyenAnhDuong.md`](2A202604087_NguyenAnhDuong.md) | Viết 2 tool mới (`wikipedia`, `current_time`) + vá lỗi `@handle` và slice âm cho `timeline`, `social_search` |
| 5 | Nguyễn Tuấn Anh | `2A202604089` | [`2A202604089_NguyenTuanAnh.md`](2A202604089_NguyenTuanAnh.md) | Thiết kế 10 case `eval_group.json`, chạy eval `group`, viết toàn bộ unit test `test_tools_todo.py` (139 passed, 0 skipped) |
| 6 | Phạm Duy Thành | `2A202604075` | [`2A202604075_PhamDuyThanh.md`](2A202604075_PhamDuyThanh.md) | Xây dựng Streamlit UI `app.py`, `poster.html`, script Cloudflare Tunnel `scripts/` & chạy Live Chat `transcripts/` |

---

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix nào thuộc `system_prompt.md`?**
  - Các quy tắc hành vi tổng quát và ranh giới an toàn xuyên suốt hội thoại: không đoán mò khi thiếu thông tin (`R10`, `R11`), luôn xin xác nhận `clarify(response_type="yes_no")` trước mọi hành động gửi/đăng (`R12`), từ chối câu hỏi ngoài phạm vi hoặc trả lời thẳng câu hỏi meta mà không gọi tool (`R08`, `R09`, `R14`, `G05`, `GM01`), cho phép gọi nhiều tool song song trong cùng một lượt (`R13`, `E06`–`E09`), và nguyên tắc xử lý hội thoại nhiều lượt (chỉ thực thi lượt cuối, kế thừa ngữ cảnh và ưu tiên thông tin đính chính ở lượt sau).
- **Fix nào thuộc `tools.yaml`?**
  - Mô tả phân biệt ranh giới giữa các tool dễ nhầm (`timeline` cho bài CỦA 1 tài khoản vs `social_search` cho bài VỀ 1 chủ đề vs `hackernews` vs `lookup` vs `fetch`), quy ước định dạng từng tham số (`screenname` không có `@` kèm ánh xạ tên người nổi tiếng, `query` giữ đúng từ khóa chủ đề gốc không chèn thêm `"news today"`, `topic=news`, `timeframe=day|week|month|year`, `search_type=Top|Latest`), và đánh dấu `required` cho các trường quan trọng (`response_type` của `clarify`, `policy_area` của `policy`). Thực tế từ `v1` → `v2` cho thấy chỉ riêng việc làm rõ `tools.yaml` đã kéo `case_accuracy` từ **0.65 lên 0.95** (`argument_accuracy` từ 0.65 lên 0.95, `multiturn_accuracy` từ 0.50 lên 1.00).
- **Failure nào cần review thủ công thay vì chấm tự động?**
  - Chất lượng câu trả lời tổng hợp cuối cùng sau khi nhận kết quả từ tool: agent có trích dẫn đúng URL nguồn không, có bịa thêm thông tin ngoài `TOOL_RESULTS_JSON` không, hay có bị đánh lừa bởi các dòng prompt-injection nằm trong nội dung web/policy (`untrusted_text`) hay không. Bộ `run_eval.py` chỉ chấm lượt gọi tool đầu tiên (`tool_calls` và `args`), nên bắt buộc phải kết hợp review thủ công qua `transcripts/*.transcript.json`.
- **Nếu có thêm một vòng (`v4`), nhóm sẽ thử giả thuyết nào?**
  - Thử giả thuyết rút gọn `system_prompt.md` và nén `description` trong `tools.yaml` xuống dưới 40% độ dài hiện tại để đánh giá trên các model local nhỏ (`qwen2.5:7b`, `llama3.2:3b` qua Ollama), đồng thời bổ sung bước chấm tự động xem câu trả lời cuối của agent có chứa URL nguồn từ kết quả tool hay không.

---

## 8. Tài liệu tham khảo

- Tài liệu hướng dẫn Lab Day 03 (`README.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `RULES.md`, `docs/TOOL-SETUP.md`).
- OpenAI Function Calling & Tool Use Specification; Google GenAI SDK (`google-genai`) Documentation.
- Tavily Search API, Firecrawl Scrape API, Algolia Hacker News Search API, GitHub REST Search API, Wikimedia REST API.
