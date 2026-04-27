import sys
sys.path.insert(0, "/Users/bytedance/Documents/未命名文件夹/shijiebei/.trae/skills/match-preview-intel/scripts")
from fetch_preview import search_sportsmole_url, parse_sportsmole, fetch_page, create_session
import json
import time

MATCHES = [
    {"cn": "欧鲁巴赫 vs 利雅得胜利", "home": "Al-Nassr", "away": "Al Orobah"},
    {"cn": "皇家盐湖城 vs 洛杉矶", "home": "Real Salt Lake", "away": "Los Angeles FC"},
    {"cn": "苏格兰 vs 葡萄牙", "home": "Scotland", "away": "Portugal"},
    {"cn": "阿德莱德联 vs 西悉尼流浪者", "home": "Adelaide United", "away": "Western Sydney"},
    {"cn": "布里斯班狮吼 vs 中央海岸水手", "home": "Brisbane Roar", "away": "Central Coast"},
    {"cn": "云达不莱梅 vs 奥格斯堡", "home": "Werder Bremen", "away": "Augsburg"},
    {"cn": "斯图加特 vs 拜仁慕尼黑", "home": "Stuttgart", "away": "Bayern Munich"},
    {"cn": "巴塞罗那 vs 塞维利亚", "home": "Barcelona", "away": "Sevilla"},
    {"cn": "柏林联合 vs 霍芬海姆", "home": "Union Berlin", "away": "Hoffenheim"},
    {"cn": "法兰克福 vs 波鸿", "home": "Frankfurt", "away": "Bochum"},
    {"cn": "墨尔本城 vs 西部联", "home": "Melbourne City", "away": "Western United"},
    {"cn": "布里斯班狮吼 vs 麦克阿瑟", "home": "Brisbane Roar", "away": "Macarthur"},
    {"cn": "多特蒙德 vs 霍芬海姆", "home": "Dortmund", "away": "Hoffenheim"},
    {"cn": "门兴格拉德巴赫 vs 多特蒙德", "home": "Monchengladbach", "away": "Dortmund"},
    {"cn": "蔚山现代 vs 大邱FC", "home": "Ulsan", "away": "Daegu"},
    {"cn": "科隆 vs 美因茨", "home": "Koln", "away": "Mainz"},
    {"cn": "圣保利 vs RB莱比锡", "home": "St Pauli", "away": "Leipzig"},
    {"cn": "柏林联合 vs 美因茨", "home": "Union Berlin", "away": "Mainz"},
    {"cn": "拜仁慕尼黑 vs 皇家马德里", "home": "Bayern Munich", "away": "Real Madrid"},
    {"cn": "比利时 vs 摩洛哥", "home": "Belgium", "away": "Morocco"},
    {"cn": "莫尔德 vs 瓦勒伦加", "home": "Molde", "away": "Valerenga"},
    {"cn": "欧鲁巴赫 vs 利雅得新月", "home": "Al-Hilal", "away": "Al Orobah"},
    {"cn": "温哥华白浪 vs 达拉斯", "home": "Vancouver Whitecaps", "away": "FC Dallas"},
    {"cn": "阿德莱德联 vs 悉尼FC", "home": "Adelaide United", "away": "Sydney FC"},
    {"cn": "惠灵顿凤凰 vs 布里斯班狮吼", "home": "Wellington Phoenix", "away": "Brisbane Roar"},
    {"cn": "沃尔夫斯堡 vs 霍芬海姆", "home": "Wolfsburg", "away": "Hoffenheim"},
    {"cn": "巴黎圣日耳曼 vs 纽卡斯尔联", "home": "PSG", "away": "Newcastle"},
    {"cn": "圣保利 vs 沃尔夫斯堡", "home": "St Pauli", "away": "Wolfsburg"},
    {"cn": "墨尔本胜利 vs 奥克兰", "home": "Melbourne Victory", "away": "Auckland"},
]

session = create_session()
results = []
found = 0
with_content = 0

for i, m in enumerate(MATCHES):
    url = search_sportsmole_url(m["home"], m["away"], session)
    has_content = False
    if url:
        found += 1
        html = fetch_page(url, session)
        if html:
            parsed = parse_sportsmole(html)
            has_content = bool(parsed.get("full_text"))
            if has_content:
                with_content += 1
    mark = "✅" if url else "❌"
    content_mark = "📝" if has_content else ""
    print(f"[{i+1}/{len(MATCHES)}] {m['cn']}: {mark} {content_mark} {url or 'NOT FOUND'}")
    time.sleep(1.5)

print(f"\n=== SUMMARY ===")
print(f"Sportsmole (new): {found}/{len(MATCHES)} found ({round(found/len(MATCHES)*100)}%)")
print(f"With content: {with_content}/{len(MATCHES)} ({round(with_content/len(MATCHES)*100)}%)")
