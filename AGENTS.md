# 🏆 OPC AI TRADER (LUCKY TRADE OS) — SINGLE SOURCE OF TRUTH & MASTER DIRECTIVE
> **MANDATORY SYSTEM DIRECTIVE — ĐỌC FILE NÀY ĐẦU TIÊN KHI BẮT ĐẦU MỌI PHIÊN LÀM VIỆC**  
> **Executive Leadership:** Chairman Victor Chuyen & AI CEO Lucky  
> **Bản quyền sở hữu:** Độc quyền cá nhân Chairman Victor Chuyen (OPC Ecosystem)  
> **Cập nhật lần cuối:** 2026-09-28 (Khởi tạo Nền tảng Giao dịch Agent-Native, Tích hợp MT5 Gateway & Khóa Rủi ro FTMO Demo)

---

## ⚡ 6 NGUYÊN TẮC BẮT BUỘC TUÂN THỦ (NON-NEGOTIABLE LAWS)

### 🔴 ĐIỀU 1: ĐỌC 1 FILE DUY NHẤT KHI KHỞI ĐỘNG PHIÊN MỚI
Mỗi khi AI Agent hoặc kỹ sư bắt đầu phiên làm việc mới tại `D:\TRADE-AI\AI-Trader-main`, **BẮT BUỘC PHẢI ĐỌC FILE NÀY (`AGENTS.md`)**. Không đoán mò, không làm sai lệch kiến trúc lõi, các cổng chốt chặn rủi ro và các cổng kiểm duyệt đã đóng gói.

### 🔴 ĐIỀU 2: TÔN CHỈ DỮ LIỆU THỰC & BẰNG CHỨNG XÁC THỰC (REAL DATA & AUDIT TRAIL)
- Hệ thống hoạt động dựa trên dữ liệu giá thực tế từ MT5 Terminal, Hyperliquid (Crypto), Alpha Vantage / yfinance, và Polymarket.
- Tuyệt đối KHÔNG tự ý inject dữ liệu PnL giả (fake profit demo data).
- Tiêu chí kết quả: Lịch sử giao dịch được xác thực qua ticket đối soát của Broker MT5. Stars, video, backtest không thay thế cho bằng chứng tài khoản thật.

### 🔴 ĐIỀU 3: CHỐT CHẶN PHÊ DUYỆT 2 CỔNG (EXECUTIVE 2-GATE EXECUTION)
- **Cổng 1 — Phê duyệt người (Semi-Auto Approval Gate):**
  - Mọi tín hiệu giao dịch sinh ra từ AI Agent hoặc thuật toán (Trend Following, Donchian Breakout, Bollinger Mean Reversion) luôn ở trạng thái `PENDING_APPROVAL`.
  - Chỉ khi Chairman Victor bấm **"DUYỆT LỆNH"** trên Dashboard hoặc xác nhận qua Telegram, hệ thống mới được phép gửi lệnh `order_send()` xuống MT5.
- **Cổng 2 — Khóa trần rủi ro FTMO (FTMO Drawdown Guard Gate):**
  - Khi chạy chế độ Auto, bộ giám sát quét tài khoản MT5 liên tục:
    - Nếu Sụt giảm trong ngày (Daily Loss) chạm **4.5%** (ngưỡng trần FTMO là 5.0%), hệ thống lập tức kích hoạt trạng thái `DANGER`, đóng toàn bộ lệnh và khóa giao dịch ngày đó.
    - Nếu Tổng sụt giảm (Max Total Drawdown) chạm **9.0%** (ngưỡng trần FTMO là 10.0%), hệ thống lập tức ngắt toàn bộ kết nối.

### 🔴 ĐIỀU 4: CẤU HÌNH TÀI KHOẢN FTMO MASTER
- **Tài khoản FTMO Demo chính thức:**
  - **Platform:** MetaTrader 5 (MT5 x64)
  - **Login ID:** `1514763831`
  - **Master Password:** `36Ia$7Rh!`
  - **Investor Password:** `!6Qhf?*XV9@JK`
  - **Server:** `FTMO-Demo`
- Mọi kết nối đều được quản lý tập trung qua module [service/server/mt5_gateway.py](file:///D:/TRADE-AI/AI-Trader-main/service/server/mt5_gateway.py).

### 🔴 ĐIỀU 5: 6 SẢN PHẨM GIAO DỊCH CỐT LÕI (CHAIRMAN APPROVED ASSETS)
Hệ thống tập trung tối đa nguồn lực vào 6 sản phẩm đã được Chairman Victor phê duyệt:
1. **BTCUSD:** Bitcoin CFD (Crypto)
2. **XAUUSD:** Vàng Spot Gold CFD (Commodities)
3. **WTI:** Dầu thô US Oil Spot CFD (Commodities)
4. **EURUSD:** Forex Major Pair
5. **GBPUSD:** Forex Major Pair
6. **USDJPY:** Forex Major Pair (Tính toán PnL quy đổi JPY sang USD chính xác)

### 🔴 ĐIỀU 6: HẠ TẦNG TRÍ TUỆ NHÂN TẠO 9ROUTER (AI INFRASTRUCTURE)
- Toàn bộ tác vụ phân tích vĩ mô, bóc tách tâm lý thị trường, thẩm định chất lượng tín hiệu (Signal Quality Scoring) được điều phối qua **9Router Local AI Proxy** (`http://localhost:20128/v1`).
- Combo ưu tiên tối thượng: `fcs-astra` (`cx/gpt-6-astra` kết hợp fallback sang `ag/claude-sonnet-4-6` và `ag/gemini-3.8-flash`).

---

## 🗺️ CÂY THƯ MỤC CHUẨN CỦA HỆ THỐNG (PROJECT REPOSITORY MAP)

```
D:/TRADE-AI/AI-Trader-main/
├── AGENTS.md                                   ← [SINGLE SOURCE OF TRUTH] Bản chỉ thị tối cao & bàn giao hệ thống
├── README.md & README_ZH.md                    ← Tài liệu giới thiệu kiến trúc Agent-Native
├── .env & .env.example                         ← Cấu hình môi trường (Database, API keys, CORS)
├── .venv/                                      ← Python 3.11 Virtual Environment (uv managed)
├── skills/                                     ← Các bộ quy chuẩn MCP/Agent Skills
│   ├── ai4trade/SKILL.md                       ← Skill đăng ký Agent, xuất bản tín hiệu, tham gia Challenge
│   ├── copytrade/SKILL.md                      ← Skill tự động sao chép lệnh từ top trader
│   ├── tradesync/SKILL.md                      ← Skill đồng bộ hóa lệnh realtime
│   ├── heartbeat/SKILL.md                      ← Long-polling nhận thông báo, phản biện, task mới
│   ├── market-intel/SKILL.md                   ← Bảng tin vĩ mô, dòng tiền ETF, tâm lý mạng xã hội
│   └── polymarket/SKILL.md                     ← Dữ liệu thị trường dự đoán Polymarket
├── service/
│   ├── requirements.txt                        ← Danh sách dependencies Python (FastAPI, MT5, yfinance...)
│   ├── server/                                 ← [BACKEND FASTAPI ENGINE]
│   │   ├── main.py                             ← Khởi tạo Server (Port 8000), logging, startup events
│   │   ├── routes.py                           ← Router trung tâm tích hợp 11 phân hệ
│   │   ├── mt5_gateway.py                      ← Gateway MT5 & FTMO Challenge Risk Rules
│   │   ├── routes_mt5.py                       ← REST API endpoints cho MT5 (/v1/mt5/*)
│   │   ├── worker.py                           ← Background Worker đa nền tảng (Windows msvcrt / Linux fcntl)
│   │   ├── database.py                         ← SQLite / PostgreSQL dual-mode engine (30+ tables)
│   │   ├── price_fetcher.py                    ← Feeds giá: Alpha Vantage, yfinance, Hyperliquid, Polymarket
│   │   ├── challenge_scoring.py                ← Mark-to-market portfolio replay & Drawdown calculation
│   │   ├── signal_quality.py                   ← AI Heuristic parsing tín hiệu: Entry, SL, TP, Evidence score
│   │   ├── market_intel.py                     ← Thu thập tin tức vĩ mô, ETF flows, Adanos sentiment
│   │   ├── routes_agent.py & routes_signals.py ← Quản lý định danh Agent & Tín hiệu giao dịch
│   │   ├── routes_trading.py                   ← Giao dịch, vị thế, sao chép lệnh (Copy Trading)
│   │   ├── routes_challenges.py                ← Đấu trường thi đấu & Xếp hạng PnL
│   │   └── tests/                              ← 23 Test Suites tự động đạt 100% Pass
│   └── frontend/                               ← [WEB DASHBOARD CONSOLE]
│       ├── package.json & vite.config.mts      ← React 18, TypeScript, Vite 5 (Port 3000)
│       └── src/
│           ├── App.tsx & AppPages.tsx          ← Giao diện Console chính (Signals, Positions, Leaderboard)
│           ├── ChallengePage.tsx               ← Giao diện Đấu trường Thử thách
│           ├── i18n.ts                         ← Hệ thống song ngữ (Đang nâng cấp thêm Tiếng Việt VI)
│           └── index.css                       ← Hệ thống CSS Dark Mode Luxury
```

---

## 📊 TIẾN ĐỘ THỰC HIỆN & TRẠNG THÁI HỆ THỐNG (LIVE STATUS)

| Hạng mục | Nội dung công việc | File thực thi | Trạng thái | Kiểm thử tự động |
|---|---|---|:---:|:---:|
| **1. Windows Fix** | Sửa lỗi `fcntl` chỉ chạy trên Unix, chuyển sang file lock đa nền tảng (`msvcrt`) | `service/server/worker.py` | ✅ Hoàn thành | Đã xác minh trên Windows |
| **2. Python 3.11 Setup** | Tạo môi trường ảo CPython 3.11.15 sạch qua `uv`, cài đặt 85 packages | `.venv/` | ✅ Hoàn thành | Exit code 0 |
| **3. Dependency Fix** | Cài đặt `email-validator` & `metatrader5` vào backend requirements | `service/requirements.txt` | ✅ Hoàn thành | Khắc phục lỗi Pydantic |
| **4. MT5 FTMO Gateway** | Xây dựng Gateway MT5 kết nối tài khoản FTMO Demo `1514763831` | `service/server/mt5_gateway.py` | ✅ Hoàn thành | 6/6 tests pass |
| **5. FTMO Drawdown Guard** | Giám sát trần Daily Loss (4.5%/5.0%) & Max Drawdown (9.0%/10.0%) | `service/server/mt5_gateway.py` | ✅ Hoàn thành | 6/6 tests pass |
| **6. REST API MT5** | Xây dựng 9 endpoint `/v1/mt5/*` (status, connect, account, positions, quote, order, risk) | `service/server/routes_mt5.py` | ✅ Hoàn thành | 3/3 tests pass |
| **7. Mở rộng Thị trường** | Thêm `forex` và `commodities` (XAUUSD, WTI) vào hệ thống | `service/server/routes_shared.py` | ✅ Hoàn thành | 7/7 tests pass |
| **8. MT5 Desktop Client** | Cài đặt MetaTrader 5 Terminal trên máy trạm để kích hoạt IPC | `terminal64.exe` | ⏳ Chờ chạy setup | Đã sẵn sàng đường link |

---

## 🛠️ LỆNH THỰC THI CHUẨN (STANDARD COMMANDS)

### 1. Kích hoạt môi trường và chạy Backend API (Port 8000):
```powershell
cd D:\TRADE-AI\AI-Trader-main
& ".\.venv\Scripts\python.exe" service\server\main.py
```

### 2. Chạy Background Worker (Xử lý định giá & đồng bộ):
```powershell
cd D:\TRADE-AI\AI-Trader-main
& ".\.venv\Scripts\python.exe" service\server\worker.py
```

### 3. Chạy kiểm thử tự động MT5 Gateway:
```powershell
cd D:\TRADE-AI\AI-Trader-main
& ".\.venv\Scripts\pytest.exe" service\server\tests\test_mt5_gateway.py service\server\tests\test_routes_mt5.py
```

### 4. Kiểm tra trạng thái kết nối MT5 thực tế:
```powershell
cd D:\TRADE-AI\AI-Trader-main\service\server
& "..\..\.venv\Scripts\python.exe" -c "from mt5_gateway import get_mt5_gateway; gw = get_mt5_gateway(); print(gw.connect())"
```

---

## 📌 QUY TRÌNH KÍCH HOẠT KẾT NỐI FTMO DEMO THỰC TẾ

Để hoàn tất kết nối sống 100% giữa code Python và tài khoản FTMO:
1. Tải và cài đặt phần mềm **MetaTrader 5 Terminal** từ trang FTMO (hoặc link chính thức của MQL5).
2. Mở phần mềm MT5 lên, chọn Server `FTMO-Demo`, đăng nhập tài khoản `1514763831` với mật khẩu `36Ia$7Rh!`.
3. Khi phần mềm MT5 đang chạy, backend Python sẽ tự động kết nối qua kênh IPC trong vòng **0.5 giây**, đọc toàn bộ Balance, Equity và sẵn sàng nhận lệnh từ Dashboard.
