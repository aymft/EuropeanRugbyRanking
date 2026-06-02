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

      const teamCell = document.createElement("td");
      teamCell.textContent = row.team;

      const pointsCell = document.createElement("td");
      pointsCell.textContent = row.points;

      tableRow.appendChild(rankCell);
      tableRow.appendChild(teamCell);
      tableRow.appendChild(pointsCell);

      tableBody.appendChild(tableRow);
    });
  } catch (error) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="3">
          Unable to load ranking data.
        </td>
      </tr>
    `;

    console.error(error);
  }
}

loadRankings();