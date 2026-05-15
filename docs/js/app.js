// Paper Roundup Web App
const DATA_URL = 'https://raw.githubusercontent.com/zooblastlbz/paper-roundup/main/data/';

async function loadPapers() {
    const latestContainer = document.getElementById('latest-papers');
    const archiveContainer = document.getElementById('archive-list');
    const statsContainer = document.getElementById('stats-container');
    
    latestContainer.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        // 获取数据文件列表 (从 GitHub API 或尝试常见日期)
        const dates = getRecentDates(30);
        const papers = [];
        
        for (const date of dates) {
            try {
                const response = await fetch(`${DATA_URL}${date}.json`);
                if (response.ok) {
                    const data = await response.json();
                    papers.push({ date, data });
                }
            } catch (e) {
                // 文件不存在，跳过
            }
        }
        
        if (papers.length === 0) {
            latestContainer.innerHTML = '<div class="loading">暂无数据</div>';
            return;
        }
        
        // 更新统计
        updateStats(papers);
        
        // 显示最新论文
        const latest = papers[0];
        latestContainer.innerHTML = renderPapers(latest.data);
        
        // 显示历史归档
        archiveContainer.innerHTML = papers.map(p => `
            <div class="archive-item" onclick="loadDate('${p.date}')">
                <span class="archive-date">${p.date}</span>
                <span class="archive-count">${p.data.hot_papers?.length || 0} 篇热榜论文</span>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading papers:', error);
        latestContainer.innerHTML = '<div class="loading">加载失败，请刷新重试</div>';
    }
}

function getRecentDates(days) {
    const dates = [];
    for (let i = 0; i < days; i++) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        dates.push(d.toISOString().split('T')[0]);
    }
    return dates;
}

function updateStats(papers) {
    const totalPapers = papers.reduce((sum, p) => 
        sum + (p.data.hot_papers?.length || 0) + (p.data.interesting_papers?.length || 0), 0);
    
    document.getElementById('total-papers').textContent = totalPapers;
    document.getElementById('total-days').textContent = papers.length;
    document.getElementById('last-update').textContent = papers[0]?.date || '-';
}

function renderPapers(data) {
    const hotPapers = data.hot_papers || [];
    const interestingPapers = data.interesting_papers || [];
    
    let html = '';
    
    // 热榜论文
    if (hotPapers.length > 0) {
        html += '<h3>🔥 热榜论文</h3>';
        html += hotPapers.map(paper => renderPaperCard(paper, true)).join('');
    }
    
    // 有趣论文
    if (interestingPapers.length > 0) {
        html += '<h3>💡 有趣论文</h3>';
        html += interestingPapers.map(paper => renderPaperCard(paper, false)).join('');
    }
    
    return html || '<div class="loading">暂无论文数据</div>';
}

function renderPaperCard(paper, isHot) {
    const heatBadge = isHot ? '<span class="badge hot">🔥 热榜</span>' : '';
    const categoryBadge = paper.category ? `<span class="badge category">${paper.category}</span>` : '';
    const arxivLink = paper.arxiv_id ? `https://arxiv.org/abs/${paper.arxiv_id}` : (paper.url || '#');
    
    const keywords = (paper.keywords || []).map(k => `<span class="keyword">${k}</span>`).join('');
    
    return `
        <div class="paper-card ${isHot ? 'hot' : ''}">
            <div class="paper-header">
                <a href="${arxivLink}" target="_blank" class="paper-title">${paper.title}</a>
                <div class="paper-badges">
                    ${heatBadge}
                    ${categoryBadge}
                </div>
            </div>
            <div class="paper-meta">
                ${paper.authors || '未知作者'} ${paper.venue ? `| ${paper.venue}` : ''}
            </div>
            <div class="paper-summary">${paper.summary || '暂无摘要'}</div>
            ${keywords ? `<div class="paper-keywords">${keywords}</div>` : ''}
        </div>
    `;
}

async function loadDate(date) {
    const latestContainer = document.getElementById('latest-papers');
    latestContainer.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        const response = await fetch(`${DATA_URL}${date}.json`);
        if (response.ok) {
            const data = await response.json();
            latestContainer.innerHTML = `<h3>📅 ${date} 的论文</h3>` + renderPapers(data);
        }
    } catch (e) {
        latestContainer.innerHTML = '<div class="loading">加载失败</div>';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', loadPapers);
