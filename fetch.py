# -*- coding: utf-8 -*-
"""
fred-relay/fetch.py  —— 在 GitHub Action 中运行
================================================
从 FRED JSON API 拉取 8 个危机面板序列，写成 data/<SID>.csv（date,value 升序）。
GitHub 服务器出口能正常访问 FRED（无沙箱 Akamai 封锁），因此这是稳定、新鲜的数据源。
CSV 由沙箱侧 fetch_fred_gh.py 从 raw.githubusercontent.com 拉取。

依赖：仅标准库（urllib / csv / json）。
环境变量：FRED_API_KEY（在仓库 Secrets 中配置）。
"""
import os, json, csv, time, urllib.request

KEY = os.environ.get("FRED_API_KEY", "").strip()
if not KEY:
    raise SystemExit("ERROR: 未设置 FRED_API_KEY 环境变量（请在仓库 Secrets 中配置）")

SERIES = ["UNRATE", "T10Y2Y", "VIXCLS", "IC4WSA", "PAYEMS", "SP500", "NASDAQCOM", "GDP"]
API = ("https://api.stlouisfed.org/fred/series/observations"
       "?series_id={sid}&api_key={key}&file_type=json&sort_order=asc&limit=100000")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)

def fetch_one(sid):
    url = API.format(sid=sid, key=KEY)
    req = urllib.request.Request(url, headers={"User-Agent": "fred-relay", "Accept": "application/json"})
    data = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore"))
    if "error_code" in data:
        raise RuntimeError(f"FRED API {data.get('error_code')}: {data.get('error_message')}")
    return data.get("observations", [])

def main():
    total = 0
    for sid in SERIES:
        try:
            obs = fetch_one(sid)
        except Exception as e:
            print(f"  [WARN] {sid} 拉取失败: {e}")
            continue
        path = os.path.join(OUT, sid + ".csv")
        n = 0
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "value"])
            for o in obs:
                v = o.get("value", "")
                if v in (".", "", None):
                    continue
                w.writerow([o.get("date", ""), v])
                n += 1
        print(f"  [OK] {sid}: {n} 行 -> data/{sid}.csv")
        total += n
    print(f"完成：共写入 {total} 行。")

if __name__ == "__main__":
    main()
