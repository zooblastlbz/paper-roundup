#!/usr/bin/env python3
"""
Fetch papers from arXiv API
运行在 GitHub Actions 上，无网络限制
"""

import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# arXiv API endpoint
ARXIV_API = "http://export.arxiv.org/api/query"

# 搜索配置: (query, category_name)
SEARCH_QUERIES = [
    ("cat:cs.CV AND (multimodal OR vision-language) AND submittedDate:[{date}-0000 TO {date}-2359]", "Multimodal LLM"),
    ("cat:cs.AI AND (agent OR tool-use OR reasoning) AND submittedDate:[{date}-0000 TO {date}-2359]", "Agentic AI"),
    ("cat:cs.LG AND (DPO OR RLHF OR preference OR alignment) AND submittedDate:[{date}-0000 TO {date}-2359]", "Post-Training"),
    ("cat:cs.LG AND (world-model OR latent-dynamics) AND submittedDate:[{date}-0000 TO {date}-2359]", "World Model"),
    ("cat:cs.CV AND (diffusion OR video-generation) AND submittedDate:[{date}-0000 TO {date}-2359]", "Visual Generation"),
]


def fetch_arxiv_papers(query, max_results=10):
    """从 arXiv API 获取论文"""
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    try:
        response = requests.get(ARXIV_API, params=params, timeout=60)
        response.raise_for_status()
        return parse_arxiv_response(response.text)
    except Exception as e:
        print(f"  Error fetching arXiv: {e}")
        return []


def parse_arxiv_response(xml_content):
    """解析 arXiv API XML 响应"""
    papers = []
    
    # Register namespaces
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    root = ET.fromstring(xml_content)
    
    for entry in root.findall('.//atom:entry', ns):
        paper = {}
        
        # Title
        title_elem = entry.find('atom:title', ns)
        paper['title'] = title_elem.text.strip() if title_elem is not None else "No Title"
        
        # arXiv ID
        id_elem = entry.find('atom:id', ns)
        if id_elem is not None:
            arxiv_url = id_elem.text.strip()
            # Extract ID from URL like http://arxiv.org/abs/2501.12345
            paper['arxiv_id'] = arxiv_url.split('/')[-1]
            paper['url'] = arxiv_url
        
        # Summary/Abstract
        summary_elem = entry.find('atom:summary', ns)
        summary = summary_elem.text.strip() if summary_elem is not None else ""
        # Limit summary length
        if len(summary) > 500:
            summary = summary[:497] + "..."
        paper['summary'] = summary
        
        # Authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name_elem = author.find('atom:name', ns)
            if name_elem is not None:
                authors.append(name_elem.text.strip())
        paper['authors'] = authors[:3]  # First 3 authors
        if len(authors) > 3:
            paper['authors'].append("et al.")
        
        # Published date
        published_elem = entry.find('atom:published', ns)
        if published_elem is not None:
            paper['published'] = published_elem.text[:10]  # YYYY-MM-DD
        
        # Primary category
        cat_elem = entry.find('arxiv:primary_category', ns)
        if cat_elem is not None:
            paper['primary_category'] = cat_elem.get('term', '')
        
        # Categories
        categories = []
        for cat in entry.findall('atom:category', ns):
            term = cat.get('term', '')
            if term:
                categories.append(term)
        paper['categories'] = categories
        
        paper['source'] = 'arxiv'
        papers.append(paper)
    
    return papers


def categorize_and_save(all_papers, today):
    """分类论文并保存"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Deduplicate by arxiv_id
    seen_ids = set()
    unique_papers = []
    for p in all_papers:
        arxiv_id = p.get('arxiv_id', '')
        if arxiv_id and arxiv_id not in seen_ids:
            seen_ids.add(arxiv_id)
            unique_papers.append(p)
    
    # Sort by date
    unique_papers.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    # Split into hot and interesting
    hot_papers = unique_papers[:6]
    interesting_papers = unique_papers[6:14]
    
    for p in hot_papers:
        p['heat'] = 'trending'
    
    # Calculate category stats
    category_stats = {}
    for p in unique_papers:
        cat = p.get('search_category', 'Other')
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    data = {
        "date": today,
        "sources": {
            "arxiv": {
                "status": "success",
                "note": f"Fetched {len(unique_papers)} papers from arXiv API"
            }
        },
        "stats": {
            "search_method": "arXiv API",
            "categories": category_stats,
            "total_papers": len(hot_papers) + len(interesting_papers),
            "hot_count": len(hot_papers),
            "interesting_count": len(interesting_papers),
            "unique_papers": len(unique_papers)
        },
        "hot_papers": hot_papers,
        "interesting_papers": interesting_papers
    }
    
    # Save
    data_path = DATA_DIR / f"{today}.json"
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Saved: {data_path}")
    return data


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"\n{'='*60}")
    print(f"📚 Fetching arXiv Papers - {today}")
    print(f"{'='*60}\n")
    
    all_papers = []
    
    for query_template, category in SEARCH_QUERIES:
        query = query_template.format(date=yesterday)
        print(f"🔍 Searching: {category}")
        print(f"   Query: {query[:60]}...")
        
        papers = fetch_arxiv_papers(query, max_results=10)
        print(f"   Found: {len(papers)} papers")
        
        for p in papers:
            p['search_category'] = category
            p['category'] = category
        
        all_papers.extend(papers)
    
    print(f"\n📊 Total papers before dedup: {len(all_papers)}")
    
    if all_papers:
        data = categorize_and_save(all_papers, today)
        print(f"\n✅ Done!")
        print(f"   Hot papers: {data['stats']['hot_count']}")
        print(f"   Interesting papers: {data['stats']['interesting_count']}")
    else:
        print("\n⚠️ No papers found")


if __name__ == "__main__":
    main()
