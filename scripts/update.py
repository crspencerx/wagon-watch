"""Import entries from explicitly configured, permitted RSS/Atom listing feeds.

No default marketplace scraping. Configure data/feeds.json with feed URL and
source permission you have verified. Entries missing a genuine link are ignored.
"""
import datetime as dt
import json
import pathlib
import hashlib
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / 'data/listings.json'
FEEDS = ROOT / 'data/feeds.json'

def txt(node, tag):
    child = node.find(tag)
    return ''.join(child.itertext()).strip() if child is not None else ''

def parse_feed(raw):
    root = ET.fromstring(raw)
    for item in root.findall('.//item'):
        yield txt(item, 'title'), txt(item, 'link')
    atom = '{http://www.w3.org/2005/Atom}'
    for item in root.findall('.//' + atom + 'entry'):
        link = item.find(atom+'link')
        yield txt(item, atom+'title'), (link.get('href','') if link is not None else '')

def main():
    data=json.loads(DB.read_text()); feeds=json.loads(FEEDS.read_text()).get('feeds',[])
    seen={x['id'] for x in data['listings']}; added=0
    for feed in feeds:
        if not feed.get('permission_confirmed'):
            print('Skipping unverified feed:',feed.get('name')); continue
        url=feed.get('url','')
        if not url.startswith('https://'): continue
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'WagonWatch/0.1 (personal feed reader)'})
            with urllib.request.urlopen(req,timeout=15) as resp:
                raw=resp.read(2_000_001)
            if len(raw)>2_000_000: raise ValueError('Feed too large')
            for title,link in parse_feed(raw):
                if not link.startswith('https://') or not title: continue
                key=hashlib.sha256(link.encode()).hexdigest()[:20]
                if key in seen: continue
                if not any(term in title.lower() for term in ('estate','wagon','avant','tourer','touring','volvo 850','volvo 940')): continue
                if any(term in title.lower() for term in ('breaking','spares','parts only','wheel set','roof rack','model car','toy car')): continue
                year_match=re.search(r'\b(19[789]\d|20[012]\d)\b',title)
                price_match=re.search(r'£\s*([\d,]+)',title)
                price=int(price_match.group(1).replace(',','')) if price_match else None
                data['listings'].append({'id':key,'demo':False,'title':title[:140],'year':int(year_match.group()) if year_match else None,'price':price,'miles':None,'engine':'Verify in advert','location':'UK','type':'estate','score':None,'notes':'Feed discovery — inspect the original advert','found_at':dt.date.today().isoformat(),'url':link})
                seen.add(key);added+=1
        except Exception as exc:
            print('Feed failed:',feed.get('name'),type(exc).__name__,str(exc)[:180])
    if added:
        data['updated']=dt.date.today().isoformat()
        DB.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print('New discoveries:',added,'Configured feeds:',len(feeds))

if __name__=='__main__': main()
