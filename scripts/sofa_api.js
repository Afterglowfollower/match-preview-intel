const https = require("https");

const SOFASCORE_HEADERS = {
  Accept: "application/json",
  "Accept-Language": "en-US,en;q=0.9",
  Referer: "https://www.sofascore.com/",
  Origin: "https://www.sofascore.com",
  "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-site",
};

const BASE = "https://api.sofascore.com";

function sofaGet(path) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE);
    const options = { hostname: url.hostname, path: url.pathname + url.search, headers: SOFASCORE_HEADERS };
    https
      .get(options, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            resolve({ status: res.statusCode, data: JSON.parse(data) });
          } catch (e) {
            resolve({ status: res.statusCode, data: {} });
          }
        });
      })
      .on("error", reject);
  });
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function searchEntity(query, entityType) {
  const r = await sofaGet(`/api/v1/search/${encodeURIComponent(query)}`);
  if (r.status !== 200) return [];
  const results = (r.data.results || []).filter((x) => !entityType || x.type === entityType);
  return results.map((x) => ({ id: x.entity.id, name: x.entity.name, type: x.type, slug: x.entity.slug || "" }));
}

async function getLatestSeason(tournamentId) {
  const r = await sofaGet(`/api/v1/unique-tournament/${tournamentId}/seasons`);
  if (r.status !== 200) return null;
  const seasons = r.data.seasons || [];
  const latest = seasons.sort((a, b) => (b.year || 0) - (a.year || 0))[0];
  return latest ? { id: latest.id, name: latest.name, year: latest.year } : null;
}

async function getSeasonByYear(tournamentId, year) {
  const r = await sofaGet(`/api/v1/unique-tournament/${tournamentId}/seasons`);
  if (r.status !== 200) return null;
  const seasons = r.data.seasons || [];
  const yearStr = String(year);
  const yearShort = yearStr.slice(-2);
  let match = seasons.find((s) => String(s.year) === yearStr);
  if (!match) match = seasons.find((s) => String(s.year).includes(yearShort));
  if (!match) match = seasons.find((s) => String(s.name).includes(yearStr));
  if (match) return { id: match.id, name: match.name, year: match.year };
  const latest = seasons.sort((a, b) => (b.year || 0) - (a.year || 0))[0];
  return latest ? { id: latest.id, name: latest.name, year: latest.year } : null;
}

async function getStandings(tournamentId, seasonId) {
  const r = await sofaGet(`/api/v1/unique-tournament/${tournamentId}/season/${seasonId}/standings/total`);
  if (r.status !== 200 || !r.data.standings) return [];
  const rows = r.data.standings[0]?.rows || [];
  return rows.map((row) => ({
    position: row.position,
    team: row.team.name,
    team_id: row.team.id,
    points: row.points,
    wins: row.wins,
    draws: row.draws,
    losses: row.losses,
    scores_for: row.scoresFor,
    scores_against: row.scoresAgainst,
  }));
}

async function findMatchByTeams(tournamentId, seasonId, homeTeam, awayTeam) {
  for (let round = 1; round <= 40; round++) {
    const r = await sofaGet(`/api/v1/unique-tournament/${tournamentId}/season/${seasonId}/events/round/${round}`);
    if (r.status !== 200) break;
    const events = r.data.events || [];
    for (const e of events) {
      const hName = (e.homeTeam.name || "").toLowerCase();
      const aName = (e.awayTeam.name || "").toLowerCase();
      if (hName.includes(homeTeam.toLowerCase()) && aName.includes(awayTeam.toLowerCase())) {
        return { game_id: e.id, round, homeTeam: e.homeTeam.name, awayTeam: e.awayTeam.name, startTimestamp: e.startTimestamp };
      }
    }
    await sleep(600);
  }
  return null;
}

async function getMatchDetails(gameId) {
  const r = await sofaGet(`/api/v1/event/${gameId}`);
  if (r.status !== 200) return {};
  const e = r.data.event || {};
  return {
    referee: e.referee ? { name: e.referee.name, country: e.referee.country?.name } : null,
    venue: e.venue ? { name: e.venue.stadium.name, city: e.venue.city?.name, capacity: e.venue.stadium.capacity } : null,
    homeTeam: e.homeTeam?.name,
    awayTeam: e.awayTeam?.name,
    homeScore: e.homeScore?.current,
    awayScore: e.awayScore?.current,
    startTimestamp: e.startTimestamp,
  };
}

async function getPregameForm(gameId) {
  const r = await sofaGet(`/api/v1/event/${gameId}/pregame-form`);
  if (r.status !== 200) return {};
  const result = {};
  for (const side of ["homeTeam", "awayTeam"]) {
    const f = r.data[side];
    if (f) {
      result[side] = {
        position: f.position,
        avg_rating: f.avgRating,
        value: f.value,
        form: f.form || [],
      };
    }
  }
  return result;
}

async function getH2H(gameId) {
  const r = await sofaGet(`/api/v1/event/${gameId}/h2h`);
  if (r.status !== 200) return {};
  const duel = r.data.teamDuel || {};
  return { home_wins: duel.homeWins, away_wins: duel.awayWins, draws: duel.draws };
}

async function getRefereeStats(refereeId) {
  const r = await sofaGet(`/api/v1/referee/${refereeId}`);
  if (r.status !== 200) return {};
  const ref = r.data.referee || {};
  return {
    name: ref.name,
    country: ref.country?.name,
    games: ref.games,
    yellow_cards: ref.yellowCards,
    red_cards: ref.redCards,
    yellow_to_red: ref.yellowToRedCards,
    penalties: ref.penalties,
    avg_cards_per_game: ref.games > 0 ? ((ref.yellowCards || 0) / ref.games).toFixed(2) : null,
  };
}

async function getTeamStats(teamId, tournamentId, seasonId) {
  const r = await sofaGet(`/api/v1/team/${teamId}/unique-tournament/${tournamentId}/season/${seasonId}/statistics/overall`);
  if (r.status !== 200) return {};
  return r.data.statistics || {};
}

async function getMatchIncidents(gameId) {
  const r = await sofaGet(`/api/v1/event/${gameId}/incidents`);
  if (r.status !== 200) return [];
  return (r.data.incidents || []).map((inc) => ({
    type: inc.incidentType,
    time: inc.time,
    player: inc.player?.name,
    team: inc.isHome ? "home" : "away",
    reason: inc.reason,
    card_type: inc.incidentClass,
  }));
}

async function main() {
  const command = process.argv[2];
  const args = process.argv.slice(3);

  switch (command) {
    case "search": {
      const [query, type] = args;
      const results = await searchEntity(query, type);
      console.log(JSON.stringify(results));
      break;
    }
    case "seasons": {
      const [tid] = args;
      const season = await getLatestSeason(parseInt(tid));
      console.log(JSON.stringify(season));
      break;
    }
    case "standings": {
      const [tid, sid] = args;
      const rows = await getStandings(parseInt(tid), parseInt(sid));
      console.log(JSON.stringify(rows));
      break;
    }
    case "find-match": {
      const [tid, sid, home, away] = args;
      const match = await findMatchByTeams(parseInt(tid), parseInt(sid), home, away);
      console.log(JSON.stringify(match));
      break;
    }
    case "match-details": {
      const [gid] = args;
      const details = await getMatchDetails(parseInt(gid));
      console.log(JSON.stringify(details));
      break;
    }
    case "pregame-form": {
      const [gid] = args;
      const form = await getPregameForm(parseInt(gid));
      console.log(JSON.stringify(form));
      break;
    }
    case "h2h": {
      const [gid] = args;
      const h2h = await getH2H(parseInt(gid));
      console.log(JSON.stringify(h2h));
      break;
    }
    case "referee-stats": {
      const [rid] = args;
      const stats = await getRefereeStats(parseInt(rid));
      console.log(JSON.stringify(stats));
      break;
    }
    case "team-stats": {
      const [teamId, tid, sid] = args;
      const stats = await getTeamStats(parseInt(teamId), parseInt(tid), parseInt(sid));
      console.log(JSON.stringify(stats));
      break;
    }
    case "incidents": {
      const [gid] = args;
      const incs = await getMatchIncidents(parseInt(gid));
      console.log(JSON.stringify(incs));
      break;
    }
    case "full-preview": {
      const [tid, sidOrYear, home, away] = args;
      const tournamentId = parseInt(tid);

      let seasonId;
      if (sidOrYear && sidOrYear.length <= 4 && /^\d{4}$/.test(sidOrYear)) {
        const season = await getSeasonByYear(tournamentId, parseInt(sidOrYear));
        seasonId = season ? season.id : parseInt(sidOrYear);
      } else {
        const season = sidOrYear ? { id: parseInt(sidOrYear) } : await getLatestSeason(tournamentId);
        seasonId = season ? season.id : null;
      }
      if (!seasonId) {
        console.log(JSON.stringify({ error: "Season not found" }));
        break;
      }

      const result = { standings: [], match: null, details: {}, pregame_form: {}, h2h: {}, referee: {}, team_stats: {} };

      result.standings = await getStandings(tournamentId, seasonId);
      await sleep(600);

      const match = await findMatchByTeams(tournamentId, seasonId, home, away);
      if (match) {
        result.match = match;
        await sleep(600);

        result.details = await getMatchDetails(match.game_id);
        await sleep(600);

        result.pregame_form = await getPregameForm(match.game_id);
        await sleep(600);

        result.h2h = await getH2H(match.game_id);
        await sleep(600);

        if (result.details.referee?.name) {
          const refSearch = await searchEntity(result.details.referee.name, "referee");
          if (refSearch.length > 0) {
            await sleep(600);
            result.referee = await getRefereeStats(refSearch[0].id);
          }
        }

        const homeTeamId = result.standings.find((r) => r.team.toLowerCase().includes(home.toLowerCase()))?.team_id;
        const awayTeamId = result.standings.find((r) => r.team.toLowerCase().includes(away.toLowerCase()))?.team_id;
        if (homeTeamId) {
          await sleep(600);
          result.team_stats.home = await getTeamStats(homeTeamId, tournamentId, seasonId);
        }
        if (awayTeamId) {
          await sleep(600);
          result.team_stats.away = await getTeamStats(awayTeamId, tournamentId, seasonId);
        }
      }

      console.log(JSON.stringify(result));
      break;
    }
    default:
      console.error(
        "Usage: node sofa_api.js <command> [args]\nCommands: search, seasons, standings, find-match, match-details, pregame-form, h2h, referee-stats, team-stats, incidents, full-preview"
      );
      process.exit(1);
  }
}

main().catch(console.error);
