#!/bin/bash

# 获取微博热榜 (ranking_id: 12549)
echo "获取微博热榜..."
curl -s -X POST https://llmlink.bytedance.net/trendflow/tool/get_event_board \
  -H "Content-Type: application/json" \
  -H "x-source: sensight-skill" \
  -H "x-skill-version: 0.2.0" \
  -d '{"ranking_id": "12549"}' > /tmp/weibo.json

# 获取百度热搜 (ranking_id: 24847)
echo "获取百度热搜..."
curl -s -X POST https://llmlink.bytedance.net/trendflow/tool/get_event_board \
  -H "Content-Type: application/json" \
  -H "x-source: sensight-skill" \
  -H "x-skill-version: 0.2.0" \
  -d '{"ranking_id": "24847"}' > /tmp/baidu.json

# 获取头条热榜 (ranking_id: 4071)
echo "获取头条热榜..."
curl -s -X POST https://llmlink.bytedance.net/trendflow/tool/get_event_board \
  -H "Content-Type: application/json" \
  -H "x-source: sensight-skill" \
  -H "x-skill-version: 0.2.0" \
  -d '{"ranking_id": "4071"}' > /tmp/toutiao.json

echo "完成！"
ls -la /tmp/*.json
