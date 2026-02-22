const DATA = [
  { id: "A-101", name: "玄関ホール", tag: "entrance", building: "north", cell: 2, x: 22, y: 28 },
  { id: "A-102", name: "受付カウンター", tag: "entrance", building: "north", cell: 7, x: 34, y: 34 },
  { id: "B-201", name: "避難経路1", tag: "evacuation", building: "south", cell: 18, x: 72, y: 40 },
  { id: "B-202", name: "避難階段", tag: "evacuation", building: "south", cell: 23, x: 78, y: 62 },
  { id: "E-301", name: "分電盤", tag: "electrical", building: "north", cell: 14, x: 49, y: 49 },
  { id: "E-302", name: "電源室", tag: "electrical", building: "south", cell: 20, x: 62, y: 57 },
];

const state = {
  keyword: "",
  building: "all",
  quickTag: "",
  selectedId: "",
  viewMode: "split",
};

const els = {
  form: document.getElementById("searchForm"),
  keyword: document.getElementById("keyword"),
  building: document.getElementById("building"),
  clearBtn: document.getElementById("clearBtn"),
  resultMeta: document.getElementById("resultMeta"),
  resultList: document.getElementById("resultList"),
  drawingGrid: document.getElementById("drawingGrid"),
  mapBox: document.getElementById("mapBox"),
  selectionInfo: document.getElementById("selectionInfo"),
  canvasArea: document.getElementById("canvasArea"),
  tabs: Array.from(document.querySelectorAll(".tab")),
  chips: Array.from(document.querySelectorAll(".chip")),
};

function createStaticView() {
  els.drawingGrid.innerHTML = "";
  for (let i = 1; i <= 25; i += 1) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.dataset.index = String(i);
    cell.textContent = i;
    els.drawingGrid.appendChild(cell);
  }

  els.mapBox.innerHTML = "";
  DATA.forEach((row) => {
    const pin = document.createElement("div");
    pin.className = "pin";
    pin.dataset.id = row.id;
    pin.style.left = `${row.x}%`;
    pin.style.top = `${row.y}%`;
    pin.title = `${row.id} ${row.name}`;
    els.mapBox.appendChild(pin);
  });
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

function renderResults() {
  const rows = getFilteredData();
  els.resultMeta.textContent = `検索結果: ${rows.length}件`;
  els.resultList.innerHTML = "";

  if (!rows.length) {
    const li = document.createElement("li");
    li.className = "result-item";
    li.textContent = "該当なし。キーワードや建物条件を変更してください。";
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

    if (!state.selectedId && idx === 0) {
      state.selectedId = row.id;
    }
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
  Array.from(els.drawingGrid.querySelectorAll(".cell")).forEach((cell) => {
    cell.classList.remove("target");
  });
  Array.from(els.mapBox.querySelectorAll(".pin")).forEach((pin) => {
    pin.classList.remove("target");
  });

  if (!item) {
    els.selectionInfo.textContent = "項目を選択すると、図面・地図の該当箇所がここに表示されます。";
    return;
  }

  const targetCell = els.drawingGrid.querySelector(`.cell[data-index="${item.cell}"]`);
  if (targetCell) targetCell.classList.add("target");

  const targetPin = els.mapBox.querySelector(`.pin[data-id="${item.id}"]`);
  if (targetPin) targetPin.classList.add("target");

  const tagLabel = {
    entrance: "玄関系",
    evacuation: "避難導線",
    electrical: "電気設備",
  }[item.tag];

  els.selectionInfo.innerHTML = `
    <strong>${item.id} ${item.name}</strong><br>
    図面セル: ${item.cell} / 地図座標: (${item.x}, ${item.y}) / 区分: ${tagLabel}
  `;
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

  els.chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      state.quickTag = chip.dataset.filter === state.quickTag ? "" : chip.dataset.filter;
      state.selectedId = "";
      renderResults();
      els.chips.forEach((c) => c.classList.toggle("active", c === chip && state.quickTag));
    });
  });
}

createStaticView();
bindEvents();
applyViewMode();
renderResults();
