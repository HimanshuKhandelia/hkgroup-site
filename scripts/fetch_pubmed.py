#!/usr/bin/env python3
"""Generate _generated/publications.md from PubMed using NCBI E-utilities."""
from __future__ import annotations
import html
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

TERM = 'Khandelia H[Author]'
BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
OUT = Path(__file__).resolve().parents[1] / '_generated' / 'publications.md'
UA = 'hkgroup-sdu-website/1.0 (contact: hkhandel@sdu.dk)'


def get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def text(node, path, default=''):
    x = node.find(path)
    return ''.join(x.itertext()).strip() if x is not None else default


def clean(s: str) -> str:
    s = html.unescape(re.sub(r'<[^>]+>', '', s or ''))
    return re.sub(r'\s+', ' ', s).strip()


def main():
    q = urllib.parse.urlencode({'db':'pubmed','term':TERM,'retmax':500,'sort':'pub date','retmode':'xml'})
    root = ET.fromstring(get(BASE + 'esearch.fcgi?' + q))
    ids = [x.text for x in root.findall('.//IdList/Id') if x.text]
    if not ids:
        raise RuntimeError('No PubMed records found')

    by_year = defaultdict(list)
    for start in range(0, len(ids), 100):
        batch = ids[start:start+100]
        q = urllib.parse.urlencode({'db':'pubmed','id':','.join(batch),'retmode':'xml'})
        data = ET.fromstring(get(BASE + 'efetch.fcgi?' + q))
        for art in data.findall('.//PubmedArticle'):
            citation = art.find('./MedlineCitation')
            article = citation.find('./Article') if citation is not None else None
            if article is None:
                continue
            pmid = text(citation, './PMID')
            title = clean(text(article, './ArticleTitle'))
            journal = clean(text(article, './Journal/Title'))
            year = text(article, './Journal/JournalIssue/PubDate/Year')
            if not year:
                med = text(article, './Journal/JournalIssue/PubDate/MedlineDate')
                m = re.search(r'(19|20)\d{2}', med)
                year = m.group(0) if m else 'Undated'
            authors=[]
            for a in article.findall('./AuthorList/Author'):
                collective=text(a,'./CollectiveName')
                if collective:
                    authors.append(collective); continue
                last=text(a,'./LastName'); initials=text(a,'./Initials')
                if last: authors.append(f'{last} {initials}'.strip())
            doi=''
            for aid in art.findall('./PubmedData/ArticleIdList/ArticleId'):
                if aid.attrib.get('IdType') == 'doi' and aid.text:
                    doi=aid.text.strip(); break
            by_year[year].append((title, authors, journal, pmid, doi))
        time.sleep(.35)

    lines=['## Publication list','']
    years=sorted(by_year, key=lambda y: (y=='Undated', -(int(y) if y.isdigit() else 0)))
    for year in years:
        lines += [f'### {year}','']
        for title,authors,journal,pmid,doi in by_year[year]:
            title=title.replace('[','\\[').replace(']','\\]')
            auth=', '.join(authors)
            if len(auth) > 220:
                auth = ', '.join(authors[:8]) + ', et al.'
            link=f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
            doi_txt=f' · [DOI](https://doi.org/{doi})' if doi else ''
            lines.append(f'- **[{title}]({link})**  ')
            lines.append(f'  {auth}. *{journal}*.{doi_txt}')
        lines.append('')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {OUT} with {len(ids)} PubMed records')

if __name__ == '__main__':
    main()
