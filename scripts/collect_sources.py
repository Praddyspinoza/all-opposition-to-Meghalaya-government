import json, re, urllib.parse, urllib.request, datetime, pathlib, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"daily_sources.json"
actors=["Mukul Sangma","Ardent Miller Basaiawmoit","Saleng Sangma","Adelbert Nongrum","Ronnie V Lyngdoh","Brightstarwell Marbaniang","Heaving Stone Kharpran","Charles Pyngrope","George B Lyngdoh","Zenith Sangma","A L Hek","Luckshwell M Sangma","Bernard N Marak","Khasi Students Union","Hynniewtrep Youths Council","FKJGP","HNYF","CoMSO","ACHIK","Garo Students Union","CSWO","Jaintia Students Union","Jaintia National Council","CoRP","Garoland State Movement Committee","A'chik Progressive Approach","Thma U Rangli Juki","Meghalaya People's Human Rights Council","Angela Rangad","Agnes Kharshiing","Cherian G Momin"]
try: old=json.loads(OUT.read_text())
except Exception: old={"records":[]}
records={x["url"]:x for x in old.get("records",[]) if x.get("url")}
headers={"User-Agent":"MeghalayaCivicArchive/1.0 (public source index)"}
for actor in actors:
 for platform,query in [("News",'"'+actor+'" Meghalaya when:30d'),("Facebook",'"'+actor+'" site:facebook.com when:30d'),("YouTube",'"'+actor+'" site:youtube.com/watch when:30d'),("X",'"'+actor+'" site:x.com when:30d')]:
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
# Rolling historical backfill: two political actors per run, 2023 onward.
political=actors[:13]
today=datetime.date.today()
for offset in range(2):
 actor=political[(today.toordinal()*2+offset)%len(political)]
 for year in range(2023,today.year+1):
  for platform,domain in [("News",""),("Facebook","site:facebook.com"),("YouTube","site:youtube.com"),("X","site:x.com")]:
   query=f'"{actor}" Meghalaya {domain} after:{year}-01-01 before:{year+1}-01-01'
   url="https://news.google.com/rss/search?q="+urllib.parse.quote(query)+"&hl=en-IN&gl=IN&ceid=IN:en"
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=12) as response:
     root=ET.fromstring(response.read())
    for item in root.findall("./channel/item")[:20]:
     title=item.findtext("title","").strip()
     link=item.findtext("link","").strip()
     if title and link:
      records[link]={"actor":actor,"platform":platform,"title":title,"url":link,"published":item.findtext("pubDate",""),"discovered":datetime.datetime.now(datetime.timezone.utc).isoformat(),"note":"Historical indexed search lead; verify actor and original source"}
   except Exception as e: print("Backfill unavailable",actor,year,platform,str(e)[:90])
old["records"]=sorted(records.values(),key=lambda r:r.get("discovered",""),reverse=True)[:15000]
old["last_checked_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
OUT.write_text(json.dumps(old,ensure_ascii=False,indent=2))
print("Stored",len(old["records"]),"records")
