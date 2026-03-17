# 每日热点简报

自动抓取微博、百度、头条热榜，按财经金融、时政要闻、全球局势分类展示。

## 目录结构

```
hotspot-daily/
├── docs/                    # GitHub Pages 根目录
│   ├── index.html          # 网页
│   └── data/               # 热点数据
│       └── hotspots-YYYY-MM-DD.json
├── scripts/
│   └── fetch-hotspots.sh   # 抓取脚本
├── update-and-deploy.sh    # 一键更新部署
└── README.md
```

## 使用方法

### 1. 手动更新
```bash
./update-and-deploy.sh
```

### 2. 自动更新（Cron定时任务）
每天早上8点自动抓取：
```bash
# 编辑crontab
crontab -e

# 添加一行
0 8 * * * cd /path/to/hotspot-daily && ./update-and-deploy.sh >> logs/cron.log 2>&1
```

## 数据来源

- 微博热榜
- 百度热搜  
- 头条热榜

数据来自 Sensight 平台。

## 分类规则

### 💰 财经金融
股市、A股、港股、美股、基金、金融、银行、央行、利率、经济、GDP、通胀、财经、证券、期货、比特币、加密、投资、融资、上市、财报等

### 🏛️ 时政要闻
政策、国务院、两会、人大、政协、政府、中央、部委、改革、立法、法规、纪委、反腐、巡视、干部、任命、选举等

### 🌍 全球局势
美国、俄罗斯、乌克兰、欧盟、日本、韩国、朝鲜、中东、以色列、巴勒斯坦、伊朗、欧洲、北约、联合国、关税、制裁、贸易战、外交、战争、冲突等

---

🦞 由槑头脑特工4号自动生成
