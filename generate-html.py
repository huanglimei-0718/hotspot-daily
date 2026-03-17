#!/usr/bin/env python3
"""
热点日报网页生成器
从JSON数据生成静态HTML页面
"""

import json
import os
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
DOCS_DIR = SCRIPT_DIR / "docs"

# 分类配置
CATEGORIES = {
    "finance": {"name": "财经金融", "icon": "📊", "color": "#10b981"},
    "politics": {"name": "时政要闻", "icon": "🏛️", "color": "#6366f1"},
    "global": {"name": "全球局势", "icon": "🌍", "color": "#f59e0b"},
    "other": {"name": "其他热点", "icon": "📰", "color": "#6b7280"},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日热点简报 - {date}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
        body {{ font-family: 'Noto Sans SC', sans-serif; }}
        .hot-tag {{ animation: pulse 2s infinite; }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .source-badge {{
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 4px;
            background: #e5e7eb;
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="max-w-4xl mx-auto px-4 py-8">
        <!-- Header -->
        <header class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">📰 每日热点简报</h1>
            <p class="text-gray-500">{date} · 自动抓取整理</p>
            <p class="text-xs text-gray-400 mt-1">更新时间: {updated}</p>
        </header>

        <!-- Stats -->
        <div class="grid grid-cols-4 gap-4 mb-8">
            {stats_html}
        </div>

        <!-- Content -->
        {content_html}

        <!-- Footer -->
        <footer class="text-center text-gray-400 text-sm mt-12 pb-8">
            <p>数据来源: 微博热榜 · 百度热搜 · 头条热榜 (Sensight)</p>
            <p class="mt-1">自动抓取 · 智能分类 · 每日更新</p>
        </footer>
    </div>

    <script>
        // 简单的交互
        document.querySelectorAll('.hot-item').forEach(item => {{
            item.addEventListener('click', () => {{
                const url = item.dataset.url;
                if (url) window.open(url, '_blank');
            }});
        }});
    </script>
</body>
</html>
"""

ITEM_TEMPLATE = """
<div class="hot-item flex items-start gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer {cursor_class}" data-url="{url}">
    <span class="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold {rank_class}">{rank}</span>
    <div class="flex-1 min-w-0">
        <p class="text-gray-800 font-medium truncate">{title}</p>
        <p class="text-xs text-gray-400 mt-1">
            <span class="source-badge">{source}</span>
            {hot_value}
        </p>
    </div>
</div>
"""


def load_latest_data():
    """加载最新的热点数据"""
    data_files = sorted(DATA_DIR.glob("hotspots-*.json"), reverse=True)
    if not data_files:
        return None
    
    with open(data_files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def categorize_items(data):
    """按分类整理热点"""
    categories = {cat: [] for cat in CATEGORIES}
    seen_titles = set()
    
    for source_name, items in data.get("sources", {}).items():
        for item in items:
            title = item.get("title", "")
            
            # 去重
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            # 分类
            category = item.get("category", "other")
            if category not in categories:
                category = "other"
            
            categories[category].append({
                **item,
                "source": source_name,
            })
    
    # 每个分类按热度排序，取前10
    for cat in categories:
        categories[cat] = sorted(
            categories[cat], 
            key=lambda x: int(x.get("hot_value", "0").replace("+", "").replace("万", "0000") or "0"),
            reverse=True
        )[:10]
    
    return categories


def generate_stats_html(categories):
    """生成统计卡片"""
    stats = []
    for cat_id, cat_config in CATEGORIES.items():
        count = len(categories.get(cat_id, []))
        stats.append(f"""
        <div class="bg-white rounded-lg p-4 text-center shadow-sm">
            <div class="text-2xl mb-1">{cat_config['icon']}</div>
            <div class="text-2xl font-bold" style="color: {cat_config['color']}">{count}</div>
            <div class="text-xs text-gray-500">{cat_config['name']}</div>
        </div>
        """)
    return "\n".join(stats)


def generate_content_html(categories):
    """生成内容区域HTML"""
    sections = []
    
    for cat_id, cat_config in CATEGORIES.items():
        items = categories.get(cat_id, [])
        if not items:
            continue
        
        items_html = []
        for item in items:
            rank = item.get("rank", "?")
            title = item.get("title", "")
            source = item.get("source", "")
            hot_value = item.get("hot_value", "")
            url = item.get("url", "")
            
            # 热度显示
            hot_text = f"· {hot_value}" if hot_value else ""
            
            # 排名样式
            if rank <= 3:
                rank_class = f"bg-{['red', 'orange', 'yellow'][rank-1]}-500 text-white"
            else:
                rank_class = "bg-gray-200 text-gray-600"
            
            # URL存在才有点击样式
            cursor_class = "hover:bg-gray-50" if url else "opacity-75"
            
            items_html.append(ITEM_TEMPLATE.format(
                rank=rank,
                title=title,
                source=source,
                hot_value=hot_text,
                url=url,
                rank_class=rank_class,
                cursor_class=cursor_class,
            ))
        
        sections.append(f"""
        <section class="mb-8">
            <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
                <span>{cat_config['icon']}</span>
                <span>{cat_config['name']}</span>
                <span class="text-sm font-normal text-gray-400">({len(items)}条)</span>
            </h2>
            <div class="space-y-2">
                {"".join(items_html)}
            </div>
        </section>
        """)
    
    return "\n".join(sections)


def generate_html(data):
    """生成完整HTML"""
    categories = categorize_items(data)
    
    return HTML_TEMPLATE.format(
        date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
        updated=data.get("updated", ""),
        stats_html=generate_stats_html(categories),
        content_html=generate_content_html(categories),
    )


def main():
    """主函数"""
    # 确保输出目录存在
    DOCS_DIR.mkdir(exist_ok=True)
    
    # 加载数据
    data = load_latest_data()
    if not data:
        print("错误: 未找到热点数据，请先运行 fetch-hotspots.sh")
        return 1
    
    # 生成HTML
    html = generate_html(data)
    
    # 写入文件
    output_file = DOCS_DIR / "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"网页已生成: {output_file}")
    return 0


if __name__ == "__main__":
    exit(main())
