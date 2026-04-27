"""
足球赛前情报爬虫 - 核心脚本
支持从 CSV 读取比赛列表，并行抓取 Sofascore / El Futbolero / Sportsmole / 风驰直播 / Transfermarkt 数据
WhoScored 保留为概念性信息源，待后续集成
"""

import csv
import time
import random
import json
import re
import subprocess
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("fetch_preview_log.txt", mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class MatchInfo:
    home_team: str = ""
    away_team: str = ""
    match_time: str = ""
    competition: str = ""
    csv_row: dict = field(default_factory=dict)


@dataclass
class PreviewData:
    match: MatchInfo = field(default_factory=MatchInfo)
    sofa_data: dict = field(default_factory=dict)
    sportsmole_url: str = ""
    sportsmole_content: str = ""
    fczhibo_url: str = ""
    fczhibo_content: str = ""
    elfutbolero_url: str = ""
    elfutbolero_content: str = ""
    tm_home_coach: dict = field(default_factory=dict)
    tm_away_coach: dict = field(default_factory=dict)
    tm_home_injuries: list = field(default_factory=list)
    tm_away_injuries: list = field(default_factory=list)
    tm_referee: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    })
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_page(url: str, session: requests.Session, timeout: int = 15) -> Optional[str]:
    try:
        time.sleep(random.uniform(1.5, 3.5))
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error ({url}): {e}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error ({url}): {e}")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout ({url}): {e}")
    except Exception as e:
        logger.error(f"Unknown error ({url}): {e}")
    return None


def parse_sportsmole(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {"team_news": "", "possible_lineups": "", "h2h": "", "prediction": "", "full_text": ""}

    body = soup.find("div", itemprop="articleBody") or soup.find("div", class_="article_body")
    if not body:
        return result

    result["full_text"] = body.get_text(strip=True, separator="\n")

    paragraphs = body.find_all(["p", "h2", "h3"])
    current_section = ""
    section_texts = {"team_news": [], "possible_lineups": [], "h2h": [], "prediction": []}

    for p in paragraphs:
        text = p.get_text(strip=True)
        lower = text.lower()
        if "team news" in lower:
            current_section = "team_news"
        elif "possible lineup" in lower or "predicted xi" in lower:
            current_section = "possible_lineups"
        elif "head-to-head" in lower or "h2h" in lower:
            current_section = "h2h"
        elif "prediction" in lower and len(lower) < 50:
            current_section = "prediction"
        elif current_section and text:
            section_texts[current_section].append(text)

    for key, texts in section_texts.items():
        result[key] = "\n".join(texts)

    return result


def parse_fczhibo(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {"preview_text": "", "match_stats": {}, "lineups": {}}

    all_text = soup.get_text(strip=True, separator="\n")
    if "直播前瞻" in all_text:
        idx = all_text.find("直播前瞻")
        result["preview_text"] = all_text[idx : idx + 3000]

    return result


def search_elfutbolero_url(team_a: str, team_b: str, session: requests.Session) -> Optional[str]:
    queries = [
        f"{team_a} preview",
        f"{team_b} preview",
        f"{team_a} {team_b}",
        team_a,
        team_b,
    ]
    for query in queries:
        search_url = f"https://www.elfutbolero.us/search?q={quote_plus(query)}"
        html = fetch_page(search_url, session)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        if "No results found" in (soup.find("main") or soup).get_text():
            continue

        both_matches = []
        partial_matches = []

        for article in soup.find_all("article"):
            link = article.find("a", href=True)
            if not link:
                continue
            href = link["href"]
            title = article.get_text(strip=True).lower()
            team_a_lower = team_a.lower()
            team_b_lower = team_b.lower()
            has_a = team_a_lower in title
            has_b = team_b_lower in title
            has_preview = "preview" in title or "lineup" in title or "match" in title

            full_url = href
            if href.startswith("/"):
                full_url = "https://www.elfutbolero.us" + href

            if has_a and has_b:
                both_matches.append(full_url)
            elif (has_a or has_b) and has_preview:
                partial_matches.append(full_url)

        if both_matches:
            return both_matches[0]
        if partial_matches:
            return partial_matches[0]
    return None


def parse_elfutbolero(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {
        "headline": "",
        "full_text": "",
        "lineups": "",
        "section_headers": [],
        "keywords": [],
        "date_published": "",
    }

    for ld in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(ld.string)
            if data.get("@type") == "NewsArticle":
                result["headline"] = data.get("headline", "")
                result["full_text"] = data.get("articleBody", "")
                result["keywords"] = data.get("keywords", [])
                result["date_published"] = data.get("datePublished", "")
                break
        except (json.JSONDecodeError, TypeError):
            pass

    article = soup.find("article")
    if article:
        for ad in article.find_all(class_="article-ad"):
            ad.decompose()

        prose = article.find("div", class_="prose")
        if prose:
            headers = prose.find_all(class_="article-header")
            result["section_headers"] = [h.get_text(strip=True) for h in headers]

            lineup_lists = prose.find_all("ul", class_="article-list")
            lineup_texts = []
            for ul in lineup_lists:
                text = ul.get_text(strip=True, separator="; ")
                lower_text = text.lower()
                has_position_kw = any(
                    kw in lower_text
                    for kw in ["goalkeeper", "defender", "midfielder", "forward", " xi"]
                )
                has_player_sep = ";" in text and text.count(";") >= 4
                has_team_name = any(
                    kw in lower_text
                    for kw in ["al hilal", "al nassr", "inter miami", "united", "city", "real"]
                )
                is_broadcast = any(
                    kw in lower_text
                    for kw in ["streaming", "broadcast", "tv:", "fubo", "dazn", "apple tv", "fox sports"]
                )
                if is_broadcast:
                    continue
                if has_position_kw or (has_team_name and has_player_sep):
                    lineup_texts.append(text)
            result["lineups"] = "\n".join(lineup_texts)

    return result


def extract_elfutbolero_sections(parsed: dict) -> dict:
    full_text = parsed.get("full_text", "")
    if not full_text:
        return {}

    sections = {
        "standings": "",
        "team_news": "",
        "h2h": "",
        "lineups": parsed.get("lineups", ""),
        "prediction": "",
        "coach_info": "",
        "off_field": "",
    }

    lower = full_text.lower()

    standings_patterns = [
        r"(?:sitting|sits|stands|currently)\s+(?:\w+\s+)?(?:in\s+)?(?:the\s+)?(\w+\s+)?(?:with\s+\d+\s+points)",
        r"(\d+(?:st|nd|rd|th)\s+(?:in\s+)?(?:the\s+)?(?:Eastern|Western\s+)?(?:Conference|League|table))",
        r"(\d+\s+points\s*\(\d+W?[-–]\d+D?[-–]\d+L?\))",
    ]
    for pat in standings_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            start = max(0, m.start() - 100)
            sections["standings"] = full_text[start : m.end() + 50].strip()
            break

    injury_patterns = [
        r"(?:injur(?:y|ies)|absen(?:ce|t)|doubtful|out|sidelined|miss(?:ing|es)).*?(?:\.|$)",
        r"(?:without|missing)\s+[\w\s]+(?:knee|hamstring|ankle|muscle|injury)",
    ]
    for pat in injury_patterns:
        matches = re.findall(pat, full_text, re.IGNORECASE)
        if matches:
            sections["team_news"] = " ".join(matches[:5])
            break

    h2h_patterns = [
        r"(?:head-to-head|h2h|histor(?:y|ically)|all-time|previous\s+meetings).*?(?:\.|$)",
    ]
    for pat in h2h_patterns:
        matches = re.findall(pat, full_text, re.IGNORECASE)
        if matches:
            sections["h2h"] = " ".join(matches[:3])
            break

    prediction_patterns = [
        r"(?:predict(?:ed|ion)?|forecast|expect(?:ed|ing)?|favor(?:ite|ed)).*?(?:\.|$)",
    ]
    for pat in prediction_patterns:
        matches = re.findall(pat, full_text, re.IGNORECASE)
        if matches:
            sections["prediction"] = " ".join(matches[:3])
            break

    return sections


SOFA_API_SCRIPT = Path(__file__).parent / "sofa_api.js"

TOURNAMENT_MAP = {
    "saudi pro league": 955,
    "premier league": 17,
    "la liga": 8,
    "bundesliga": 35,
    "2. bundesliga": 44,
    "serie a": 23,
    "ligue 1": 34,
    "champions league": 7,
    "europa league": 679,
    "a-league": 136,
    "a-league men": 136,
    "k league 1": 410,
    "k league": 410,
    "j1 league": 292,
    "j.league": 292,
    "mls": 242,
    "eliteserien": 20,
    "norwegian": 20,
    "world cup": 16,
    "club world cup": 631,
    "european championship": 1,
    "euro": 1,
    "nations league": 10783,
    "uefa nations league": 10783,
    "chinese super league": 378,
    "super liga": 378,
}


def _run_sofa_api(*args) -> Optional[dict]:
    if not SOFA_API_SCRIPT.exists():
        logger.error(f"Sofascore API script not found: {SOFA_API_SCRIPT}")
        return None
    try:
        result = subprocess.run(
            ["node", str(SOFA_API_SCRIPT)] + list(args),
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            logger.error(f"sofa_api.js error: {result.stderr[:200]}")
            return None
        return json.loads(result.stdout.strip())
    except subprocess.TimeoutExpired:
        logger.error("sofa_api.js timed out")
    except json.JSONDecodeError as e:
        logger.error(f"sofa_api.js JSON parse error: {e}")
    except Exception as e:
        logger.error(f"sofa_api.js unknown error: {e}")
    return None


def _find_tournament_id(competition: str) -> Optional[int]:
    lower = competition.lower().strip()
    for name, tid in TOURNAMENT_MAP.items():
        if name in lower or lower in name:
            return tid
    return None


def fetch_sofascore_preview(home_team: str, away_team: str, competition: str) -> dict:
    result = {"standings": [], "match": None, "details": {}, "pregame_form": {}, "h2h": {}, "referee": {}, "team_stats": {}}

    tournament_id = _find_tournament_id(competition)
    if not tournament_id:
        search = _run_sofa_api("search", competition, "uniqueTournament")
        if search and len(search) > 0:
            tournament_id = search[0].get("id")
    if not tournament_id:
        logger.warning(f"Sofascore: tournament not found for '{competition}'")
        return result

    season = _run_sofa_api("seasons", str(tournament_id))
    if not season or not season.get("id"):
        logger.warning(f"Sofascore: season not found for tournament {tournament_id}")
        return result
    season_id = season["id"]

    full = _run_sofa_api("full-preview", str(tournament_id), str(season_id), home_team, away_team)
    if full:
        result = full

    return result


SPORTSMOLE_TEAM_SLUG_MAP = {
    "al-nassr": "al-nassr", "al-hilal": "al-hilal", "al-ahli": "al-ahli",
    "al-orobah": "al-orobah", "al-ettifaq": "al-ettifaq", "al-itthad": "al-itthad",
    "barcelona": "barcelona", "real madrid": "real-madrid", "sevilla": "sevilla",
    "atletico madrid": "atletico-madrid",
    "bayern munich": "bayern-munich", "bayern": "bayern-munich",
    "dortmund": "dortmund", "borussia dortmund": "dortmund",
    "stuttgart": "stuttgart", "leverkusen": "leverkusen",
    "union berlin": "union-berlin", "hoffenheim": "hoffenheim",
    "werder bremen": "werder-bremen", "bremen": "werder-bremen",
    "frankfurt": "frankfurt", "wolfsburg": "wolfsburg",
    "st pauli": "st-pauli", "st. pauli": "st-pauli",
    "leipzig": "leipzig", "rb leipzig": "leipzig",
    "mainz": "mainz", "koln": "koln", "cologne": "koln",
    "bochum": "bochum", "augsburg": "augsburg",
    "monchengladbach": "monchengladbach", "gladbach": "monchengladbach",
    "inter miami": "inter-miami", "los angeles fc": "los-angeles-fc",
    "real salt lake": "real-salt-lake", "vancouver whitecaps": "vancouver-whitecaps",
    "fc dallas": "fc-dallas", "dallas": "fc-dallas",
    "adelaide united": "adelaide-united", "western sydney": "western-sydney-wanderers",
    "brisbane roar": "brisbane-roar", "central coast": "central-coast-mariners",
    "melbourne city": "melbourne-city", "western united": "western-united",
    "macarthur": "macarthur-fc", "sydney fc": "sydney-fc",
    "wellington phoenix": "wellington-phoenix",
    "melbourne victory": "melbourne-victory", "auckland": "auckland-fc",
    "ulsan": "ulsan", "daegu": "daegu",
    "molde": "molde", "valerenga": "valerenga",
    "scotland": "scotland", "portugal": "portugal",
    "belgium": "belgium", "morocco": "morocco",
    "psg": "paris-saint-germain", "paris saint-germain": "paris-saint-germain",
    "newcastle": "newcastle-united", "newcastle united": "newcastle-united",
    "liverpool": "liverpool", "arsenal": "arsenal", "manchester city": "manchester-city",
    "manchester united": "manchester-united", "man utd": "manchester-united",
    "chelsea": "chelsea", "tottenham": "tottenham",
}


def _to_sportsmole_slug(team_name: str) -> str:
    lower = team_name.lower().strip()
    if lower in SPORTSMOLE_TEAM_SLUG_MAP:
        return SPORTSMOLE_TEAM_SLUG_MAP[lower]
    return lower.replace(" ", "-").replace(".", "").replace("'", "")


def search_sportsmole_url(team_a: str, team_b: str, session: requests.Session) -> Optional[str]:
    slug_a = _to_sportsmole_slug(team_a)
    slug_b = _to_sportsmole_slug(team_b)
    exact = []
    partial = []
    for slug in [slug_a, slug_b]:
        team_page_url = f"https://www.sportsmole.co.uk/football/{slug}/"
        html = fetch_page(team_page_url, session)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "preview" not in href.lower() and "prediction" not in href.lower():
                continue
            other_slug = slug_b if slug == slug_a else slug_a
            full_url = href if href.startswith("http") else f"https://www.sportsmole.co.uk{href}"
            url_slug = full_url.split("/preview/")[-1].split("_")[0].lower() if "/preview/" in full_url else ""
            url_has_other = other_slug in url_slug or other_slug.replace("-", " ") in url_slug.replace("-", " ")
            link_text = a.get_text(strip=True).lower()
            other_name_parts = team_b.lower().split() if slug == slug_a else team_a.lower().split()
            text_match = sum(1 for part in other_name_parts if part in link_text)
            if url_has_other and text_match >= len(other_name_parts) - 1:
                exact.append(full_url)
            elif url_has_other or text_match >= max(1, len(other_name_parts) - 1):
                partial.append((int(url_has_other) * 10 + text_match, full_url))
    if exact:
        return exact[0]
    if partial:
        partial.sort(key=lambda x: -x[0])
        return partial[0][1]
    return None


def search_fczhibo_url(team_a_cn: str, team_b_cn: str, session: requests.Session) -> Optional[str]:
    query = f"site:fczhibo.net {team_a_cn} {team_b_cn}"
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    html = fetch_page(search_url, session)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "fczhibo.net" in href:
            if "/url?q=" in href:
                href = href.split("/url?q=")[1].split("&")[0]
            return href
    return None


def fetch_tm_coach(team_name: str, session: requests.Session) -> dict:
    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={team_name.replace(' ', '+')}"
    html = fetch_page(search_url, session)
    if not html:
        return {}
    soup = BeautifulSoup(html, "html.parser")
    coach_link = soup.find("a", href=lambda x: x and "/trainer/" in str(x))
    if coach_link:
        coach_url = "https://www.transfermarkt.com" + coach_link["href"] if coach_link["href"].startswith("/") else coach_link["href"]
        coach_html = fetch_page(coach_url, session)
        if coach_html:
            coach_soup = BeautifulSoup(coach_html, "html.parser")
            name_el = coach_soup.find("h1", class_="dataName")
            info_els = coach_soup.find_all("span", class_="dataValue")
            return {
                "name": name_el.get_text(strip=True) if name_el else "",
                "url": coach_url,
                "info": [el.get_text(strip=True) for el in info_els[:5]],
            }
    return {}


def fetch_tm_referee(referee_name: str, session: requests.Session) -> dict:
    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={referee_name.replace(' ', '+')}"
    html = fetch_page(search_url, session)
    if not html:
        return {}
    soup = BeautifulSoup(html, "html.parser")
    ref_link = soup.find("a", href=lambda x: x and "/schiedsrichter/" in str(x))
    if ref_link:
        ref_url = "https://www.transfermarkt.com" + ref_link["href"] if ref_link["href"].startswith("/") else ref_link["href"]
        ref_html = fetch_page(ref_url, session)
        if ref_html:
            ref_soup = BeautifulSoup(ref_html, "html.parser")
            name_el = ref_soup.find("h1", class_="dataName")
            return {
                "name": name_el.get_text(strip=True) if name_el else referee_name,
                "url": ref_url,
            }
    return {}


def process_match(match: MatchInfo, session: requests.Session) -> PreviewData:
    data = PreviewData(match=match)
    logger.info(f"Processing: {match.home_team} vs {match.away_team}")

    sofa = fetch_sofascore_preview(match.home_team, match.away_team, match.competition)
    if sofa and sofa.get("match"):
        data.sofa_data = sofa
    else:
        data.errors.append("Sofascore: match not found or API unavailable")

    ef_url = search_elfutbolero_url(match.home_team, match.away_team, session)
    if ef_url:
        data.elfutbolero_url = ef_url
        html = fetch_page(ef_url, session)
        if html:
            parsed = parse_elfutbolero(html)
            sections = extract_elfutbolero_sections(parsed)
            combined = {**parsed, "extracted_sections": sections}
            data.elfutbolero_content = json.dumps(combined, ensure_ascii=False, indent=2)
    else:
        data.errors.append("El Futbolero: preview article not found")

    sm_url = search_sportsmole_url(match.home_team, match.away_team, session)
    if sm_url:
        data.sportsmole_url = sm_url
        html = fetch_page(sm_url, session)
        if html:
            parsed = parse_sportsmole(html)
            data.sportsmole_content = json.dumps(parsed, ensure_ascii=False, indent=2)
    else:
        data.errors.append("Sportsmole: preview article not found")

    fc_url = search_fczhibo_url(match.home_team, match.away_team, session)
    if fc_url:
        data.fczhibo_url = fc_url
        html = fetch_page(fc_url, session)
        if html:
            parsed = parse_fczhibo(html)
            data.fczhibo_content = json.dumps(parsed, ensure_ascii=False, indent=2)
    else:
        data.errors.append("风驰直播: match page not found")

    data.tm_home_coach = fetch_tm_coach(match.home_team, session)
    data.tm_away_coach = fetch_tm_coach(match.away_team, session)

    return data


def read_csv(csv_path: str) -> list[MatchInfo]:
    matches = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams = row.get("TEAMS", "")
            if " vs " in teams:
                parts = teams.split(" vs ")
                match = MatchInfo(
                    home_team=parts[0].strip(),
                    away_team=parts[1].strip(),
                    match_time=row.get("DATE", ""),
                    competition="",
                    csv_row=row,
                )
                matches.append(match)
    return matches


def save_results(results: list[PreviewData], output_path: str):
    output = []
    for r in results:
        sofa = r.sofa_data
        output.append({
            "home_team": r.match.home_team,
            "away_team": r.match.away_team,
            "match_time": r.match.match_time,
            "competition": r.match.competition,
            "sofascore_standings": sofa.get("standings", [])[:5] if sofa else [],
            "sofascore_match": sofa.get("match") if sofa else None,
            "sofascore_referee": sofa.get("referee") if sofa else None,
            "sofascore_pregame_form": sofa.get("pregame_form") if sofa else None,
            "sofascore_h2h": sofa.get("h2h") if sofa else None,
            "sofascore_team_stats_home": sofa.get("team_stats", {}).get("home") if sofa else None,
            "sofascore_team_stats_away": sofa.get("team_stats", {}).get("away") if sofa else None,
            "elfutbolero_url": r.elfutbolero_url,
            "elfutbolero_preview": r.elfutbolero_content[:500] if r.elfutbolero_content else "",
            "sportsmole_url": r.sportsmole_url,
            "sportsmole_preview": r.sportsmole_content[:500] if r.sportsmole_content else "",
            "fczhibo_url": r.fczhibo_url,
            "fczhibo_preview": r.fczhibo_content[:500] if r.fczhibo_content else "",
            "tm_home_coach": r.tm_home_coach,
            "tm_away_coach": r.tm_away_coach,
            "errors": r.errors,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    logger.info(f"Results saved to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="足球赛前情报爬虫")
    parser.add_argument("--csv", required=True, help="输入 CSV 文件路径")
    parser.add_argument("--output", default="preview_results.json", help="输出 JSON 文件路径")
    args = parser.parse_args()

    matches = read_csv(args.csv)
    logger.info(f"Loaded {len(matches)} matches from CSV")

    session = create_session()
    results = []

    for match in matches:
        data = process_match(match, session)
        results.append(data)

    save_results(results, args.output)


if __name__ == "__main__":
    main()
