"""Optional public-page discovery for sources whose operators permit crawling.

Never run this against restricted marketplaces. Each source must be explicitly
approved in data/sources.json; robots.txt is checked on every run. No login,
proxy rotation, CAPTCHA solving, or anti-bot circumvention.
"""
import datetime as dt
import hashlib
import html.parser
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
import urllib.robotparser

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'data/sources.json'
DB = ROOT / 'data/listings.json'
AGENT = 'WagonWatchPersonal/0.2 (+public GitHub Pages project; contact repository owner)'
MAX_BYTES = 1_000_000

class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.current=None; self.text=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href'):
            self.current=attrs['href']; self.text=[]
    def handle_data(self, data):
        if self.current is not None: self.text.append(data)
    def handle_endtag(self, tag):
        if tag=='a' and self.current is not None:
            self.links.append((self.current,' '.join(''.join(self.text).split())))
            self.current=None

def fetch(url):
    req=urllib.request.Request(url, headers={'User-Agent':AGENT,'Accept':'text/html'})
    with urllib.request.urlopen(req, timeout=15) as response:
        if 'text/html' not in response.headers.get('Content-Type',''): raise ValueError('Not HTML')
        raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES: raise ValueError('Page too large')
        return raw.decode('utf-8','replace')

def main():
    config=json.loads(SOURCES.read_text())
    data=json.loads(DB.read_text())
    seen={item['id'] for item in data.get('listings',[])}
    added=0
    for source in config.get('sources',[]):
        if not source.get('enabled') or not source.get('permission_confirmed'):
            print('Disabled/unapproved:',source.get('name')); continue
        url=source.get('search_url','')
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='https' or not parsed.hostname: continue
        robots_url=f'{parsed.scheme}://{parsed.netloc}/robots.txt'
        robots=urllib.robotparser.RobotFileParser()
        try:
            robots.set_url(robots_url); robots.read()
            if not robots.can_fetch(AGENT,url):
                print('Robots disallow:',source['name']); continue
            page=fetch(url)
            links=Links(); links.feed(page)
            host=parsed.hostname
            allowed_path=source.get('listing_path_contains','')
            for href,title in links.links:
                dest=urllib.parse.urljoin(url,href)
                d=urllib.parse.urlsplit(dest)
                if d.scheme!='https' or d.hostname!=host: continue
                if allowed_path and allowed_path not in d.path: continue
                if not robots.can_fetch(AGENT,dest): continue
                if not any(x in title.lower() for x in ('estate','wagon','avant','tourer','touring')): continue
                if any(x in title.lower() for x in ('parts','breaking','roof rack','toy','spares')): continue
                key=hashlib.sha256(dest.encode()).hexdigest()[:20]
                if key in seen: continue
                year=re.search(r'\b(19[789]\d|20[012]\d)\b',title)
                price=re.search(r'£\s*([\d,]+)',title)
                data.setdefault('listings',[]).append({'id':key,'demo':False,'title':title[:140],
                    'year':int(year.group()) if year else None,
                    'price':int(price.group(1).replace(',','')) if price else None,
                    'miles':None,'engine':'Check original advert','location':'UK',
                    'type':'estate','score':None,'notes':'Public listing link; details unverified',
                    'found_at':dt.date.today().isoformat(),'url':dest,'source':source['name']})
                seen.add(key); added+=1
            time.sleep(3)
        except Exception as exc:
            print('Source failed:',source.get('name'),type(exc).__name__,str(exc)[:150])
    if added:
        data['updated']=dt.date.today().isoformat()
        DB.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('New public-page discoveries:',added)

if __name__=='__main__': main()
