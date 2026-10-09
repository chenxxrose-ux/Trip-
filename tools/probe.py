import urllib.request, json, ssl, re
U={
'findrate':'https://www.findrate.tw/JPY/',
'bot':'https://rate.bot.com.tw/xrt/flcsv/0/day',
'esun':'https://www.esunbank.com/zh-tw/personal/deposit/rate/forex/foreign-exchange-rates',
'cathay':'https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard/',
'first':'https://ibank.firstbank.com.tw/NetBank/7/0201.html?sh=none',
'taishin':'https://www.taishinbank.com.tw/TSB/personal/deposit/lookup/realtime/',
'tcb':'https://www.tcb-bank.com.tw/personal-banking/deposit-exchange/exchange-rate/spot',
'land':'https://www.landbank.com.tw/Category/Items/%E7%89%8C%E5%91%8A%E5%8C%AF%E7%8E%87',
'mega':'https://www.megabank.com.tw/personal/foreign-exchange/rate/rate',
'ctbc':'https://www.ctbcbank.com/twrbo/zh_tw/dep_index/dep_ratequery/dep_foreign_rates.html',
'sinopac':'https://m.sinopac.com/ws/share/rate/ws_exchange.ashx?exchangeType=REMIT',
'hncb':'https://www.hncb.com.tw/wps/portal/HNCB/exchange_rate',
'chb':'https://www.bankchb.com/frontend/G0100.jsp',
'kgi':'https://www.kgibank.com.tw/zh-tw/personal/interest-rate/fx',
'fubon':'https://www.fubon.com/banking/personal/deposit/exchange_rate/exchange_rate_tw.htm',
}
out={}
for k,u in U.items():
  try:
    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1','Accept-Language':'zh-TW'}),timeout=25)
    b=r.read().decode('utf-8','replace')
    i=b.find('JPY'); j=b.find('日圓'); j=j if j>=0 else b.find('日幣')
    out[k]={'status':r.status,'len':len(b),'jpy_at':i,'snip':b[max(0,i-300):i+1500] if i>=0 else b[max(0,j-300):j+1500] if j>=0 else b[:600]}
  except Exception as e: out[k]={'err':repr(e)[:300]}
open('probe.json','w').write(json.dumps(out,ensure_ascii=False,indent=1))
