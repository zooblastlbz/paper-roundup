#!/usr/bin/env python3
"""
Generate static HTML reports from JSON data
"""

import json
from datetime import datetime
from pathlib import Path
from html import escape

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"

CSS = """
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #21262d;
    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
    --accent: #58a6ff;
    --accent-hot: #f85149;
    --border: #30363d;
    --radius: 8px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}
header {
    background: var(--bg-secondary);
    padding: 3rem 1rem;
    text-align: center;
    border-bottom: 1px solid var(--border);
}
header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
header p { color: var(--text-secondary); font-size: 1.1rem; }
main { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
section { margin-bottom: 3rem; }
section h2 {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
.stat-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}
.stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    text-align: center;
}
.stat-number { display: block; font-size: 2rem; font-weight: bold; color: var(--accent); }
.stat-label { display: block; color: var(--text-secondary); margin-top: 0.5rem; }
.paper-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: transform 0.2s, border-color 0.2s;
}
.paper-card:hover { transform: translateY(-2px); border-color: var(--accent); }
.paper-card.hot { border-left: 4px solid var(--accent-hot); }
.paper-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    gap: 1rem;
}
.paper-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--accent);
    text-decoration: none;
    flex: 1;
}
.paper-title:hover { text-decoration: underline; }
.paper-badges { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.badge {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
}
.badge.hot { background: var(--accent-hot); color: white; }
.badge.category { background: var(--accent); color: var(--bg-primary); }
.paper-meta {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
}
.paper-summary {
    color: var(--text-primary);
    line-height: 1.7;
}
.paper-keywords {
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}
.keyword {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
}
footer {
    background: var(--bg-secondary);
    border-top: 1px solid var(--border);
    padding: 2rem;
    text-align: center;
    color: var(--text-secondary);
}
footer a { color: var(--accent); text-decoration: none; }
footer a:hover { text-decoration: underline; }
@media (max-width: 768px) {
    header h1 { font-size: 1.8rem; }
    .paper-header { flex-direction: column; }
    .paper-badges { margin-top: 0.5rem; }
}
"""


def generate_html(data, date_str):
    """Generate HTML for a given date"""
    hot_papers = data.get("hot_papers", [])
    interesting_papers = data.get("interesting_papers", [])
    stats = data.get("stats", {})
    
    def render_paper(paper, is_hot=False):
        heat_badge = '<span class="badge hot">🔥 Hot</span>' if is_hot else ''
        cat_badge = f'<span class="badge category">{escape(paper.get("category", "Other"))}</span>' if paper.get("category") else ''
        url = paper.get("url") or f"https://arxiv.org/abs/{paper.get('arxiv_id', '')}"
        arxiv_id = paper.get("arxiv_id", "")
        
        authors = paper.get("authors", [])
        authors_str = ", ".join(authors) if authors else "Unknown"
        
        categories = paper.get("categories", [])
        keywords_html = ''.join(f'<span class="keyword">{escape(c)}</span>' for c in categories[:3])
        
        return f'''
        <div class="paper-card {'hot' if is_hot else ''}">
            <div class="paper-header">
                <a href="{escape(url)}" target="_blank" class="paper-title">{escape(paper.get("title", "Untitled"))}</a>
                <div class="paper-badges">{heat_badge}{cat_badge}</div>
            </div>
            <div class="paper-meta">
                {f"arXiv:{arxiv_id} | " if arxiv_id else ""}
                {escape(authors_str)}
                {f" | {paper.get('published', '')}" if paper.get("published") else ""}
            </div>
            <div class="paper-summary">{escape(paper.get("summary", "No abstract available"))}</div>
            {f'<div class="paper-keywords">{keywords_html}</div>' if keywords_html else ''}
        </div>
        '''
    
    hot_html = ''.join(render_paper(p, True) for p in hot_papers) if hot_papers else '<p style="color:var(--text-secondary);padding:2rem;text-align:center;">No hot papers found</p>'
    interesting_html = ''.join(render_paper(p, False) for p in interesting_papers) if interesting_papers else '<p style="color:var(--text-secondary);padding:2rem;text-align:center;">No papers found</p>'
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paper Roundup - {date_str}</title>
    <style>{CSS}</style>
</head>
<body>
    <header>
        <h1>📚 Paper Roundup</h1>
        <p>Daily AI/ML Papers - {date_str}</p>
    </header>

    <main>
        <section class="stats">
            <h2>📊 Statistics</h2>
            <div class="stat-cards">
                <div class="stat-card">
                    <span class="stat-number">{stats.get("total_papers", 0)}</span>
                    <span class="stat-label">Total Papers</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{stats.get("hot_count", 0)}</span>
                    <span class="stat-label">Hot Papers</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{stats.get("interesting_count", 0)}</span>
                    <span class="stat-label">Interesting</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len(stats.get("categories", {}))}</span>
                    <span class="stat-label">Categories</span>
                </div>
            </div>
        </section>

        <section>
            <h2>🔥 Hot Papers ({len(hot_papers)})</h2>
            <div>{hot_html}</div>
        </section>

        <section>
            <h2>💡 Interesting Papers ({len(interesting_papers)})</h2>
            <div>{interesting_html}</div>
        </section>
    </main>

    <footer>
        <p>Generated on {date_str} | Source: arXiv API | <a href="https://github.com/zooblastlbz/paper-roundup">GitHub</a></p>
    </footer>
</body>
</html>'''
    
    return html


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Find the latest data file
    data_files = sorted(DATA_DIR.glob("*.json"), reverse=True)
    if not data_files:
        print("No data files found")
        return
    
    latest_file = data_files[0]
    date_str = latest_file.stem
    
    print(f"Generating HTML from: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    html = generate_html(data, date_str)
    
    # Save date-specific HTML
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    date_html_path = DOCS_DIR / f"{date_str}.html"
    with open(date_html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {date_html_path}")
    
    # Save as index.html
    index_path = DOCS_DIR / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated: {index_path}")


if __name__ == "__main__":
    main()
