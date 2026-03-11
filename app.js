const ASSETS_DIR = "survivor_files";

function cssTextShadow(borderColor) {
  const offsets = [
    [-3,0],[3,0],[0,-3],[0,3],
    [-2,-2],[-2,2],[2,-2],[2,2]
  ];
  return offsets.map(([x,y]) => `${x}px ${y}px 0 ${borderColor}`).join(",");
}

function findImage(keyword, files) {
  keyword = keyword.toLowerCase();
  return files.find(f => f.toLowerCase().includes(keyword));
}

function renderCard(name, imagePath, eliminated) {

  const card = document.createElement("article");
  card.className = "card" + (eliminated ? " eliminated" : "");

  const imageWrap = document.createElement("div");
  imageWrap.className = "image-wrap";

  if (imagePath) {
    const img = document.createElement("img");
    img.src = imagePath;
    img.alt = name;
    imageWrap.appendChild(img);
  } else {
    const missing = document.createElement("div");
    missing.className = "missing-image";
    missing.innerText = "No image found";
    imageWrap.appendChild(missing);
  }

  if (eliminated) {
    const stamp = document.createElement("div");
    stamp.className = "stamp";
    stamp.innerText = "ELIMINATED";
    imageWrap.appendChild(stamp);
  }

  const nameDiv = document.createElement("div");
  nameDiv.className = "name";
  nameDiv.innerText = name;

  card.appendChild(imageWrap);
  card.appendChild(nameDiv);

  return card;
}

function renderGroup(groupName, names, data, imageFiles) {

  const section = document.createElement("section");
  section.className = "tribe";
  section.style.setProperty("--tribe-bg", data.team_colors[groupName]);

  const style = data.team_name_styles[groupName];

  const title = document.createElement("h2");
  title.className = "tribe-title";
  title.innerText = groupName;
  title.style.color = style.fill;
  title.style.textShadow = cssTextShadow(style.border);

  const grid = document.createElement("div");
  grid.className = "card-grid";

  names.forEach(name => {

    const keyword = data.name_map[name];
    const imageFile = findImage(keyword, imageFiles);
    const imagePath = imageFile ? `${ASSETS_DIR}/${imageFile}` : null;

    const card = renderCard(
      name,
      imagePath,
      data.eliminated.includes(name)
    );

    grid.appendChild(card);
  });

  section.appendChild(title);
  section.appendChild(grid);

  return section;
}

async function init() {

  const response = await fetch("./storage/data.json");
  const data = await response.json();

  document.title = data.title;
  document.querySelector("#page-title").innerText = data.title;

  // load image list
  const imgResponse = await fetch(`${ASSETS_DIR}/`);
  const text = await imgResponse.text();

  const imageFiles = [...text.matchAll(/href="([^"]+)"/g)]
    .map(m => m[1])
    .filter(f => f.match(/\.(png|jpg|jpeg|webp)$/i));

  const container = document.querySelector("#content");

  Object.entries(data.groups).forEach(([group, names]) => {
    const section = renderGroup(group, names, data, imageFiles);
    container.appendChild(section);
  });

}

init();