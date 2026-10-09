import json, re, urllib.parse, urllib.request, datetime, pathlib, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"daily_sources.json"
actors=["Mukul Sangma","Ardent Miller Basaiawmoit","Saleng Sangma","Adelbert Nongrum","Ronnie V Lyngdoh","Brightstarwell Marbaniang","Heaving Stone Kharpran","Charles Pyngrope","George B Lyngdoh","Zenith Sangma","A L Hek","Luckshwell M Sangma","Bernard N Marak","Khasi Students Union","Hynniewtrep Youths Council","FKJGP","HNYF","CoMSO","ACHIK","Garo Students Union","CSWO","Jaintia Students Union","Jaintia National Council","CoRP","Garoland State Movement Committee","A'chik Progressive Approach","Thma U Rangli Juki","Meghalaya People's Human Rights Council","Angela Rangad","Agnes Kharshiing","Cherian G Momin"]
try: old=json.loads(OUT.read_text())
except Exception: old={"records":[]}
records={x["url"]:x for x in old.get("records",[]) if x.get("url")}
headers={"User-Agent":"MeghalayaCivicArchive/1.0 (public source index)"}
for actor in actors:
 for platform,query in [("News",'"'+actor+'" Meghalaya when:7d'),("Facebook",'"'+actor+'" site:facebook.com when:7d'),("YouTube",'"'+actor+'" site:youtube.com/watch when:7d'),("X",'"'+actor+'" site:x.com when:7d')]:
  url="https://news.google.com/rss/search?q="+urllib.parse.quote(query)+"&hl=en-IN&gl=IN&ceid=IN:en"
  try:
   req=urllib.request.Request(url,headers=headers)
   with urllib.request.urlopen(req,timeout=12) as response: root=ET.fromstring(response.read())
   for item in root.findall("./channel/item")[:12]:
    title=item.findtext("title","").strip()
    link=item.findtext("link","").strip()
    date=item.findtext("pubDate","")
    if not link or not title: continue
    records[link]={"actor":actor,"platform":platform,"title":title,"url":link,"published":date,"discovered":datetime.datetime.now(datetime.timezone.utc).isoformat(),"note":"Google News indexed link; platform attribution is based on search query and must be checked"}
  except Exception as e: print("Source unavailable:",actor,platform,str(e)[:120])
old["records"]=sorted(records.values(),key=lambda r:r.get("discovered",""),reverse=True)[:15000]
old["last_checked_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
OUT.write_text(json.dumps(old,ensure_ascii=False,indent=2))
print("Stored",len(old["records"]),"records")
