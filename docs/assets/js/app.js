function formatSignedNumber(value) {
  if (value > 0) {
    return `+${value}`;
  }

  return `${value}`;
}


function createRankChangeElement(rankChange) {
  const container = document.createElement("span");

  if (rankChange > 0) {
    container.className = "rank-change rank-change-up";
    container.textContent = `↑ ${rankChange}`;
  } else if (rankChange < 0) {
    container.className = "rank-change rank-change-down";
    container.textContent = `↓ ${Math.abs(rankChange)}`;
  } else {
    container.className = "rank-change rank-change-neutral";
    container.textContent = "—";
  }

  return container;
}


function createPointsChangeElement(pointsChange) {
  const container = document.createElement("span");

  if (pointsChange > 0) {
    container.className = "points-change points-change-positive";
  } else if (pointsChange < 0) {
    container.className = "points-change points-change-negative";
  } else {
    container.className = "points-change points-change-neutral";
  }

  container.textContent = formatSignedNumber(pointsChange);

  return container;
}


function createTeamElement(row) {
  const container = document.createElement("div");
  container.className = "team-cell";

  const logo = document.createElement("img");
  logo.className = "team-logo";
  logo.src = row.logo;
  logo.alt = `${row.team} logo`;
  logo.loading = "lazy";

  logo.onerror = () => {
    logo.style.display = "none";

    const fallback = document.createElement("span");
    fallback.className = "team-logo-placeholder";
    fallback.textContent = row.team
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((word) => word[0])
      .join("")
      .toUpperCase();

    container.prepend(fallback);
  };

  const name = document.createElement("span");
  name.className = "team-name";
  name.textContent = row.team;

  container.appendChild(logo);
  container.appendChild(name);

  return container;
}

function createLeagueElement(row) {
  const container = document.createElement("div");
  container.className = "league-cell";

  const logo = document.createElement("img");
  logo.className = "league-logo";
  logo.src = row.league_logo;
  logo.alt = `${row.league} logo`;
  logo.loading = "lazy";

  logo.onerror = () => {
    logo.style.display = "none";

    const fallback = document.createElement("span");
    fallback.className = "league-fallback";
    fallback.textContent = row.league;
    container.appendChild(fallback);
  };

  container.appendChild(logo);

  return container;
}

async function loadRankings() {
  const tableBody = document.getElementById("ranking-table-body");

  try {
    const response = await fetch("data/rankings.json");

    if (!response.ok) {
      throw new Error(`Could not load rankings.json: ${response.status}`);
    }

    const rankings = await response.json();

    tableBody.innerHTML = "";

    rankings.forEach((row) => {
      const tableRow = document.createElement("tr");

      const rankCell = document.createElement("td");
      rankCell.textContent = row.rank;

      const movementCell = document.createElement("td");
      movementCell.appendChild(createRankChangeElement(row.rank_change));

      const teamCell = document.createElement("td");
      teamCell.appendChild(createTeamElement(row));

      const leagueCell = document.createElement("td");
      leagueCell.appendChild(createLeagueElement(row));

      const pointsCell = document.createElement("td");
      pointsCell.textContent = row.points;

      const pointsChangeCell = document.createElement("td");
      pointsChangeCell.appendChild(createPointsChangeElement(row.points_change));

      tableRow.appendChild(rankCell);
      tableRow.appendChild(movementCell);
      tableRow.appendChild(teamCell);
      tableRow.appendChild(leagueCell);
      tableRow.appendChild(pointsCell);
      tableRow.appendChild(pointsChangeCell);

      tableBody.appendChild(tableRow);
    });
  } catch (error) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6">
          Unable to load ranking data.
        </td>
      </tr>
    `;

    console.error(error);
  }
}


loadRankings();