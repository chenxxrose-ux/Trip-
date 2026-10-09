import urllib.request
H={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1','Accept-Language':'zh-TW'}
for n,u in [('fr_jpy.html','https://www.findrate.tw/JPY/'),('fr_robots.txt','https://www.findrate.tw/robots.txt'),('fr_home.html','https://www.findrate.tw/'),('fr_vnd.html','https://www.findrate.tw/VND/')]:
  try: b=urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=25).read()
  except Exception as e: b=repr(e).encode()
  open('probe_'+n,'wb').write(b)
