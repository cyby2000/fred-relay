# fred-relay —— 危机面板 FRED 数据中继

## 为什么需要它
沙箱出口对 `fred.stlouisfed.org` 有 Akamai 间歇性封锁（好窗口时通、坏窗口时全超时），
导致危机预警面板的自动宏观指标无法稳定拉取。

本仓库用 **GitHub Action** 解决：
1. Action 运行在 GitHub 服务器（出口能正常访问 FRED，无封锁）；
2. 每日 `07:00 UTC`（北京 15:00，早于面板 16:00）拉取 8 个序列并 commit 到 `data/*.csv`；
3. 沙箱侧 `fetch_fred_gh.py` 从 `raw.githubusercontent.com` 拉 CSV（已验证稳定、秒级可达）。

数据永远新鲜，且彻底绕开沙箱封锁。

## 部署步骤（约 2 分钟）
1. 在 GitHub 新建一个**公开**仓库，命名为 `fred-relay`（或你喜欢的名字）。
2. 仓库 **Settings → Secrets and variables → Actions → New repository secret**：
   - Name: `FRED_API_KEY`
   - Value: 你的 FRED API key（免费注册 https://fredaccount.stlouisfed.org/apikeys）
3. 把本目录内容（ `fetch.py` 和 `.github/workflows/update.yml` ）push 到仓库。
4. 进入仓库 **Actions** 标签，手动触发一次 `Update FRED data`（或等次日 07:00 UTC 自动跑），
   确认 `data/` 下生成 8 个 CSV。

## 沙箱侧使用
二选一（推荐方式②，自动化无需手传环境变量）：

**① 环境变量**
```bash
export FRED_RELAY_REPO=你的用户名/fred-relay   # 必填
# export FRED_RELAY_BRANCH=main               # 可选，默认 main
```

**② 本地文件（推荐，crisis_watch.py 与 fetch_fred_gh.py 均会自动读取）**
在 `crisis-watch/` 目录新建文件 `.fred_relay_repo`，内容仅一行：
```
你的用户名/fred-relay
```
FRED API key 同理已支持 `.fred_api_key` 文件（crisis-watch/ 下已有）。

配置好后，主流程 `python crisis_watch.py [DATE]` 会自动走「GitHub 中继优先 → FRED API 直连补充 → 本地缓存兜底」双源逻辑。

## 8 个序列
UNRATE（失业率）、T10Y2Y（10Y-2Y 利差）、VIXCLS（VIX 恐慌）、
IC4WSA（初申失业金）、PAYEMS（非农就业）、SP500（标普500）、
NASDAQCOM（纳指）、GDP。

## 文件
- `fetch.py`：Action 内运行，调用 FRED JSON API，写 `data/<SID>.csv`（date,value 升序）。
- `.github/workflows/update.yml`：每日定时 + 手动触发，拉取并提交。
- 沙箱侧 `fetch_fred_gh.py`（在 crisis-watch/ 主目录）：从 raw.githubusercontent.com 拉 CSV 并生成面板摘要。
