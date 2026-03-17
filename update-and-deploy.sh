#!/bin/bash
# 一键更新热点并部署
# 用法: ./update-and-deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 抓取今日热点..."
bash scripts/fetch-hotspots.sh

# 复制数据到docs目录
TODAY=$(date +"%Y-%m-%d")
cp "data/hotspots-$TODAY.json" "docs/data/"

echo "📦 提交到Git..."
git add .
git commit -m "更新热点: $TODAY" || echo "无变更"

echo "🚀 推送到GitHub..."
git push origin master

echo "✅ 完成！访问你的 GitHub Pages 查看更新"
