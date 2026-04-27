import requests
import json
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

MATCHES = [
    {"cn": "欧鲁巴赫 vs 利雅得胜利", "home": "Al-Nassr", "away": "Al Orobah"},
    {"cn": "皇家盐湖城 vs 洛杉矶", "home": "Inter Miami", "away": "Los Angeles"},
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
    {"cn": "温哥华白浪 vs 达拉斯", "home": "Vancouver", "away": "Dallas"},
    {"cn": "阿德莱德联 vs 悉尼FC", "home": "Adelaide United", "away": "Sydney FC"},
    {"cn": "惠灵顿凤凰 vs 布里斯班狮吼", "home": "Wellington Phoenix", "away": "Brisbane"},
    {"cn": "沃尔夫斯堡 vs 霍芬海姆", "home": "Wolfsburg", "away": "Hoffenheim"},
    {"cn": "巴黎圣日耳曼 vs 纽卡斯尔联", "home": "PSG", "away": "Newcastle"},
    {"cn": "圣保利 vs 沃尔夫斯堡", "home": "St Pauli", "away": "Wolfsburg"},
    {"cn": "墨尔本胜利 vs 奥克兰", "home": "Melbourne Victory", "away": "Auckland"},
]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
})

def search_elfutbolero(team_a, team_b):
    queries = [f"{team_a} preview", f"{team_b} preview", f"{team_a} {team_b}", team_a, team_b]
    for query in queries:
        url = f"https://www.elfutbolero.us/search?q={quote_plus(query)}"
        try:
            r = session.get(url, timeout=10)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            if "No results found" in soup.get_text():
                continue
            both = []
            partial = []
            for article in soup.find_all("article"):
                link = article.find("a", href=True)
                if not link:
                    continue
                href = link["href"]
                title = article.get_text(strip=True).lower()
                ha = team_a.lower() in title
                hb = team_b.lower() in title
                has_preview = "preview" in title or "lineup" in title
                full_url = href if href.startswith("http") else "https://www.elfutbolero.us" + href
                if ha and hb:
                    both.append(full_url)
                elif (ha or hb) and has_preview:
                    partial.append(full_url)
            if both:
                return both[0]
            if partial:
                return partial[0]
        except Exception:
            continue
    return None

def search_sportsmole(team_a, team_b):
    queries = [
        f"site:sportsmole.co.uk {team_a} {team_b} preview",
        f"sportsmole {team_a} {team_b} prediction",
    ]
    for query in queries:
        url = f"https://www.google.com/search?q={quote_plus(query)}&num=5"
        try:
            r = session.get(url, timeout=10)
            if r.status_code != 200:
                continue
            for match in re.finditer(r'https?://www\.sportsmole\.co\.uk/football/[^"&\s]+preview[^"&\s]*\.html', r.text):
                return match.group(0)
        except Exception:
            continue
    return None

results = []
for i, m in enumerate(MATCHES):
    print(f"[{i+1}/{len(MATCHES)}] {m['cn']}...", flush=True)

    ef_url = search_elfutbolero(m["home"], m["away"])
    time.sleep(1)

    sm_url = search_sportsmole(m["home"], m["away"])
    time.sleep(1)

    result = {
        "match": m["cn"],
        "elfutbolero": ef_url,
        "sportsmole": sm_url,
    }
    results.append(result)
    ef_mark = "✅" if ef_url else "❌"
    sm_mark = "✅" if sm_url else "❌"
    print(f"  ElFutbolero={ef_mark} Sportsmole={sm_mark}", flush=True)

with open("/tmp/ef_sm_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

ef_count = sum(1 for r in results if r["elfutbolero"])
sm_count = sum(1 for r in results if r["sportsmole"])
print(f"\n=== SUMMARY ===")
print(f"El Futbolero: {ef_count}/{len(MATCHES)} ({round(ef_count/len(MATCHES)*100)}%)")
print(f"Sportsmole: {sm_count}/{len(MATCHES)} ({round(sm_count/len(MATCHES)*100)}%)")
