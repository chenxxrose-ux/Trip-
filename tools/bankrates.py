"""抓取台灣各銀行外幣現鈔牌告匯率（來源：比率網 findrate.tw），輸出 bankrates.json。
由 GitHub Actions 定時執行；網頁只讀取結果檔，不會用到 Claude。"""
import json, re, sys, time, urllib.request, html
from datetime import datetime, timedelta, timezone

CURS = 'USD JPY KRW THB VND HKD SGD MYR PHP IDR CNY EUR GBP AUD NZD CAD CHF MOP INR TRY SEK DKK MXN ZAR'.split()
UA = {'User-Agent': 'Mozilla/5.0 (trip-checklist rate bot; +https://chenxxrose-ux.github.io/Trip-/)', 'Accept-Language': 'zh-TW'}
TPE = timezone(timedelta(hours=8))
FRESH_DAYS = 4  # 超過 4 天沒更新的銀行資料視為過期，不列入比價（週末、連假仍可涵蓋）

ROW = re.compile(r'<td\s+class="bank">\s*<a[^>]*>([^<]{1,30})</a>\s*</td>(.*?)</tr>', re.S)
TD = re.compile(r'<td[^>]*>(.*?)</td>', re.S)

def num(s):
    s = re.sub(r'<[^>]+>', '', s).strip()
    try:
        v = float(s)
        return v if v > 0 else None
    except ValueError:
        return None

def clean(s, n):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.sub(r'\s+', ' ', s).strip()[:n]

def parse(page, today):
    rows, stale = [], 0
    for m in ROW.finditer(page):
        bank = clean(m.group(1), 20)
        tds = TD.findall(m.group(2))
        if len(tds) < 5:
            continue
        cash_buy, cash_sell = num(tds[0]), num(tds[1])
        dm = re.search(r'<!--(\d{4}-\d{2}-\d{2})-->\s*([0-9:]{4,5})', tds[4])
        if not cash_sell or not dm:
            continue
        d = datetime.strptime(dm.group(1), '%Y-%m-%d').date()
        if (today - d).days > FRESH_DAYS or d > today + timedelta(days=1):
            stale += 1
            continue
        fee = clean(tds[5], 60) if len(tds) > 5 else ''
        rows.append([bank, cash_sell, cash_buy, f'{dm.group(1)} {dm.group(2)}', fee])
    rows.sort(key=lambda r: r[1])
    return rows, stale

def main(out):
    now = datetime.now(TPE)
    data = {'v': 1, 'fetchedAt': now.isoformat(timespec='minutes'), 'source': '比率網 findrate.tw', 'freshDays': FRESH_DAYS, 'cur': {}}
    for c in CURS:
        try:
            req = urllib.request.Request(f'https://www.findrate.tw/{c}/', headers=UA)
            page = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
            rows, stale = parse(page, now.date())
            if rows:
                data['cur'][c] = {'rows': rows, 'stale': stale}
            print(c, len(rows), 'fresh,', stale, 'stale')
        except Exception as e:
            print(c, 'ERROR', e)
        time.sleep(1.5)
    # 基本檢查：主要幣別都抓不到就判定失敗，保留上一份好的資料
    if not all(k in data['cur'] and len(data['cur'][k]['rows']) >= 5 for k in ('USD', 'JPY')):
        print('Sanity check failed; keeping previous data'); sys.exit(1)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bankrates.json')
