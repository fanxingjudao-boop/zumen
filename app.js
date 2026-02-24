const DATA = [
  { id: "A-101", name: "玄関ホール", tag: "entrance", building: "north", cell: 2, lat: 35.1706, lon: 136.8808 },
  { id: "A-102", name: "受付カウンター", tag: "entrance", building: "north", cell: 7, lat: 35.1704, lon: 136.8814 },
  { id: "B-201", name: "避難経路1", tag: "evacuation", building: "south", cell: 18, lat: 35.1689, lon: 136.8825 },
  { id: "B-202", name: "避難階段", tag: "evacuation", building: "south", cell: 23, lat: 35.1684, lon: 136.8832 },
  { id: "E-301", name: "分電盤", tag: "electrical", building: "north", cell: 14, lat: 35.1713, lon: 136.8821 },
  { id: "E-302", name: "電源室", tag: "electrical", building: "south", cell: 20, lat: 35.1697, lon: 136.8839 },
];

const initialParams = new URLSearchParams(window.location.search);

const state = {
  keyword: "",
  building: "all",
  quickTag: "",
  selectedId: "",
  viewMode: "split",
  mapMode: initialParams.get("mapMode") || "offline",
};

const els = {
  form: document.getElementById("searchForm"),
  keyword: document.getElementById("keyword"),
  building: document.getElementById("building"),
  mapMode: document.getElementById("mapMode"),
  clearBtn: document.getElementById("clearBtn"),
  resultMeta: document.getElementById("resultMeta"),
  resultList: document.getElementById("resultList"),
  drawingGrid: document.getElementById("drawingGrid"),
  mapFrame: document.getElementById("mapFrame"),
  selectionInfo: document.getElementById("selectionInfo"),
  canvasArea: document.getElementById("canvasArea"),
  tabs: Array.from(document.querySelectorAll(".tab")),
  chips: Array.from(document.querySelectorAll(".chip")),
  openBlueprintBtn: document.getElementById("openBlueprintBtn"),
  openMapNewTabBtn: document.getElementById("openMapNewTabBtn"),
};

function createDrawingGrid() {
  els.drawingGrid.innerHTML = "";
  for (let i = 1; i <= 25; i += 1) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.dataset.index = String(i);
    cell.textContent = i;
    els.drawingGrid.appendChild(cell);
  }
}

function getFilteredData() {
  return DATA.filter((item) => {
    const kw = state.keyword.trim().toLowerCase();
    const target = `${item.id} ${item.name}`.toLowerCase();
    const keywordMatch = !kw || target.includes(kw);
    const buildingMatch = state.building === "all" || item.building === state.building;
    const tagMatch = !state.quickTag || item.tag === state.quickTag;
    return keywordMatch && buildingMatch && tagMatch;
  });
}

function mapUrl(item) {
  if (!item) return "nearby_map/app/?mode=offline";
  const params = new URLSearchParams({
    mode: state.mapMode,
    lat: String(item.lat),
    lon: String(item.lon),
    z: "16",
    marker: `${item.id} ${item.name}`,
    blueprintId: item.id,
    building: item.building,
    source: "root",
  });
  return `nearby_map/app/?${params.toString()}`;
}

function selectedItem() {
  return getFilteredData().find((r) => r.id === state.selectedId) || null;
}

function renderResults() {
  const rows = getFilteredData();
  els.resultMeta.textContent = `検索結果: ${rows.length}件`;
  els.resultList.innerHTML = "";

  if (!rows.length) {
    const li = document.createElement("li");
    li.className = "result-item";
    li.textContent = "該当なし。条件を変更してください。";
    els.resultList.appendChild(li);
    highlightSelection(null);
    return;
  }

  rows.forEach((row, idx) => {
    const li = document.createElement("li");
    li.className = `result-item${state.selectedId === row.id ? " active" : ""}`;
    li.innerHTML = `
      <button type="button" data-id="${row.id}" aria-label="${row.id} ${row.name} を表示">
        <strong>${row.id}</strong> ${row.name}
        <small>${row.building === "north" ? "北棟" : "南棟"} / ${row.tag}</small>
      </button>
    `;
    els.resultList.appendChild(li);

    if (!state.selectedId && idx === 0) state.selectedId = row.id;
  });

  const selected = rows.find((r) => r.id === state.selectedId) || rows[0];
  if (selected) {
    state.selectedId = selected.id;
    highlightSelection(selected);
    updateActiveResult();
  }
}

function updateActiveResult() {
  Array.from(els.resultList.querySelectorAll(".result-item")).forEach((el) => {
    const btn = el.querySelector("button");
    if (!btn) return;
    el.classList.toggle("active", btn.dataset.id === state.selectedId);
  });
}

function highlightSelection(item) {
  Array.from(els.drawingGrid.querySelectorAll(".cell")).forEach((cell) => cell.classList.remove("target"));

  if (!item) {
    els.mapFrame.src = mapUrl(null);
    els.selectionInfo.textContent = "項目を選択すると、図面セル・地図中心・位置マーカーを同期表示します。";
    return;
  }

  const targetCell = els.drawingGrid.querySelector(`.cell[data-index="${item.cell}"]`);
  if (targetCell) targetCell.classList.add("target");

  els.mapFrame.src = mapUrl(item);
  const tagLabel = { entrance: "玄関", evacuation: "避難", electrical: "電気" }[item.tag] || item.tag;
  els.selectionInfo.innerHTML = `<strong>${item.id} ${item.name}</strong><br>図面セル: ${item.cell} / 建物: ${item.building === "north" ? "北棟" : "南棟"} / 種別: ${tagLabel}`;
}

function applyViewMode() {
  els.canvasArea.classList.remove("split", "drawing-only", "map-only");
  if (state.viewMode === "drawing") els.canvasArea.classList.add("drawing-only");
  else if (state.viewMode === "map") els.canvasArea.classList.add("map-only");
  else els.canvasArea.classList.add("split");

  els.tabs.forEach((tab) => {
    const active = tab.dataset.view === state.viewMode;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
}

function bindEvents() {
  els.form.addEventListener("submit", (e) => {
    e.preventDefault();
    state.keyword = els.keyword.value;
    state.building = els.building.value;
    state.mapMode = els.mapMode.value;
    state.selectedId = "";
    renderResults();
  });

  els.clearBtn.addEventListener("click", () => {
    state.keyword = "";
    state.building = "all";
    state.quickTag = "";
    state.selectedId = "";
    els.keyword.value = "";
    els.building.value = "all";
    els.mapMode.value = "offline";
    state.mapMode = "offline";
    renderResults();
  });

  els.resultList.addEventListener("click", (e) => {
    const button = e.target.closest("button[data-id]");
    if (!button) return;
    state.selectedId = button.dataset.id;
    const item = getFilteredData().find((r) => r.id === state.selectedId);
    highlightSelection(item || null);
    updateActiveResult();
  });

  els.tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      state.viewMode = tab.dataset.view;
      applyViewMode();
    });
  });

  els.mapMode.addEventListener("change", () => {
    state.mapMode = els.mapMode.value;
    highlightSelection(selectedItem());
  });

  els.chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      state.quickTag = chip.dataset.filter === state.quickTag ? "" : chip.dataset.filter;
      state.selectedId = "";
      renderResults();
      els.chips.forEach((c) => c.classList.toggle("active", c === chip && state.quickTag));
    });
  });

  els.openBlueprintBtn?.addEventListener("click", () => {
    const item = selectedItem();
    const q = new URLSearchParams({
      keyword: item ? item.id : state.keyword,
      building: item ? item.building : state.building,
      source: "root",
    });
    window.open(`nearby_map/blueprint_map/app/?${q.toString()}`, "_blank");
  });

  els.openMapNewTabBtn?.addEventListener("click", () => {
    const item = selectedItem();
    window.open(mapUrl(item), "_blank");
  });
}

if (initialParams.get("keyword")) {
  state.keyword = initialParams.get("keyword") || "";
  if (els.keyword) els.keyword.value = state.keyword;
}
if (initialParams.get("building") && els.building) {
  state.building = initialParams.get("building");
  els.building.value = state.building;
}
if (els.mapMode) els.mapMode.value = state.mapMode;

createDrawingGrid();
bindEvents();
applyViewMode();
renderResults();
