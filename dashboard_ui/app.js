let chart;
const activeTags = new Set();
const colors = {};
const acked = [];
let unacked = [];

async function fetchData() {
  return (await fetch('/data')).json();
}

function updateInputs(r, ts) {
  document.getElementById('last-update').textContent = new Date(ts).toLocaleTimeString();
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  Object.entries(r).forEach(([tag, i]) => {
    const card = document.createElement('div');
    card.className = 'card ' + i.status + (activeTags.has(tag) ? ' active' : '');
    card.innerHTML = `<strong>${tag}</strong><br>${i.value}`;
    card.onclick = () => toggleTrend(tag);
    grid.appendChild(card);
  });
}

function updateDiagnostics(a, ts) {
  document.getElementById('last-diag').textContent = new Date(ts).toLocaleTimeString();
  a.forEach(m => {
    if (!acked.includes(m) && !unacked.includes(m)) unacked.push(m);
  });
  renderAlarms();
}

function renderAlarms() {
  const ul = document.getElementById('alarms');
  ul.innerHTML = '';
  unacked.forEach(m => {
    const li = document.createElement('li');
    li.textContent = m;
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-primary';
    btn.textContent = 'Ack';
    btn.onclick = () => ack(m);
    li.appendChild(btn);
    ul.appendChild(li);
  });
}

function ack(m) {
  acked.push(m);
  unacked = unacked.filter(x => x !== m);
  renderAlarms();
}

function setupChart() {
  const ctx = document.getElementById('trendChart').getContext('2d');
  chart = new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: { x: { display: true }, y: { beginAtZero: true } }
    }
  });
}

function updateTrends(r, ts) {
  const t = new Date(ts).toLocaleTimeString();
  chart.data.labels.push(t);
  if (chart.data.labels.length > 50) chart.data.labels.shift();
  chart.data.datasets.forEach(ds => {
    ds.data.push(r[ds.label]?.value ?? null);
    if (ds.data.length > 50) ds.data.shift();
  });
  chart.update();
}

function toggleTrend(tag) {
  const grid = document.getElementById('grid');
  if (activeTags.has(tag)) {
    activeTags.delete(tag);
    const idx = chart.data.datasets.findIndex(d => d.label === tag);
    if (idx >= 0) chart.data.datasets.splice(idx, 1);
  } else {
    activeTags.add(tag);
    const col = colors[tag] || ('#' + Math.floor(Math.random() * 0xFFFFFF).toString(16));
    colors[tag] = col;
    chart.data.datasets.push({ label: tag, data: [], borderColor: col, backgroundColor: 'transparent' });
  }
  // redraw active class
  Array.from(grid.children).forEach(card => {
    const t = card.textContent.split('\n')[0];
    card.classList.toggle('active', activeTags.has(t));
  });
  chart.update();
}

window.onload = () => {
  setupChart();
  (async function loop() {
    const d = await fetchData();
    updateInputs(d.readings, d.last_updated);
    updateDiagnostics(d.alarms, d.last_updated);
    updateTrends(d.readings, d.last_updated);
    setTimeout(loop, 3000);
  })();
};
