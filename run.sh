#!/bin/bash
# 一键运行: 抓取热点 + 生成网页

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔍 抓取热点数据..."
bash "$SCRIPT_DIR/fetch-hotspots.sh"

echo ""
echo "📄 生成网页..."
python3 "$SCRIPT_DIR/generate-html.py"

echo ""
echo "✅ 完成！"
echo "📁 网页位置: $SCRIPT_DIR/docs/index.html"
