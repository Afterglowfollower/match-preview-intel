const https = require("https");
const fs = require("fs");

const SOFASCORE_HEADERS = {
  Accept: "application/json",
  "Accept-Language": "en-US,en;q=0.9",
  Referer: "https://www.sofascore.com/",
  Origin: "https://www.sofascore.com",
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-site",
};

function sofaGet(path) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, "https://api.sofascore.com");
    const options = { hostname: url.hostname, path: url.pathname + url.search, headers: SOFASCORE_HEADERS };
    https.get(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
        catch (e) { resolve({ status: res.statusCode, data: {} }); }
      });
    }).on("error", reject);
  });
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

const MATCHES = [
  { cn: "欧鲁巴赫 vs 利雅得胜利", tid: 955, year: 2024, home: "Al Orobah", away: "Al-Nassr" },
  { cn: "皇家盐湖城 vs 洛杉矶", tid: 242, year: 2025, home: "Real Salt Lake", away: "Los Angeles FC" },
  { cn: "苏格兰 vs 葡萄牙", tid: 10783, year: 2024, home: "Scotland", away: "Portugal" },
  { cn: "阿德莱德联 vs 西悉尼流浪者", tid: 136, year: 2025, home: "Adelaide United", away: "Western Sydney Wanderers" },
  { cn: "布里斯班狮吼 vs 中央海岸水手", tid: 136, year: 2025, home: "Brisbane Roar", away: "Central Coast Mariners" },
  { cn: "云达不莱梅 vs 奥格斯堡", tid: 35, year: 2024, home: "Werder Bremen", away: "Augsburg" },
  { cn: "斯图加特 vs 拜仁慕尼黑", tid: 35, year: 2025, home: "Stuttgart", away: "Bayern" },
  { cn: "巴塞罗那 vs 塞维利亚", tid: 8, year: 2025, home: "Barcelona", away: "Sevilla" },
  { cn: "柏林联合 vs 霍芬海姆", tid: 35, year: 2024, home: "Union Berlin", away: "Hoffenheim" },
  { cn: "法兰克福 vs 波鸿", tid: 35, year: 2024, home: "Frankfurt", away: "Bochum" },
  { cn: "墨尔本城 vs 西部联", tid: 136, year: 2025, home: "Melbourne City", away: "Western United" },
  { cn: "布里斯班狮吼 vs 麦克阿瑟", tid: 136, year: 2025, home: "Brisbane Roar", away: "Macarthur" },
  { cn: "多特蒙德 vs 霍芬海姆", tid: 35, year: 2025, home: "Dortmund", away: "Hoffenheim" },
  { cn: "门兴格拉德巴赫 vs 多特蒙德", tid: 35, year: 2024, home: "Mönchengladbach", away: "Dortmund" },
  { cn: "蔚山现代 vs 大邱FC", tid: 410, year: 2025, home: "Ulsan", away: "Daegu" },
  { cn: "科隆 vs 美因茨", tid: 44, year: 2025, home: "Köln", away: "Mainz" },
  { cn: "圣保利 vs RB莱比锡", tid: 35, year: 2024, home: "St. Pauli", away: "Leipzig" },
  { cn: "柏林联合 vs 美因茨", tid: 35, year: 2024, home: "Union Berlin", away: "Mainz" },
  { cn: "拜仁慕尼黑 vs 皇家马德里", tid: 7, year: 2023, home: "Bayern", away: "Real Madrid" },
  { cn: "比利时 vs 摩洛哥", tid: 16, year: 2022, home: "Belgium", away: "Morocco" },
  { cn: "莫尔德 vs 瓦勒伦加", tid: 20, year: 2025, home: "Molde", away: "Vålerenga" },
  { cn: "欧鲁巴赫 vs 利雅得新月", tid: 955, year: 2024, home: "Al Orobah", away: "Al-Hilal" },
  { cn: "温哥华白浪 vs 达拉斯", tid: 242, year: 2025, home: "Vancouver Whitecaps", away: "FC Dallas" },
  { cn: "阿德莱德联 vs 悉尼FC", tid: 136, year: 2025, home: "Adelaide United", away: "Sydney FC" },
  { cn: "惠灵顿凤凰 vs 布里斯班狮吼", tid: 136, year: 2025, home: "Wellington Phoenix", away: "Brisbane Roar" },
  { cn: "沃尔夫斯堡 vs 霍芬海姆", tid: 35, year: 2025, home: "Wolfsburg", away: "Hoffenheim" },
  { cn: "巴黎圣日耳曼 vs 纽卡斯尔联", tid: 7, year: 2023, home: "Paris Saint-Germain", away: "Newcastle" },
  { cn: "圣保利 vs 沃尔夫斯堡", tid: 35, year: 2024, home: "St. Pauli", away: "Wolfsburg" },
  { cn: "墨尔本胜利 vs 奥克兰", tid: 136, year: 2025, home: "Melbourne Victory", away: "Auckland" },
];

async function getSeason(tid, year) {
  const r = await sofaGet(`/api/v1/unique-tournament/${tid}/seasons`);
  if (r.status !== 200) return null;
  const seasons = r.data.seasons || [];
  const yearStr = String(year);
  const yearShort = yearStr.slice(-2);
  let s = seasons.find((x) => String(x.year) === yearStr);
  if (!s) s = seasons.find((x) => String(x.year).includes(yearShort));
  if (!s) s = seasons.find((x) => String(x.name).includes(yearStr));
  if (!s) s = seasons.sort((a, b) => (b.year || 0) - (a.year || 0))[0];
  return s ? { id: s.id, name: s.name, year: s.year } : null;
}

async function findMatch(tid, seasonId, home, away) {
  for (let round = 1; round <= 46; round++) {
    const r = await sofaGet(`/api/v1/unique-tournament/${tid}/season/${seasonId}/events/round/${round}`);
    if (r.status !== 200) break;
    for (const e of r.data.events || []) {
      const h = (e.homeTeam.name || "").toLowerCase();
      const a = (e.awayTeam.name || "").toLowerCase();
      const homeL = home.toLowerCase();
      const awayL = away.toLowerCase();
      if ((h.includes(homeL) || homeL.includes(h.split(" ").pop())) && (a.includes(awayL) || awayL.includes(a.split(" ").pop()))) {
        return { round, id: e.id, home: e.homeTeam.name, away: e.awayTeam.name };
      }
    }
    if (round % 5 === 0) await sleep(400);
  }
  return null;
}

async function getMatchDetails(gameId) {
  const r = await sofaGet(`/api/v1/event/${gameId}`);
  if (r.status !== 200) return {};
  const e = r.data.event || {};
  return {
    referee: e.referee ? { name: e.referee.name, country: e.referee.country?.name } : null,
    venue: e.venue ? { name: e.venue.stadium.name, city: e.venue.city?.name } : null,
  };
}

async function getPregameForm(gameId) {
  const r = await sofaGet(`/api/v1/event/${gameId}/pregame-form`);
  if (r.status !== 200) return {};
  const result = {};
  for (const side of ["homeTeam", "awayTeam"]) {
    const f = r.data[side];
    if (f) result[side] = { position: f.position, avg_rating: f.avgRating, form: f.form || [], value: f.value };
  }
  return result;
}

async function getH2H(gameId) {
  const r = await sofaGet(`/api/v1/event/${gameId}/h2h`);
  if (r.status !== 200) return {};
  const d = r.data.teamDuel || {};
  return { home_wins: d.homeWins, away_wins: d.awayWins, draws: d.draws };
}

async function getRefereeStats(refereeName) {
  const r = await sofaGet(`/api/v1/search/${encodeURIComponent(refereeName)}`);
  if (r.status !== 200) return {};
  const refs = (r.data.results || []).filter((x) => x.type === "referee");
  if (refs.length === 0) return {};
  const refId = refs[0].entity.id;
  await sleep(400);
  const rr = await sofaGet(`/api/v1/referee/${refId}`);
  if (rr.status !== 200) return {};
  const ref = rr.data.referee || {};
  return { name: ref.name, games: ref.games, yellow_cards: ref.yellowCards, red_cards: ref.redCards, avg_cards: ref.games > 0 ? (ref.yellowCards / ref.games).toFixed(1) : null };
}

async function getTeamStats(teamId, tid, sid) {
  const r = await sofaGet(`/api/v1/team/${teamId}/unique-tournament/${tid}/season/${sid}/statistics/overall`);
  if (r.status !== 200) return {};
  return r.data.statistics || {};
}

async function processMatch(m) {
  const result = { cn: m.cn, sofa: null, elfutbolero: null, sportsmole: null, fczhibo: null };

  const season = await getSeason(m.tid, m.year);
  if (!season) { result.sofa = { found: false, reason: "season not found" }; return result; }

  const standings = await sofaGet(`/api/v1/unique-tournament/${m.tid}/season/${season.id}/standings/total`);
  const hasStandings = standings.status === 200 && standings.data.standings;
  await sleep(400);

  const match = await findMatch(m.tid, season.id, m.home, m.away);
  if (!match) { result.sofa = { found: false, standings: hasStandings, reason: "match not found in rounds" }; return result; }

  await sleep(400);
  const details = await getMatchDetails(match.id);
  await sleep(400);
  const form = await getPregameForm(match.id);
  await sleep(400);
  const h2h = await getH2H(match.id);

  let referee = {};
  if (details.referee?.name) {
    await sleep(400);
    referee = await getRefereeStats(details.referee.name);
  }

  let homeTeamId = null, awayTeamId = null;
  if (hasStandings) {
    const rows = standings.data.standings[0].rows || [];
    for (const r of rows) {
      if (r.team.name.toLowerCase().includes(m.home.toLowerCase())) homeTeamId = r.team.id;
      if (r.team.name.toLowerCase().includes(m.away.toLowerCase())) awayTeamId = r.team.id;
    }
  }

  let homeStats = {}, awayStats = {};
  if (homeTeamId) { await sleep(400); homeStats = await getTeamStats(homeTeamId, m.tid, season.id); }
  if (awayTeamId) { await sleep(400); awayStats = await getTeamStats(awayTeamId, m.tid, season.id); }

  result.sofa = {
    found: true,
    round: match.round,
    home: match.home,
    away: match.away,
    standings: hasStandings,
    referee: referee.name ? referee : null,
    venue: details.venue,
    pregame_form: form,
    h2h: h2h,
    home_stats_count: Object.keys(homeStats).length,
    away_stats_count: Object.keys(awayStats).length,
  };

  return result;
}

async function main() {
  const results = [];
  for (let i = 0; i < MATCHES.length; i++) {
    const m = MATCHES[i];
    console.error(`[${i + 1}/${MATCHES.length}] ${m.cn}...`);
    const result = await processMatch(m);
    results.push(result);
    if (result.sofa?.found) {
      const s = result.sofa;
      console.error(`  ✅ Sofascore: R${s.round} ${s.home} vs ${s.away} | ref=${s.referee?.name || "N/A"} | h2h=H${s.h2h.home_wins}D${s.h2h.draws}A${s.h2h.away_wins} | stats=${s.home_stats_count}/${s.away_stats_count}`);
    } else {
      console.error(`  ❌ Sofascore: ${result.sofa?.reason || "unknown"}`);
    }
    await sleep(600);
  }

  const summary = results.map((r) => ({
    match: r.cn,
    sofa_found: r.sofa?.found || false,
    sofa_round: r.sofa?.round || null,
    sofa_referee: r.sofa?.referee?.name || null,
    sofa_h2h: r.sofa?.h2h ? `H${r.sofa.h2h.home_wins}D${r.sofa.h2h.draws}A${r.sofa.h2h.away_wins}` : null,
    sofa_form: r.sofa?.pregame_form?.homeTeam ? `H:pos${r.sofa.pregame_form.homeTeam.position} A:pos${r.sofa.pregame_form.awayTeam?.position || "?"}` : null,
    sofa_stats: r.sofa?.found ? `${r.sofa.home_stats_count}/${r.sofa.away_stats_count}` : null,
    sofa_standings: r.sofa?.standings || false,
  }));

  console.log(JSON.stringify(summary, null, 2));

  const found = results.filter((r) => r.sofa?.found).length;
  const withReferee = results.filter((r) => r.sofa?.referee).length;
  const withH2H = results.filter((r) => r.sofa?.h2h?.home_wins !== undefined).length;
  const withForm = results.filter((r) => r.sofa?.pregame_form?.homeTeam).length;
  const withStats = results.filter((r) => (r.sofa?.home_stats_count || 0) > 0).length;
  const withStandings = results.filter((r) => r.sofa?.standings).length;

  console.error(`\n=== SOFASCORE SUMMARY ===`);
  console.error(`Match found: ${found}/${MATCHES.length} (${Math.round(found / MATCHES.length * 100)}%)`);
  console.error(`With standings: ${withStandings}/${MATCHES.length}`);
  console.error(`With referee: ${withReferee}/${MATCHES.length}`);
  console.error(`With H2H: ${withH2H}/${MATCHES.length}`);
  console.error(`With pregame form: ${withForm}/${MATCHES.length}`);
  console.error(`With team stats: ${withStats}/${MATCHES.length}`);
}

main().catch(console.error);
