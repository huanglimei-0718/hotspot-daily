#!/bin/bash
# 生成热点日报（由Agent调用）
# 用法: bash generate-report.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TODAY=$(date +"%Y-%m-%d")

cd "$PROJECT_DIR"

echo "📊 开始生成 $TODAY 热点日报..."

# 1. 调用sensight获取热点（这里需要Agent手动调用skill）
# 脚本只负责生成HTML，数据由Agent提供

# 2. 检查数据文件是否存在
DATA_FILE="docs/data/hotspots-$TODAY.json"
if [ ! -f "$DATA_FILE" ]; then
  echo "❌ 错误: 找不到今日数据文件 $DATA_FILE"
  exit 1
fi

# 3. 验证JSON格式
if ! jq empty "$DATA_FILE" 2>/dev/null; then
  echo "❌ 错误: JSON格式无效"
  exit 1
fi

echo "✅ 数据文件就绪"

# 4. Git提交和推送
git add .
git commit -m "更新热点日报: $TODAY" || echo "无变更需要提交"
git push origin main || git push origin master

echo "✅ 日报已推送至GitHub Pages"
