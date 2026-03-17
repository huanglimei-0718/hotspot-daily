#!/bin/bash
# 每日热点抓取脚本 (优化版)
# 输出: data/hotspots-YYYY-MM-DD.json

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$(dirname "$SCRIPT_DIR")/data"
TODAY=$(date +"%Y-%m-%d")
OUTPUT_FILE="$DATA_DIR/hotspots-$TODAY.json"

mkdir -p "$DATA_DIR"

# 热榜源配置 (ID:名称)
SOURCES=(
  "12549:微博热榜"
  "24847:百度热搜"
  "4071:头条热榜"
)

# 分类关键词
FINANCE_KW="股市 A股 港股 美股 基金 金融 银行 央行 利率 经济 GDP 通胀 财经 证券 期货 比特币 加密 投资 融资 上市 财报 理财 债券 外汇 人民币 美元 汇率"
POLITICS_KW="政策 国务院 两会 人大 政协 政府 中央 部委 省委 市委 改革 立法 法规 纪委 反腐 巡视 干部 任命 选举 会议 视察 讲话 批示"
GLOBAL_KW="美国 俄罗斯 乌克兰 欧盟 日本 韩国 朝鲜 中东 以色列 巴勒斯坦 伊朗 欧洲 北约 联合国 关税 制裁 贸易战 外交 访问 会谈 峰会 G7 G20 APEC 战争 冲突 边境 领土 国际 海外"
ENTERTAINMENT_KW="明星 演员 歌手 电影 电视剧 综艺 娱乐 八卦 颜值 恋爱 结婚 离婚 绯闻 网红 直播 抖音 微博热搜 偶像 爱豆 粉丝 CP 豆瓣 影视 音乐 演唱会 综艺节目 真人秀 明星八卦 爆料"

# 分类函数
categorize() {
  local title="$1"
  
  # 先检查娱乐八卦（优先级最高，避免被其他分类覆盖）
  for kw in $ENTERTAINMENT_KW; do
    [[ "$title" == *"$kw"* ]] && echo "entertainment" && return
  done
  
  for kw in $FINANCE_KW; do
    [[ "$title" == *"$kw"* ]] && echo "finance" && return
  done
  
  for kw in $POLITICS_KW; do
    [[ "$title" == *"$kw"* ]] && echo "politics" && return
  done
  
  for kw in $GLOBAL_KW; do
    [[ "$title" == *"$kw"* ]] && echo "global" && return
  done
  
  echo "other"
}

# 抓取单个热榜 (带超时)
fetch_board() {
  local ranking_id=$1
  
  curl -s --max-time 10 -X POST https://llmlink.bytedance.net/trendflow/tool/get_event_board \
    -H "Content-Type: application/json" \
    -H "x-source: sensight-skill" \
    -H "x-skill-version: 0.2.0" \
    -d "{\"ranking_id\": \"$ranking_id\"}" 2>/dev/null || echo '{}'
}

# 主函数
main() {
  echo "抓取热点数据: $TODAY" >&2
  
  # 临时存储
  declare -A ALL_ITEMS
  
  for source in "${SOURCES[@]}"; do
    IFS=':' read -r ranking_id source_name <<< "$source"
    echo "  抓取: $source_name" >&2
    
    response=$(fetch_board "$ranking_id")
    
    # 解析热点
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      
      title=$(echo "$line" | cut -d'|' -f1)
      rank=$(echo "$line" | cut -d'|' -f2)
      hot_value=$(echo "$line" | cut -d'|' -f3)
      
      [ -z "$title" ] && continue
      
      category=$(categorize "$title")
      
      # 存储到数组 (用标题去重)
      ALL_ITEMS["$title"]="$source_name|$rank|$hot_value|$category"
    done < <(echo "$response" | jq -r '.data.items[]? | "\(.title)|\(.rank)|\(.hot_value // "")"' 2>/dev/null || true)
  done
  
  # 输出JSON
  echo "{" > "$OUTPUT_FILE"
  echo "  \"date\": \"$TODAY\"," >> "$OUTPUT_FILE"
  echo "  \"updated\": \"$(date -Iseconds)\"," >> "$OUTPUT_FILE"
  echo "  \"total\": ${#ALL_ITEMS[@]}," >> "$OUTPUT_FILE"
  echo "  \"items\": [" >> "$OUTPUT_FILE"
  
  first=true
  for title in "${!ALL_ITEMS[@]}"; do
    IFS='|' read -r source rank hot_value category <<< "${ALL_ITEMS[$title]}"
    
    [ "$first" = true ] && first=false || echo "," >> "$OUTPUT_FILE"
    
    printf '    {"title": "%s", "source": "%s", "rank": %s, "hot_value": "%s", "category": "%s"}' \
      "$(echo "$title" | sed 's/"/\\"/g')" \
      "$source" \
      "${rank:-0}" \
      "$hot_value" \
      "$category" \
      >> "$OUTPUT_FILE"
  done
  
  echo "" >> "$OUTPUT_FILE"
  echo "  ]" >> "$OUTPUT_FILE"
  echo "}" >> "$OUTPUT_FILE"
  
  echo "✅ 已保存 ${#ALL_ITEMS[@]} 条热点: $OUTPUT_FILE" >&2
}

main
