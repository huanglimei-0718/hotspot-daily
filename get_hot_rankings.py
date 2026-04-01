#!/usr/bin/env python3
"""
获取三大热榜数据：微博、百度、头条
"""
import json
import re
from datetime import datetime, timezone
import requests
from requests.exceptions import RequestException

# 配置请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://www.baidu.com/'
}

def get_weibo_hot():
    """获取微博热搜"""
    try:
        url = "https://s.weibo.com/top/summary"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = response.apparent_encoding  # 自动识别编码
        
        # 解析热搜列表
        pattern = r'<tr class=\"(?:\w+ )?\".*?><td class=\"td-01\">(\d+)</td><td class=\"td-02\"><a href=\"/weibo\?q=.*?\" target=\"_blank\">(.*?)</a>.*?<span class=\"(?:\w+ )?\">(.*?)</span></td>'
        matches = re.findall(pattern, response.text, re.DOTALL)
        
        hot_list = []
        for rank, title, hot_value in matches[:20]:
            hot_list.append({
                'title': title.strip(),
                'hot_value': hot_value.strip(),
                'source': '微博热搜',
                'rank': int(rank)
            })
        return hot_list
    except RequestException as e:
        print(f"微博热搜获取失败：{str(e)}")
        return []

def get_baidu_hot():
    """获取百度热搜"""
    try:
        url = "https://top.baidu.com/board?tab=realtime"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        # 解析JSON数据
        pattern = r'window\.initialState = (.*?);</script>'
        match = re.search(pattern, response.text)
        
        if match:
            state = json.loads(match.group(1))
            hot_list = []
            for card in state.get('cards', []):
                if 'group' in card:
                    for group in card['group']:
                        for term in group.get('terms', [])[:10]:
                            hot_list.append({
                                'title': term.get('name', '').strip(),
                                'hot_value': f"{term.get('score', 0)/10000:.1f}万",
                                'source': '百度热搜'
                            })
            return hot_list[:20]
        else:
            # 备用解析方案
            pattern = r'<div class=\"c-single-text-ellipsis\">(.*?)</div>.*?<div class=\"hot-index_1Bl1a\">(.*?)</div>'
            matches = re.findall(pattern, response.text)
            hot_list = []
            for title, hot_value in matches[:20]:
                hot_list.append({
                    'title': title.strip(),
                    'hot_value': hot_value.strip(),
                    'source': '百度热搜'
                })
            return hot_list
    except RequestException as e:
        print(f"百度热搜获取失败：{str(e)}")
        return []

def get_toutiao_hot():
    """获取头条热榜"""
    try:
        url = "https://www.toutiao.com/hot-event/hot-board/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        # 解析JSON数据
        pattern = r'window\.pageData = (.*?);'
        match = re.search(pattern, response.text)
        
        if match:
            data = json.loads(match.group(1))
            hot_list = []
            for row in data.get('rows', [])[:20]:
                hot_list.append({
                    'title': row.get('title', '').strip(),
                    'hot_value': f"{row.get('heat', 0)}万",
                    'source': '头条热榜'
                })
            return hot_list
        else:
            # 备用解析方案
            pattern = r'<div class=\"c-single-text-ellipsis\">(.*?)</div>.*?<div class=\"hot-index\">(.*?)</div>'
            matches = re.findall(pattern, response.text)
            hot_list = []
            for title, hot_value in matches[:20]:
                hot_list.append({
                    'title': title.strip(),
                    'hot_value': hot_value.strip(),
                    'source': '头条热榜'
                })
            return hot_list
    except RequestException as e:
        print(f"头条热榜获取失败：{str(e)}")
        return []

def main():
    print("正在获取热榜数据...")
    
    # 获取三个来源的热榜
    weibo_hot = get_weibo_hot()
    baidu_hot = get_baidu_hot()
    toutiao_hot = get_toutiao_hot()
    
    print(f"\n微博热搜：{len(weibo_hot)}条")
    print(f"百度热搜：{len(baidu_hot)}条")
    print(f"头条热榜：{len(toutiao_hot)}条")
    
    # 合并数据
    all_hot = weibo_hot + baidu_hot + toutiao_hot
    
    # 按标题去重（保留热度最高的）
    unique_hot = {}
    for item in all_hot:
        title = item['title'].strip()
        if title and title not in unique_hot:
            unique_hot[title] = item
    
    # 转换为列表并重新编号
    final_list = sorted(unique_hot.values(), key=lambda x: x.get('hot_value', '0'), reverse=True)[:10]
    for i, item in enumerate(final_list):
        item['rank'] = i + 1
    
    # 输出结果
    result = {
        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'updated': datetime.now(timezone.utc).isoformat(),
        'total': len(final_list),
        'items': final_list
    }
    
    print(f"\n去重后共 {len(final_list)} 条热点:")
    for item in final_list:
        print(f"  {item['rank']}. [{item['source']}] {item['title']} ({item['hot_value']})")
    
    # 保存为 JSON
    output_path = '/home/gem/workspace/agent/workspace/hotspot-daily/data/hotspots-raw.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到：{output_path}")
    return result

if __name__ == '__main__':
    main()
