# 📚 Paper Roundup

每日 AI/ML 论文精选与汇总工具。

## 🌐 在线访问

**网页版：** https://zooblastlbz.github.io/paper-roundup/

## 📁 目录结构

```
paper-roundup/
├── .github/workflows/    # GitHub Actions (自动部署)
├── data/                 # 每日论文数据 (JSON)
├── docs/                 # GitHub Pages 网站
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── scripts/              # 工具脚本
│   ├── daily_task.py     # 每日任务主脚本
│   └── generate_report.py # 报告生成
└── README.md
```

## 🔄 自动更新

- **定时任务**：每天上午 9:00 自动执行
- **数据来源**：arXiv API + Hugging Face Papers
- **自动推送**：生成数据后自动推送到 GitHub
- **网页部署**：通过 GitHub Pages 自动部署

## 📊 关注领域

1. **多模态大语言模型** (Multimodal LLM)
2. **Agentic AI** - 智能体、工具使用、规划推理
3. **模型后训练** - DPO、RL、SFT改进
4. **世界模型** (World Models)
5. **视觉生成模型** - 图像/视频生成、扩散模型

## 🚀 快速开始

```bash
# 运行每日任务
python scripts/daily_task.py

# 生成报告
python scripts/generate_report.py

# 手动推送
git add -A && git commit -m "update" && git push origin main
```

---

自动生成于每日 9:00 | [GitHub](https://github.com/zooblastlbz/paper-roundup)
