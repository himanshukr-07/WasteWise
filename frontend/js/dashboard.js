const totalScans = document.getElementById('totalScans');
const categoriesSeen = document.getElementById('categoriesSeen');
const groundingRate = document.getElementById('groundingRate');
const reviewRequired = document.getElementById('reviewRequired');
const categoryBars = document.getElementById('categoryBars');
const categoryEmpty = document.getElementById('categoryEmpty');
const specificCount = document.getElementById('specificCount');
const limitedCount = document.getElementById('limitedCount');
const noneCount = document.getElementById('noneCount');
const groundingFill = document.getElementById('groundingFill');
const qualityText = document.getElementById('qualityText');
const dailyChart = document.getElementById('dailyChart');
const dailyEmpty = document.getElementById('dailyEmpty');

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}

function renderCategoryBars(counts, total) {
  categoryBars.innerHTML = '';
  const entries = Object.entries(counts);
  if (!entries.length) {
    categoryEmpty.classList.remove('hidden');
    return;
  }
  categoryEmpty.classList.add('hidden');
  entries.forEach(([category, count]) => {
    const pct = total ? (count / total) * 100 : 0;
    const row = document.createElement('div');
    row.className = 'bar-row';
    row.innerHTML = `
      <div class="bar-label"><span>${escapeHtml(category)}</span><strong>${count}</strong></div>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.max(pct, 3)}%"></div></div>`;
    categoryBars.appendChild(row);
  });
}

function renderDaily(data) {
  dailyChart.innerHTML = '';
  if (!data.length) {
    dailyEmpty.classList.remove('hidden');
    return;
  }
  dailyEmpty.classList.add('hidden');
  const max = Math.max(...data.map(x => x.count), 1);
  data.forEach((entry) => {
    const col = document.createElement('div');
    col.className = 'day-column';
    const height = Math.max((entry.count / max) * 100, 8);
    const dateLabel = new Date(`${entry.date}T00:00:00`).toLocaleDateString(undefined, {month:'short', day:'numeric'});
    col.innerHTML = `
      <div class="day-value">${entry.count}</div>
      <div class="day-bar-wrap"><div class="day-bar" style="height:${height}%"></div></div>
      <div class="day-label">${escapeHtml(dateLabel)}</div>`;
    dailyChart.appendChild(col);
  });
}

async function loadDashboard() {
  try {
    const response = await fetch('/api/history/analytics');
    if (!response.ok) throw new Error('Unable to load dashboard analytics.');
    const data = await response.json();
    const counts = data.category_counts || {};
    totalScans.textContent = data.total_scans ?? 0;
    categoriesSeen.textContent = Object.keys(counts).length;
    groundingRate.textContent = `${Number(data.grounding_rate || 0).toFixed(1)}%`;
    reviewRequired.textContent = data.review_required ?? 0;

    const grounding = data.grounding_counts || {};
    specificCount.textContent = grounding['category-specific'] ?? 0;
    limitedCount.textContent = grounding.limited ?? 0;
    noneCount.textContent = grounding.none ?? 0;
    const total = Math.max(Number(data.total_scans || 0), 1);
    groundingFill.style.width = `${Math.min(Number(data.grounding_rate || 0), 100)}%`;
    qualityText.textContent = `${data.grounding_rate || 0}% of saved scans have category-specific evidence. Limited and ungrounded scans should be reviewed before operational use.`;

    renderCategoryBars(counts, Number(data.total_scans || 0));
    renderDaily(Array.isArray(data.daily_counts) ? data.daily_counts : []);
  } catch (error) {
    qualityText.textContent = error.message;
    categoryEmpty.classList.remove('hidden');
  }
}

loadDashboard();
