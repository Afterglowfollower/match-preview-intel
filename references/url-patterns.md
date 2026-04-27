# URL 规律文档 (URL Patterns)

各信息源的 URL 构造规律与搜索策略。

## 一、Sportsmole

### Preview 文章 URL 规律

```
https://www.sportsmole.co.uk/football/{team-slug}/preview/{team-a}-vs-{team-b}-prediction-team-news-lineups_{article_id}.html
```

- `{team-slug}`: 球队在 Sportsmole 上的 URL slug（如 `bayern-munich`、`al-nassr`）
- `{article_id}`: 文章数字 ID（6 位数字）

### 获取策略（优先级）

1. **球队页面提取（推荐，已验证）**：访问 `https://www.sportsmole.co.uk/football/{team-slug}/`，从页面中提取包含对手名的 Preview 链接
   - 优点：纯 HTTP 可获取，无需搜索引擎，覆盖沙特联/MLS/澳超等冷门联赛
   - 流程：球队页面 → 匹配 `href` 含 `preview` + `prediction` + 对手 slug 的链接 → 拼接完整 URL
2. **站内搜索（备选）**：`https://www.sportsmole.co.uk/search/?q={team_a}+{team_b}+preview`
   - 缺点：搜索结果不够精确，返回旧文章
3. **Preview 列表页（备选）**：`https://www.sportsmole.co.uk/football/preview/`

### ❌ 不可用方案

- ~~Google 搜索 `site:sportsmole.co.uk`~~：被限流 429，无法使用

### DOM 提取选择器

| 内容 | CSS 选择器 |
| :--- | :--- |
| 文章正文 | `div[itemprop="articleBody"]` 或 `div.article_body` |
| Team News 段落 | 搜索含 "Team News" 标题后的段落 |
| Possible Lineups | 搜索含 "Possible Lineups" 标题后的内容 |
| H2H 记录 | 搜索含 "Head-to-Head" 标题后的段落 |
| Prediction | 搜索含 "Prediction" 标题后的段落 |
| 球队页面 Preview 链接 | `a[href*="preview"][href*="prediction"]` |

### team-slug 映射（已验证）

| 球队 | slug | 联赛 |
| :--- | :--- | :--- |
| 拜仁慕尼黑 | `bayern-munich` | 德甲 |
| 多特蒙德 | `dortmund` | 德甲 |
| 巴塞罗那 | `barcelona` | 西甲 |
| 皇家马德里 | `real-madrid` | 西甲 |
| 塞维利亚 | `sevilla` | 西甲 |
| 云达不莱梅 | `werder-bremen` | 德甲 |
| 斯图加特 | `stuttgart` | 德甲 |
| 柏林联合 | `union-berlin` | 德甲 |
| 霍芬海姆 | `hoffenheim` | 德甲 |
| 法兰克福 | `frankfurt` | 德甲 |
| 门兴 | `monchengladbach` | 德甲 |
| 圣保利 | `st-pauli` | 德甲 |
| 科隆 | `koln` | 德乙 |
| 美因茨 | `mainz` | 德甲/德乙 |
| RB莱比锡 | `leipzig` | 德甲 |
| 利雅得胜利 | `al-nassr` | 沙特联 |
| 利雅得新月 | `al-hilal` | 沙特联 |
| 欧鲁巴赫 | `al-orobah` | 沙特联 |
| Inter Miami | `inter-miami` | MLS |
| Real Salt Lake | `real-salt-lake` | MLS |
| Vancouver | `vancouver-whitecaps` | MLS |
| FC Dallas | `fc-dallas` | MLS |
| Adelaide United | `adelaide-united` | 澳超 |
| Brisbane Roar | `brisbane-roar` | 澳超 |
| Central Coast | `central-coast-mariners` | 澳超 |
| Melbourne City | `melbourne-city` | 澳超 |
| Western Sydney | `western-sydney-wanderers` | 澳超 |
| Sydney FC | `sydney-fc` | 澳超 |
| Wellington Phoenix | `wellington-phoenix` | 澳超 |
| Melbourne Victory | `melbourne-victory` | 澳超 |
| Molde | `molde` | 挪威超 |
| Scotland | `scotland` | 国家队 |
| Portugal | `portugal` | 国家队 |
| Belgium | `belgium` | 国家队 |
| Morocco | `morocco` | 国家队 |
| PSG | `paris-saint-germain` | 法甲 |
| Newcastle | `newcastle-united` | 英超 |

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

## 六、Sofascore API (api.sofascore.com)

### 技术特征

- **无需浏览器**：纯 HTTP API，通过 Node.js `https` 模块直接请求
- **TLS 指纹检测**：Sofascore API 有 TLS 指纹验证，Python `requests` 会被 403，需用 `curl_cffi`（模拟 Chrome TLS 指纹）或 Node.js 原生 `https`
- **当前方案**：通过 `scripts/sofa_api.js`（Node.js）调用，Python 通过 `subprocess` 调用
- **限速**：建议 600ms 间隔（脚本已内置）
- **联赛覆盖**：全球 500+ 联赛，沙特联/MLS/澳超/K联赛/J联赛/中超全覆盖

### 核心 API 端点

| 端点 | URL Pattern | 说明 |
|:---|:---|:---|
| 搜索 | `/api/v1/search/{query}` | 搜索球队/球员/联赛/裁判 |
| 联赛赛季 | `/api/v1/unique-tournament/{tid}/seasons` | 获取联赛所有赛季 |
| 积分榜 | `/api/v1/unique-tournament/{tid}/season/{sid}/standings/total` | 结构化积分表 |
| 轮次赛程 | `/api/v1/unique-tournament/{tid}/season/{sid}/events/round/{round}` | 指定轮次所有比赛 |
| 比赛详情 | `/api/v1/event/{game_id}` | 裁判/场馆/比分 |
| 赛前状态 | `/api/v1/event/{game_id}/pregame-form` | 近5场/排名/评分/身价 |
| 历史交锋 | `/api/v1/event/{game_id}/h2h` | H2H 胜负记录 |
| 裁判统计 | `/api/v1/referee/{referee_id}` | 执法场次/出牌率 |
| 球队统计 | `/api/v1/team/{team_id}/unique-tournament/{tid}/season/{sid}/statistics/overall` | 115+ 指标 |
| 比赛事件 | `/api/v1/event/{game_id}/incidents` | 进球/黄牌/红牌/VAR |

### 联赛 ID 映射

| 联赛 | tournament_id |
|:---|:---|
| 沙特联 | 955 |
| 英超 | 17 |
| 西甲 | 8 |
| 德甲 | 35 |
| 德乙 | 44 |
| 意甲 | 23 |
| 法甲 | 34 |
| 欧冠 | 7 |
| 欧联 | 679 |
| MLS | 242 |
| 澳超 (A-League Men) | 136 |
| K联赛 (K League 1) | 410 |
| J联赛 | 292 |
| 挪威超 (Eliteserien) | 20 |
| 世界杯 | 16 |
| 世俱杯 | 631 |
| 欧洲杯 | 1 |
| 欧国联 | 10783 |
| 中超 | 378 |

### 调用方式

```bash
# 通过 Node.js 脚本
node scripts/sofa_api.js full-preview 955 63998 "Al-Nassr" "Al-Hilal"

# 单独命令
node scripts/sofa_api.js search "Saudi Pro League"
node scripts/sofa_api.js seasons 955
node scripts/sofa_api.js standings 955 63998
node scripts/sofa_api.js match-details 12624994
node scripts/sofa_api.js pregame-form 12624994
node scripts/sofa_api.js h2h 12624994
node scripts/sofa_api.js referee-stats {referee_id}
node scripts/sofa_api.js team-stats {team_id} 955 63998
```

### Python 集成

```python
from fetch_preview import fetch_sofascore_preview
result = fetch_sofascore_preview("Al-Nassr", "Al-Hilal", "Saudi Pro League")
# result = {standings, match, details, pregame_form, h2h, referee, team_stats}
```

## 七、补充信息源

当四大核心源无法覆盖时，降级到以下补充源：

| 信息源 | 用途 | URL 规律 |
| :--- | :--- | :--- |
| 网易体育 | 中文深度前瞻 | `c.m.163.com/news/a/{ID}.html` |
| 直播吧 | 五大联赛彩经 | `news.zhibo8.com/zuqiu/{date}/{ID}native.htm` |
| Goal.com | 全联赛英文前瞻 | `goal.com/en-us/news/watch-{teams}-{league}.../blt{ID}` |
| Wikipedia | 球队/球员百科 | `zh.wikipedia.org/wiki/{name}` |
| FBref | 进阶数据 | `fbref.com/en/players/{id}/{name}` |
| WorldFootball.net | 裁判记录 | `worldfootball.net/referee/{name}/` |
