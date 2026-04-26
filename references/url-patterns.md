# URL 规律文档 (URL Patterns)

各信息源的 URL 构造规律与搜索策略。

## 一、Sportsmole

### Preview 文章 URL 规律

```
https://www.sportsmole.co.uk/football/{team-slug}/preview-{team-a}-vs-{team-b}-prediction-team-news-lineups_{article_id}.html
```

- `{team-slug}`: 球队在 Sportsmole 上的 URL slug（如 `bayern-munich`、`werder-bremen`）
- `{article_id}`: 文章数字 ID（6 位数字）

### 搜索策略

1. **直接构造**：根据 team-slug 尝试构造 URL，成功率约 70%
2. **搜索引擎定位**：`site:sportsmole.co.uk "{team_a}" "{team_b}" preview`
3. **球队专栏浏览**：`https://www.sportsmole.co.uk/football/{team-slug}/` 列出最近文章

### DOM 提取选择器

| 内容 | CSS 选择器 |
| :--- | :--- |
| 文章正文 | `div[itemprop="articleBody"]` 或 `div.article_body` |
| Team News 段落 | 搜索含 "Team News" 标题后的段落 |
| Possible Lineups | 搜索含 "Possible Lineups" 标题后的内容 |
| H2H 记录 | 搜索含 "Head-to-Head" 标题后的段落 |
| Prediction | 搜索含 "Prediction" 标题后的段落 |

### 常见 team-slug 映射

| 球队 | slug |
| :--- | :--- |
| 拜仁慕尼黑 | `bayern-munich` |
| 多特蒙德 | `borussia-dortmund` |
| 巴塞罗那 | `barcelona` |
| 皇家马德里 | `real-madrid` |
| 云达不莱梅 | `werder-bremen` |
| 斯图加特 | `stuttgart` |
| 柏林联合 | `union-berlin` |
| 霍芬海姆 | `hoffenheim` |
| 法兰克福 | `eintracht-frankfurt` |
| 门兴 | `borussia-monchengladbach` |
| 圣保利 | `st-pauli` |
| 科隆 | `koln` |
| 奥格斯堡 | `fc-augsburg` |
| 波鸿 | `bochum` |
| 美因茨 | `mainz` |
| RB莱比锡 | `rb-leipzig` |
| 塞维利亚 | `sevilla` |
| 利雅得胜利 | `al-nassr` |

## 二、WhoScored

### 球队页面 URL 规律

```
https://www.whoscored.com/Teams/{team_id}/Show/{country}-{team-name}
```

- `{team_id}`: 数字 ID（如拜仁 32，巴萨 65）
- 示例：`https://www.whoscored.com/Teams/32/Show/Germany-Bayern-Munich`

### 球员页面 URL 规律

```
https://www.whoscored.com/Players/{player_id}/Show/{country}-{player-name}
```

### 搜索策略

1. **搜索引擎定位**：`site:whoscored.com "{team_name}" team`
2. **从 Sportsmole/Transfermarkt 页面中的 WhoScored 链接提取 ID**

### DOM 提取选择器

| 内容 | CSS 选择器 |
| :--- | :--- |
| 球队风格 | `div.team-style-grid` 或 API 返回 JSON |
| 球员 strengths | `div.player-strengths li` |
| 球员 weaknesses | `div.player-weaknesses li` |
| 阵型信息 | `div.formation-grid` |

### 注意事项

- WhoScored 大量使用 AJAX 加载，纯 HTML 爬取可能拿不到完整数据
- 建议使用 CDP 浏览器模式或搜索其隐藏 API（`/Statistics` 端点返回 JSON）
- 反爬较严格，需控制请求频率（建议 3-5 秒间隔）

## 三、风驰直播 (fczhibo.net)

### 比赛页面 URL 规律

```
https://www.fczhibo.net/live/{league-slug}/{match_id}.html
```

- `{league-slug}`: 联赛 slug（如 `yingchao`、`xijia`、`dejia`）
- `{match_id}`: 比赛数字 ID

### 联赛 slug 映射

| 联赛 | slug |
| :--- | :--- |
| 英超 | `yingchao` |
| 西甲 | `xijia` |
| 德甲 | `dejia` |
| 意甲 | `yijia` |
| 法甲 | `fajia` |
| 欧冠 | `ouguan` |
| 欧联 | `oulian` |

### 搜索策略

1. **站内搜索**：`https://www.fczhibo.net/search?kw={team_name}`
2. **联赛列表页**：`https://www.fczhibo.net/{league-slug}/` 浏览近期比赛
3. **搜索引擎**：`site:fczhibo.net "{team_a}" "{team_b}"`

### DOM 提取选择器

| 内容 | CSS 选择器 |
| :--- | :--- |
| 直播前瞻文本 | 搜索含"直播前瞻"的 div 段落 |
| 比赛统计 | `div.team-stats` 内的表格 |
| 首发阵容 | `div.lineup` 内的球员列表 |
| 预期进球(xG) | 统计表中"预期进球"行 |

### 风驰直播特殊优势

- 前瞻段落是中文语境下最完整的赛前文本
- 包含积分形势、射手榜、近6场战绩拆解（主客场胜率、场均得失球）
- 比赛统计含 xG、危险进攻、传中成功率等进阶数据

## 四、Transfermarkt

### 页面 URL 规律

```
# 球员
https://www.transfermarkt.com/{player-slug}/profil/spieler/{player_id}

# 教练
https://www.transfermarkt.com/{coach-slug}/profil/trainer/{coach_id}

# 裁判
https://www.transfermarkt.com/{referee-slug}/profil/schiedsrichter/{referee_id}

# 俱乐部
https://www.transfermarkt.com/{club-slug}/startseite/verein/{club_id}

# 联赛积分榜
https://www.transfermarkt.com/{league-slug}/tabelle/wettbewerb/{league_id}
```

### ceapi 端点（无需认证，返回 JSON）

```
# 球员身价曲线
GET https://www.transfermarkt.com/ceapi/marketValueDevelopment/graph/{player_id}

# 球员转会记录
GET https://www.transfermarkt.com/ceapi/transferHistory/list/{player_id}
```

### 搜索策略

1. **站内搜索**：`https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={team_name}`
2. **transfermarkt-wrapper (Python)**：
   ```python
   from transfermarkt_wrapper import Player, Club, Coach
   player = Player(player_id=28003)  # Messi
   profile = player.profile()
   ```
3. **transfermarkt_api_client (Node.js)**：
   ```javascript
   import { playerProfile, coachProfile, refereeProfile } from './src/services/index.js';
   const profile = await playerProfile(28003);
   ```

### ID 获取方式

1. 从搜索结果页面提取
2. 从其他网站（Sportsmole/WhoScored）页面中的 Transfermarkt 链接提取
3. 缓存已知 ID 映射

## 五、El Futbolero (elfutbolero.us)

### Preview 文章 URL 规律

```
https://www.elfutbolero.us/news/{slug}-{YYYYMMDD}-{id}.html
```

- `{slug}`: kebab-case 标题，含球队名、联赛名、关键词（preview/match/broadcast-guide/viewing-guide）
- `{YYYYMMDD}`: 发布日期
- `{id}`: 5 位数字 ID

**URL 示例**：
- `https://www.elfutbolero.us/news/al-hilal-vs-al-nassr-preview-and-viewing-guide-saudi-pro-league-2024-25-matchday-26-20250403-49998.html`
- `https://www.elfutbolero.us/news/how-to-watch-inter-miami-vs-new-york-red-bulls-mls-2025-match-preview-20250503-50323.html`
- `https://www.elfutbolero.us/news/al-qadisiya-vs-al-nassr-saudi-pro-league-2024-25-matchday-28-broadcast-guide-and-preview-20250417-50167.html`

### 分类页 URL

| 分类 | URL | 分页 |
| :--- | :--- | :--- |
| MLS | `https://www.elfutbolero.us/mls` | `?page=N` |
| 新闻 | `https://www.elfutbolero.us/news` | - |
| 英超 | `https://www.elfutbolero.us/premier-league` | `?page=N` |
| 欧冠 | `https://www.elfutbolero.us/champions-league` | `?page=N` |

### 搜索策略

1. **站内搜索（推荐）**：`https://www.elfutbolero.us/search?q={team_a}+{team_b}+preview`
   - 返回 `<article>` 卡片列表，含标题和链接
   - 搜索结果精确度高，直接匹配球队名
2. **搜索引擎定位**：`site:elfutbolero.us "{team_a}" "{team_b}" preview`
3. **分类页浏览**：`/mls` 或 `/premier-league` 浏览近期文章

### DOM 提取选择器

| 内容 | CSS 选择器 | 说明 |
| :--- | :--- | :--- |
| 文章正文容器 | `article div.prose` | Tailwind Typography 样式的正文区 |
| 章节标题 | `div.article-header` | 文章内的分节标题 |
| 列表内容（阵容/转播） | `ul.article-list` | 含预测阵容、转播信息 |
| 广告（需过滤） | `div.article-ad.not-prose` | 广告占位 |
| 推荐文章（需过滤） | `div.not-prose`（含"Recommended"） | 推荐文章卡片 |
| JSON-LD 全文 | `script[type="application/ld+json"]` → `articleBody` | 纯文本全文，4k+ 字符 |
| JSON-LD 标题 | 同上 → `headline` | 文章标题 |
| JSON-LD 关键词 | 同上 → `keywords` | 标签数组，如 `["Al Nassr", "Cristiano Ronaldo"]` |
| JSON-LD 日期 | 同上 → `datePublished` | ISO 8601 格式 |
| 搜索结果卡片 | `article` > `a[href*="/news/"]` | 搜索页/列表页的文章卡片 |

### 技术特征

- **框架**：Astro SSG（静态站点生成），HTML 直出，无 JS 渲染依赖
- **反爬**：无 Cloudflare，无频率限制，纯 curl 可直接获取 200
- **建议限速**：2-3 秒间隔（礼貌性限速）
- **JSON-LD 优先**：`articleBody` 字段提供纯文本全文，可直接提取，无需解析 HTML DOM

### 提取策略（优先级）

1. **JSON-LD 提取（推荐）**：从 `script[type="application/ld+json"]` 获取 `articleBody`，纯文本，无 HTML 标签干扰
2. **DOM 提取（补充）**：从 `article div.prose` 获取结构化内容，可区分章节（`div.article-header`）和列表（`ul.article-list`）
3. **混合策略**：JSON-LD 获取全文 → DOM 提取阵容列表和章节标题 → 合并输出

## 六、补充信息源

当四大核心源无法覆盖时，降级到以下补充源：

| 信息源 | 用途 | URL 规律 |
| :--- | :--- | :--- |
| 网易体育 | 中文深度前瞻 | `c.m.163.com/news/a/{ID}.html` |
| 直播吧 | 五大联赛彩经 | `news.zhibo8.com/zuqiu/{date}/{ID}native.htm` |
| Goal.com | 全联赛英文前瞻 | `goal.com/en-us/news/watch-{teams}-{league}.../blt{ID}` |
| Wikipedia | 球队/球员百科 | `zh.wikipedia.org/wiki/{name}` |
| FBref | 进阶数据 | `fbref.com/en/players/{id}/{name}` |
| WorldFootball.net | 裁判记录 | `worldfootball.net/referee/{name}/` |
