const ASSETS_DIR = "./survivor_files";
const DATA_URL = "./storage/data.json";
const TOTAL_EPISODES = 13;

let appData = null;
let selectedEpisode = 1;

function cssTextShadow(borderColor) {
  const offsets = [
    [-3, 0],
    [3, 0],
    [0, -3],
    [0, 3],
    [-2, -2],
    [-2, 2],
    [2, -2],
    [2, 2]
  ];
  return offsets.map(([x, y]) => `${x}px ${y}px 0 ${borderColor}`).join(", ");
}

function getEliminatedThroughEpisode(data, episodeNumber) {
  const eliminated = new Set();
  const eliminationsByEpisode = data.eliminations_by_episode || {};

  for (let ep = 1; ep <= episodeNumber; ep++) {
    const names = eliminationsByEpisode[String(ep)] || [];
    names.forEach((name) => eliminated.add(name));
  }

  return eliminated;
}

function renderCard(player, eliminatedNames) {
  const isEliminated = eliminatedNames.has(player.name);

  const card = document.createElement("article");
  card.className = `card${isEliminated ? " eliminated" : ""}`;

  const imageWrap = document.createElement("div");
  imageWrap.className = "image-wrap";

  if (player.image) {
    const img = document.createElement("img");
    img.src = `${ASSETS_DIR}/${player.image}`;
    img.alt = player.name;
    img.loading = "lazy";
    imageWrap.appendChild(img);
  } else {
    const missing = document.createElement("div");
    missing.className = "missing-image";
    missing.textContent = "No image found";
    imageWrap.appendChild(missing);
  }

  if (isEliminated) {
    const stamp = document.createElement("div");
    stamp.className = "stamp";
    stamp.textContent = "ELIMINATED";
    imageWrap.appendChild(stamp);
  }

  const nameDiv = document.createElement("div");
  nameDiv.className = "name";
  nameDiv.textContent = player.name;

  card.appendChild(imageWrap);
  card.appendChild(nameDiv);

  return card;
}

function renderGroup(groupName, players, data, eliminatedNames) {
  const section = document.createElement("section");
  section.className = "tribe";
  section.style.setProperty("--tribe-bg", data.team_colors[groupName] || "#888");

  const style = data.team_name_styles[groupName] || {
    border: "#000000",
    fill: "#ffffff"
  };

  const title = document.createElement("h2");
  title.className = "tribe-title";
  title.textContent = groupName;
  title.style.color = style.fill;
  title.style.textShadow = cssTextShadow(style.border);

  const grid = document.createElement("div");
  grid.className = "card-grid";

  players.forEach((player) => {
    grid.appendChild(renderCard(player, eliminatedNames));
  });

  section.appendChild(title);
  section.appendChild(grid);

  return section;
}

function renderEpisodeButtons() {
  const nav = document.querySelector("#episode-nav");
  if (!nav) return;

  nav.innerHTML = "";

  for (let ep = 1; ep <= TOTAL_EPISODES; ep++) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `episode-bubble${ep === selectedEpisode ? " active" : ""}`;
    button.textContent = ep;
    button.setAttribute("aria-label", `Episode ${ep}`);

    button.addEventListener("click", () => {
      selectedEpisode = ep;
      renderPage();
    });

    nav.appendChild(button);
  }
}

function renderPage() {
  if (!appData) return;

  document.title = appData.title || "Survivor";
  document.querySelector("#page-title").textContent = appData.title || "Survivor";

  const episodeLabel = document.querySelector("#episode-label");
  if (episodeLabel) {
    episodeLabel.textContent = `Showing eliminations through Episode ${selectedEpisode}`;
  }

  renderEpisodeButtons();

  const container = document.querySelector("#content");
  container.innerHTML = "";

  const eliminatedNames = getEliminatedThroughEpisode(appData, selectedEpisode);

  Object.entries(appData.groups || {}).forEach(([groupName, players]) => {
    container.appendChild(renderGroup(groupName, players, appData, eliminatedNames));
  });
}

async function init() {
  const response = await fetch(DATA_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load ${DATA_URL}: ${response.status}`);
  }

  appData = await response.json();
  selectedEpisode = 1; // always start on episode 1
  renderPage();
}

init().catch((err) => {
  console.error(err);
  const container = document.querySelector("#content");
  if (container) {
    container.innerHTML = `
      <div style="padding:20px; background:#fff3f3; color:#a40000; border:1px solid #e0b4b4; border-radius:12px;">
        Failed to load page data.
      </div>
    `;
  }
});