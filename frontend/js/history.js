const totalScans = document.getElementById('totalScans');
const topCategory = document.getElementById('topCategory');
const uniqueCategories = document.getElementById('uniqueCategories');
const historyEmpty = document.getElementById('historyEmpty');
const historyTableWrap = document.getElementById('historyTableWrap');
const historyBody = document.getElementById('historyBody');

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString();
}

async function loadHistory() {
  try {
    const [historyResponse, statsResponse] = await Promise.all([
      fetch('/api/history?limit=50'),
      fetch('/api/history/stats'),
    ]);
    if (!historyResponse.ok || !statsResponse.ok) throw new Error('Unable to load history.');

    const history = await historyResponse.json();
    const stats = await statsResponse.json();

    totalScans.textContent = stats.total_scans ?? 0;
    const counts = stats.category_counts || {};
    const tops = Array.isArray(stats.top_categories) ? stats.top_categories : [];
    topCategory.textContent = tops.length === 0 ? '—' : (tops.length === 1 ? tops[0] : `Tie: ${tops.join(', ')}`);
    uniqueCategories.textContent = Object.keys(counts).length;

    if (!Array.isArray(history.items) || history.items.length === 0) return;

    historyEmpty.classList.add('hidden');
    historyTableWrap.classList.remove('hidden');
    historyBody.innerHTML = '';

    history.items.forEach((item) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><strong>${escapeHtml(item.item)}</strong></td>
        <td><span class="badge">${escapeHtml(item.category)}</span></td>
        <td>${Math.round(Number(item.confidence || 0) * 100)}%</td>
        <td>${escapeHtml(formatDate(item.timestamp))}</td>
        <td>${item.grounded ? 'Grounded' : 'Limited'}${item.review_required ? ' • Review' : ''}</td>
      `;
      historyBody.appendChild(row);
    });
  } catch (error) {
    historyEmpty.classList.remove('hidden');
    historyEmpty.querySelector('p').textContent = error.message;
  }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}

loadHistory();
