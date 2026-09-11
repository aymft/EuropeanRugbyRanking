const LIVE_RESULTS_URL = "data/live_results.json";
const RANKINGS_URL = "data/rankings.json";

const COMPETITION_LOGOS = {
  TOP14: "assets/img/competitions/top14.png",
  URC: "assets/img/competitions/urc.svg",
  PREMIERSHIP: "assets/img/competitions/premiership.png",
  CHAMPIONS_CUP: "assets/img/competitions/champions-cup.svg",
  CHALLENGE_CUP: "assets/img/competitions/challenge-cup.svg",
};

let refreshTimer;


function createElement(tagName, className, text) {
  const element = document.createElement(tagName);

  if (className) {
    element.className = className;
  }

  if (text !== undefined) {
    element.textContent = text;
  }

  return element;
}


function initials(teamName) {
  return teamName
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}


function buildRankingLookup(rankings) {
  const lookup = new Map();

  rankings.forEach((row) => {
    if (row.club_id) {
      lookup.set(`id:${row.club_id}`, row);
    }

    if (row.team) {
      lookup.set(`name:${row.team}`, row);
    }
  });

  return lookup;
}


function findRanking(match, side, rankingLookup) {
  const clubId = match[`${side}_club_id`];
  const teamName = match[`${side}_team`];

  return (
    (clubId && rankingLookup.get(`id:${clubId}`)) ||
    rankingLookup.get(`name:${teamName}`) ||
    null
  );
}


function statusDetails(match) {
  if (match.status === "live") {
    return {
      className: "status-live",
      label: match.minute === null || match.minute === undefined
        ? "LIVE"
        : `LIVE · ${match.minute}'`,
    };
  }

  if (match.status === "finished") {
    return { className: "status-finished", label: "FULL TIME" };
  }

  if (match.status === "scheduled") {
    return { className: "status-scheduled", label: "UPCOMING" };
  }

  return {
    className: "status-unknown",
    label: (match.raw_status || match.status || "STATUS UNKNOWN").toUpperCase(),
  };
}


function formatScore(match) {
  if (match.status === "scheduled") {
    return "VS";
  }

  if (match.home_score === null || match.home_score === undefined ||
      match.away_score === null || match.away_score === undefined) {
    return "VS";
  }

  return `${match.home_score}–${match.away_score}`;
}


function formatKickoff(match) {
  if (!match.kickoff_utc) {
    return match.kickoff_display || "Kick-off TBC";
  }

  const date = new Date(match.kickoff_utc);

  if (Number.isNaN(date.getTime())) {
    return match.kickoff_display || match.kickoff_utc;
  }

  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Paris",
    weekday: "long",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}


function formatWeekendRange(data) {
  const start = new Date(data.weekend_start);
  const exclusiveEnd = new Date(data.weekend_end);

  if (Number.isNaN(start.getTime()) || Number.isNaN(exclusiveEnd.getTime())) {
    return "Friday to Sunday";
  }

  const end = new Date(exclusiveEnd.getTime() - 1000);
  const dateFormatter = new Intl.DateTimeFormat("en-GB", {
    timeZone: data.timezone || "Europe/Paris",
    day: "numeric",
    month: "long",
  });

  const yearFormatter = new Intl.DateTimeFormat("en-GB", {
    timeZone: data.timezone || "Europe/Paris",
    year: "numeric",
  });

  return `${dateFormatter.format(start)}–${dateFormatter.format(end)} ${yearFormatter.format(end)}`;
}


function createLogo(teamName, ranking) {
  const wrapper = createElement("span", "match-team-logo-wrap");

  if (!ranking || !ranking.logo) {
    wrapper.appendChild(createElement("span", "match-team-logo-fallback", initials(teamName)));
    return wrapper;
  }

  const logo = createElement("img", "match-team-logo");
  logo.src = ranking.logo;
  logo.alt = `${teamName} logo`;
  logo.loading = "lazy";

  logo.addEventListener("error", () => {
    wrapper.replaceChildren(
      createElement("span", "match-team-logo-fallback", initials(teamName)),
    );
  }, { once: true });

  wrapper.appendChild(logo);
  return wrapper;
}


function createTeam(match, side, rankingLookup) {
  const isHome = side === "home";
  const teamName = match[`${side}_team`];
  const ranking = findRanking(match, side, rankingLookup);
  const team = createElement("div", `match-team match-team-${side}`);
  const details = createElement("div", "match-team-details");
  const rank = createElement(
    "span",
    ranking ? "match-rank" : "match-rank match-rank-unavailable",
    ranking ? `#${ranking.rank}` : "Unranked",
  );
  const name = createElement("div", "match-team-name");
  const nameText = createElement("span", "match-team-name-text", teamName);

  name.appendChild(nameText);
  details.appendChild(rank);
  details.appendChild(name);

  if (isHome) {
    team.appendChild(details);
    team.appendChild(createLogo(teamName, ranking));
  } else {
    team.appendChild(createLogo(teamName, ranking));
    team.appendChild(details);
  }

  return team;
}


function createMatch(match, rankingLookup) {
  const card = createElement("article", "match-card");
  const meta = createElement("div", "match-meta");
  const status = statusDetails(match);
  const statusElement = createElement(
    "span",
    `match-status ${status.className}`,
    status.label,
  );
  const kickoff = createElement("time", "match-kickoff", formatKickoff(match));

  if (match.kickoff_utc) {
    kickoff.dateTime = match.kickoff_utc;
  }

  meta.appendChild(kickoff);
  meta.appendChild(statusElement);

  if (match.venue) {
    meta.appendChild(createElement("span", "match-venue", match.venue));
  }

  const matchup = createElement("div", "matchup");
  const score = createElement("div", "match-score", formatScore(match));
  score.setAttribute(
    "aria-label",
    match.status === "scheduled"
      ? "versus"
      : `${match.home_score} to ${match.away_score}`,
  );

  matchup.appendChild(createTeam(match, "home", rankingLookup));
  matchup.appendChild(score);
  matchup.appendChild(createTeam(match, "away", rankingLookup));

  card.appendChild(meta);
  card.appendChild(matchup);

  return card;
}


function createCompetition(competition, rankingLookup) {
  const section = createElement("section", "competition-block");
  const heading = createElement("div", "competition-heading");
  const titleGroup = createElement("div", "competition-identity");
  const logo = createElement("img", "competition-logo");
  logo.src = COMPETITION_LOGOS[competition.code] || "";
  logo.alt = "";

  if (competition.code === "CHAMPIONS_CUP" || competition.code === "CHALLENGE_CUP") {
    logo.classList.add("competition-logo-wide");
  }
  const title = createElement("h2", "competition-title", competition.name);
  const matches = competition.matches || [];
  const count = createElement(
    "span",
    "competition-count",
    `${matches.length} match${matches.length === 1 ? "" : "es"}`,
  );

  titleGroup.appendChild(logo);
  titleGroup.appendChild(title);
  heading.appendChild(titleGroup);
  heading.appendChild(count);
  section.appendChild(heading);

  if (competition.error) {
    section.appendChild(
      createElement("p", "data-warning", `Data warning: ${competition.error}`),
    );
  }

  if (matches.length === 0) {
    section.appendChild(
      createElement("p", "empty-message", "No match scheduled in this competition this weekend."),
    );
    return section;
  }

  const list = createElement("div", "match-list");
  matches.forEach((match) => list.appendChild(createMatch(match, rankingLookup)));
  section.appendChild(list);

  return section;
}


function updateMeta(data) {
  const meta = document.getElementById("live-meta");
  const updateContainer = document.getElementById("live-update");
  const generatedAt = new Date(data.generated_at);
  const ageMinutes = Math.max(0, (Date.now() - generatedAt.getTime()) / 60000);
  const updateLabel = Number.isNaN(generatedAt.getTime())
    ? "Update time unavailable"
    : `Scores updated ${new Intl.DateTimeFormat("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        timeZone: data.timezone || "Europe/Paris",
      }).format(generatedAt)}`;

  meta.textContent = `${updateLabel} · automatic refresh every 2 minutes`;
  updateContainer.classList.toggle("is-stale", ageMinutes > 12);
  document.getElementById("weekend-range").textContent = formatWeekendRange(data);
}


async function loadWeekendMatches() {
  const container = document.getElementById("live-results");

  try {
    const cacheBuster = `t=${Date.now()}`;
    const [liveResponse, rankingsResponse] = await Promise.all([
      fetch(`${LIVE_RESULTS_URL}?${cacheBuster}`),
      fetch(`${RANKINGS_URL}?${cacheBuster}`),
    ]);

    if (!liveResponse.ok) {
      throw new Error(`Live results returned HTTP ${liveResponse.status}`);
    }

    if (!rankingsResponse.ok) {
      throw new Error(`Rankings returned HTTP ${rankingsResponse.status}`);
    }

    const [data, rankings] = await Promise.all([
      liveResponse.json(),
      rankingsResponse.json(),
    ]);
    const rankingLookup = buildRankingLookup(rankings);

    container.replaceChildren(
      ...data.competitions.map((competition) =>
        createCompetition(competition, rankingLookup)),
    );
    container.setAttribute("aria-busy", "false");
    updateMeta(data);

    window.clearTimeout(refreshTimer);
    refreshTimer = window.setTimeout(
      loadWeekendMatches,
      Math.max(30, Number(data.refresh_seconds) || 120) * 1000,
    );
  } catch (error) {
    container.replaceChildren(
      createElement(
        "section",
        "competition-block empty-message",
        "Unable to load the weekend matches. Please try again shortly.",
      ),
    );
    container.setAttribute("aria-busy", "false");
    document.getElementById("live-meta").textContent = "Scores temporarily unavailable";
    console.error(error);

    window.clearTimeout(refreshTimer);
    refreshTimer = window.setTimeout(loadWeekendMatches, 60000);
  }
}


loadWeekendMatches();
