---
name: current_time
track: bonus
kind: control
requires_env: []
inputs: [utc_offset_hours]
outputs: [iso, date, time, weekday]
side_effect: false
---
# current_time

Trả về ngày, giờ và thứ hiện tại theo múi giờ UTC (mặc định `+7` — giờ Việt Nam). Chạy hoàn toàn cục bộ trên máy, không gọi mạng và không cần khóa API.

- `utc_offset_hours` là số nguyên trong khoảng `-12..14`. Giá trị không phải số tự động đưa về `7`; ngoài khoảng `-12..14` trả về dict báo lỗi.
- Chỉ dùng khi người dùng hỏi trực tiếp về thời gian/ngày tháng hiện tại ("hôm nay là ngày mấy / thứ mấy / mấy giờ"). Không dùng để giải nghĩa chữ "hôm nay" trong câu hỏi tìm tin tức (khi đó dùng `lookup(timeframe="day")`).
