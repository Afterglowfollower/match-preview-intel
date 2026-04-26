# 信息源路由表 (Source Routing)

根据联赛/赛事类型，路由到最优信息源组合。

## 一、联赛→信息源可用性矩阵

| 联赛/赛事 | WhoScored | Sportsmole | 风驰直播 | Transfermarkt | El Futbolero |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 英超 | ✅ 完整 | ✅ Preview | ✅ 彩经 | ✅ 完整 | ✅ Preview |
| 西甲 | ✅ 完整 | ✅ Preview | ✅ 彩经 | ✅ 完整 | ✅ Preview |
| 德甲 | ✅ 完整 | ✅ Preview | ✅ 彩经 | ✅ 完整 | ⚠️ 部分 |
| 意甲 | ✅ 完整 | ✅ Preview | ✅ 彩经 | ✅ 完整 | ⚠️ 部分 |
| 法甲 | ✅ 完整 | ✅ Preview | ✅ 彩经 | ✅ 完整 | ⚠️ 部分 |
| 欧冠 | ✅ 完整 | ✅ Preview | ✅ 彩经 | ✅ 完整 | ✅ Preview |
| 欧联 | ✅ 完整 | ✅ Preview | ⚠️ 部分 | ✅ 完整 | ⚠️ 部分 |
| 欧国联 | ⚠️ 部分 | ⚠️ 部分 | ❌ | ✅ 完整 | ⚠️ 部分 |
| 沙特联 | ❌ | ⚠️ 部分 | ❌ | ✅ 完整 | ✅ Preview |
| 美职联 (MLS) | ⚠️ 部分 | ⚠️ 部分 | ❌ | ✅ 完整 | ✅ Preview |
| 澳超 (A-League) | ❌ | ⚠️ 部分 | ❌ | ✅ 完整 | ⚠️ 部分 |
| K联赛 | ❌ | ⚠️ 部分 | ❌ | ✅ 完整 | ⚠️ 新闻 |
| J联赛 | ❌ | ⚠️ 部分 | ❌ | ✅ 完整 | ⚠️ 新闻 |
| 中超 | ❌ | ❌ | ⚠️ 部分 | ⚠️ 部分 | ❌ |
| 世界杯 | ✅ 完整 | ✅ Preview | ✅ 彩经 | ✅ 完整 | ✅ Preview |
| 世俱杯 | ⚠️ 部分 | ⚠️ 部分 | ❌ | ✅ 完整 | ✅ Preview |
| 洲际杯赛 | ⚠️ 部分 | ⚠️ 部分 | ❌ | ✅ 完整 | ⚠️ 部分 |

图例：✅ 完整覆盖 | ⚠️ 部分覆盖 | ❌ 无覆盖

## 二、二级子类→信息源优先级路由

### 1.2 积分形势
1. 风驰直播（直播前瞻段落，含积分、净胜球、射手榜）
2. WhoScored（Standings 页面，结构化积分表）
3. Transfermarkt（competitionTable API）
4. El Futbolero（Preview 文章中含积分排名描述，尤其沙特联/MLS）

### 1.3 后续赛程与晋级/降级压力
1. 风驰直播（前瞻文本中含后续赛程描述）
2. Sportsmole（Preview 文章中提及赛程压力）
3. El Futbolero（Preview 文章中含赛程压力描述）
4. WhoScored（Fixtures 页面）

### 1.4 裁判组构成与执法画像
1. Transfermarkt（refereeProfile API — 执法场次、出牌率）
2. 风驰直播（部分比赛页面含裁判信息）
3. WorldFootball.net（裁判执法记录，需 HTML 爬取）

### 2.3 相关历史事件/经典战役
1. Sportsmole（Preview 文章的 H2H 段落）
2. El Futbolero（Preview 文章的 head-to-head 段落，尤其沙特联/MLS）
3. 风驰直播（前瞻文本中的历史交锋描述）
4. Wikipedia（经典战役百科条目）

### 2.4 赛事历史基准线/纪录线
1. Sportsmole（Preview 文章中的纪录线描述）
2. 风驰直播（前瞻文本中的历史数据坐标）
3. Wikipedia / FIFA 官方（赛事纪录）

### 3.2 球队风格/打法特点
1. WhoScored（Team Style — PPDA、控球率、阵型倾向、传球网络）
2. Sportsmole（Preview 文章中的战术描述）
3. El Futbolero（Preview 文章中的战术/阵型描述）
4. 风驰直播（比赛统计中的进阶数据辅助判断）

### 3.3 主教练信息
1. Transfermarkt（coachProfile API — 执教履历、胜率、惯用阵型）
2. Sportsmole（Preview 文章中的教练背景段落）
3. Wikipedia（教练百科条目）

### 3.5 球队身份与荣誉
1. Transfermarkt（clubInfo API — 成立年份、荣誉列表）
2. Wikipedia（球队百科 — 绰号、世界排名、最佳战绩）
3. FIFA 排名页（国家队世界排名）

### 4.2 首发阵容变化
1. Sportsmole（Possible Lineups 段落）
2. El Futbolero（Probable Lineups — `<ul class="article-list">` 结构化阵容）
3. WhoScored（Predicted XI）
4. 风驰直播（首发阵容展示）

### 4.3 伤病与缺阵情况
1. Sportsmole（Team News 段落）
2. El Futbolero（Preview 文章中的 injury/doubtful/absence 描述）
3. Transfermarkt（俱乐部 injured 列表）
4. WhoScored（Injuries 页面）

### 4.4 停赛警戒与黄牌风险
1. Transfermarkt（球员停赛状态）
2. El Futbolero（Preview 文章中的 suspension/banned 描述）
3. FotMob（累积黄牌追踪，需 App/API）
4. ESPN（Suspended 列表）

### 5.1 技术特点与战术角色
1. WhoScored（Player Profiles — strengths/weaknesses 热力图、位置热区）
2. FBref（Scout Report — 进阶数据指标如 xG、xA、压力成功率）
3. Sportsmole（Preview 文章中的关键球员描述）

### 5.4 大赛经验
1. Transfermarkt（playerProfile API — 国家队出场数、进球数）
2. El Futbolero（Preview 文章中的球员履历/大赛经验描述）
3. Wikipedia（球员大赛经历百科）
4. Sportsmole（Preview 文章中的经验描述）

### 5.5 定位球战况
1. WhoScored（定位球主罚倾向数据）
2. FBref（点球记录、角球参与度）
3. Sportsmole（Preview 文章中的定位球描述）

### 5.6 俱乐部赛季负荷与状态
1. Transfermarkt（球员赛季出场记录、身价曲线）
2. FBref（90分钟出场数、分钟分布）
3. Understat（俱乐部 xG/xA 参与度）

### 6.1 场外背景与特殊身份
1. El Futbolero（深度叙事文章 — 球员背景、转会故事、场外风波，尤其沙特联/MLS）
2. Wikipedia（球员百科 — 国籍、家庭背景、励志经历）
3. 网易体育（深度前瞻文章中的场外故事）
4. Google News（搜索球员背景新闻）

### 6.2 人物关系/恩怨渊源
1. El Futbolero（深度叙事文章 — 恩怨/师徒/旧谊/俱乐部政治，尤其沙特联/MLS）
2. 网易体育（深度前瞻文章中的人物关系描述）
3. Wikipedia（教练/球员百科中的旧主关系）
4. Google News（搜索恩怨/师徒/旧谊相关新闻）

## 三、Transfermarkt API 调用指南

### 安装

```bash
# Python 方式
pip install transfermarkt-wrapper

# Node.js 方式
npm install transfermarkt_api_client
```

### 核心 API 端点

| 端点 | 功能 | 对应二级子类 |
| :--- | :--- | :--- |
| `playerProfile(id)` | 球员完整档案 | 5.1, 5.4, 5.6 |
| `coachProfile(id)` | 教练完整履历 | 3.3 |
| `refereeProfile(id)` | 裁判执法画像 | 1.4 |
| `clubInfo(id)` | 俱乐部详情 | 3.5 |
| `competitionTable(id)` | 联赛积分榜 | 1.2 |
| `gameDetails(id)` | 比赛详情 | 4.2 |
| `/ceapi/marketValueDevelopment/graph/{id}` | 身价曲线 | 5.6 |
| `/ceapi/transferHistory/list/{id}` | 转会记录 | 5.6 |

### 限速规则

- ceapi 端点：2 请求/分钟
- 其他端点：5 请求/分钟
- 建议缓存 TTL：24小时（身价/转会），1小时（阵容/积分）

### ID 解析

Transfermarkt 使用数字 ID 标识实体。获取 ID 的方式：
1. 搜索 API：`/quicksearch/{query}`
2. 从 Sportsmole/WhoScored 页面中的 Transfermarkt 链接提取
3. 缓存已知 ID 映射（`references/team-name-mapping.md`）
