# Prompt/tool versions

Mỗi thư mục `vN/` chứa đúng `system_prompt.md` + `tools.yaml` đã dùng để chạy eval version `vN`.
`artifacts/system_prompt.md` + `artifacts/tools.yaml` (bản nộp) = bản `v3`.

Chạy từng version (xem `scripts/run_versions.py`):

```bash
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json \
  --system-prompt artifacts/versions/v1/system_prompt.md --tools artifacts/versions/v1/tools.yaml
```

| Version | Thay đổi | Giả thuyết |
|---|---|---|
| v0 | starter nguyên bản | baseline |
| v1 | `system_prompt.md` | Prompt xấu (đoán thay vì hỏi, gửi không cần xác nhận, ép 1 bước) là nguyên nhân chính của lỗi `missing_info` / `wrong_boundary` |
| v2 | `tools.yaml` | Mô tả tool mơ hồ gây `wrong_tool` / `wrong_arg_value`; thêm "khi nào dùng / không dùng" + convention args |
| v3 | `system_prompt.md` + `tools.yaml` | Bảng routing + luật multi-turn + few-shot trong prompt; khai báo thêm 4 tool mới |
