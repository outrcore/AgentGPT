async function fetchData() {
  const response = await fetch("https://api.the-odds-api.com/v4/sports/soccer_efl_champ/odds?apiKey=5be2f524de74063d69c0210e25ab1276&regions=eu&markets=h2h,spreads,totals&dateFormat=iso&oddsFormat=american");
  const data = await response.json();
  displayData(data);
}

function displayData(data) {
  const allBookmakers = data.flatMap(game => game.bookmakers.map(bookmaker => ({ key: bookmaker.key, title: bookmaker.title }))).filter((value, index, self) => self.findIndex(item => item.key === value.key) === index);

  const marketContainers = {
    h2h: "betting-container-moneyline",
    spreads: "betting-container-points",
    totals: "betting-container-totals",
  };

  const marketNames = {
    h2h: "Moneyline",
    spreads: "Spreads",
    totals: "Totals",
  };

  Object.keys(marketContainers).forEach(marketKey => {
    let table = "<table><tr><th>Event Time</th><th>Event</th><th>Market</th><th>Bet Outcome</th><th>Best Odds</th><th>Pinnacle</th><th>Market Width</th><th>No-Vig</th><th>Avg Odds</th>";
    allBookmakers.forEach(bookmaker => {
      table += `<th>${bookmaker.title}</th>`;
    });
    table += "</tr>";

    data.forEach(game => {
      const gameTime = new Date(game.commence_time).toLocaleString();
      const eventTitle = `${game.home_team} vs ${game.away_team}`;

      let marketOdds = [];
      game.bookmakers.forEach(bookmaker => {
        const market = bookmaker.markets.find(m => m.key === marketKey);
        if (market) {
          marketOdds.push(market.outcomes);
        } else {
          marketOdds.push([]);
        }
      });

      const bestOdds = calculateBestOdds(marketOdds);
      const pinnacleOdds = calculatePinnacleOdds(marketOdds, allBookmakers);
      const noVigOdds = calculateNoVigOdds(pinnacleOdds);
      const marketWidth = calculateMarketWidth(marketOdds);
      const avgOdds = calculateAvgOdds(marketOdds);

      const outcomes = Array.from(new Set(marketOdds.flatMap(odds => odds.map(o => o.name))));

      outcomes.forEach((outcome, outcomeIndex) => {
        const rowSpanValue = outcomeIndex === 0 ? `rowspan="${outcomes.length}"` : "";
        table += `<tr>${outcomeIndex === 0 ? `<td ${rowSpanValue}>${gameTime}</td><td ${rowSpanValue}>${eventTitle}</td><td ${rowSpanValue}>${marketNames[marketKey]}</td>` : ''}<td>${outcome}${marketKey !== 'h2h' ? ` (${game.markets.find(m => m.key === marketKey).points})` : ''}</td>`;
        marketOdds.forEach((odds, bookmakerIndex) => {
          const odd = odds.find(o => o.name === outcome);
          table += `<td>${odd ? odd.price : '-'}</td>`;
          if (outcomeIndex === 0) {
            // Moved these calculations outside of the loop
            const bestOddsValue = bestOdds.odds;
            const pinnacleOddsValue = calculatePinnacleOdds(marketOdds, allBookmakers);
            const noVigOddsValue = calculateNoVigOdds(pinnacleOddsValue);
            const marketWidthValue = calculateMarketWidth(marketOdds);
            const avgOddsValue = calculateAvgOdds(marketOdds);

            if (bookmakerIndex === bestOdds.bookmakerIndex) {
              table += `<td ${rowSpanValue}>${bestOddsValue}</td>`;
            } else if (bookmakerIndex === allBookmakers.findIndex(bookmaker => bookmaker.key === 'pinnacle')) {
              table += `<td ${rowSpanValue}>${pinnacleOddsValue}</td>`;
            } else if (bookmakerIndex === allBookmakers.findIndex(bookmaker => bookmaker.key === 'no-vig')) {
              table += `<td ${rowSpanValue}>${noVigOddsValue}</td>`;
            } else if (bookmakerIndex === allBookmakers.findIndex(bookmaker => bookmaker.key === 'market-width')) {
              table += `<td ${rowSpanValue}>${marketWidthValue}</td>`;
            } else if (bookmakerIndex === allBookmakers.findIndex(bookmaker => bookmaker.key === 'avg-odds')) {
              table += `<td ${rowSpanValue}>${avgOddsValue}</td>`;
            }
          }
        });
        table += "</tr>";
      });
    });
    table += "</table>";
    document.querySelector(`#${marketContainers[marketKey]}`).innerHTML = table;
  });
}

function calculateBestOdds(marketOdds) {
  let bestOdds = null;
  let bestBookmaker = '';

  marketOdds.forEach((odds, index) => {
    odds.forEach(outcome => {
      if (!bestOdds || outcome.price > bestOdds) {
        bestOdds = outcome.price;
        bestBookmaker = outcome.name;
      }
    });
  });

  return { odds: bestOdds, bookmaker: bestBookmaker };
}

function calculatePinnacleOdds(marketOdds, allBookmakers) {
  const pinnacleIndex = allBookmakers.findIndex(bookmaker => bookmaker.key === 'pinnacle');
  if (pinnacleIndex === -1) return 'N/A';

  const pinnacleOdds = marketOdds[pinnacleIndex];
  if (!pinnacleOdds) return 'N/A'; // Add this line to check if pinnacleOdds is undefined

  return pinnacleOdds.map(o => `${o.name}: ${o.price}`).join(', ');
}


function calculateNoVigOdds(pinnacleOdds) {
  // Assuming pinnacleOdds is a string in the format "Outcome1: Price1, Outcome2: Price2"
  const oddsArray = pinnacleOdds.split(', ').map(o => parseFloat(o.split(': ')[1]));
  const noVigOddsArray = oddsArray.map(odds => odds / (1 + (odds - 1) * 0.05));
  return noVigOddsArray.join(', ');
}

function calculateMarketWidth(marketOdds) {
  // Calculate market width here
}

function calculateAvgOdds(marketOdds) {
  let sum = 0;
  let count = 0;

  marketOdds.forEach(odds => {
    odds.forEach(outcome => {
      sum += outcome.price;
      count++;
    });
  });

  return count ? (sum / count).toFixed(0) : 'N/A';
}
// ... (Rest of the code remains unchanged)

function populateBookmakerDropdown(allBookmakers) {
  const dropdownContent = document.getElementById("bookmaker-dropdown");
  allBookmakers.forEach(bookmaker => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `bookmaker-${bookmaker.key}`;
    checkbox.name = bookmaker.key;
    checkbox.value = bookmaker.key;
    checkbox.onchange = filterTable;
    
    const label = document.createElement("label");
    label.htmlFor = `bookmaker-${bookmaker.key}`;
    label.textContent = bookmaker.title;

    dropdownContent.appendChild(checkbox);
    dropdownContent.appendChild(label);
    dropdownContent.appendChild(document.createElement("br"));
  });
}

function filterTable() {
  const teamFilter = document.getElementById("team-filter").value.toLowerCase();
  const dateFilter = document.getElementById("date-filter").value;
  const bookmakerFilters = Array.from(document.querySelectorAll("#bookmaker-dropdown input[type='checkbox']")).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);

  Array.from(document.querySelectorAll(".table-container")).forEach(container => {
    const table = container.querySelector("table");
    if (!table) return;

    Array.from(table.querySelectorAll("tr")).forEach((row, rowIndex) => {
      if (rowIndex === 0) return; // Skip header row

      let displayRow = true;

      if (teamFilter) {
        const eventCell = row.querySelector("td:first-child");
        if (eventCell && !eventCell.textContent.toLowerCase().includes(teamFilter)) {
          displayRow = false;
        }
      }

      if (bookmakerFilters.length) {
        const bookmakerKeys = Array.from(row.querySelectorAll("td:nth-child(n+3):nth-child(-n+3)")).map(cell => cell.textContent.split(':')[0]);
        if (!bookmakerFilters.some(filter => bookmakerKeys.includes(filter))) {
          displayRow = false;
        }
      }

      if (dateFilter) {
        const eventCell = row.querySelector("td:first-child");
        const eventDate = new Date(eventCell.textContent.split('|')[1].trim());
        const filterDate = new Date(dateFilter);
        if (!(eventDate.toDateString() === filterDate.toDateString())) {
          displayRow = false;
        }
      }

      row.style.display = displayRow ? "" : "none";
    });
  });
}


fetchData();
