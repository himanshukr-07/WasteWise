const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const analyzeBtn = document.getElementById('analyzeBtn');
const statusEl = document.getElementById('status');
const resultEmpty = document.getElementById('resultEmpty');
const result = document.getElementById('result');

let selectedFile = null;

imageInput.addEventListener('change', () => {
  selectedFile = imageInput.files?.[0] ?? null;
  result.classList.add('hidden');
  resultEmpty.classList.remove('hidden');

  if (!selectedFile) {
    preview.classList.add('hidden');
    analyzeBtn.disabled = true;
    return;
  }

  preview.src = URL.createObjectURL(selectedFile);
  preview.classList.remove('hidden');
  analyzeBtn.disabled = false;
  statusEl.textContent = `${selectedFile.name} selected.`;
  statusEl.classList.remove('error');
});

analyzeBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append('file', selectedFile);

  analyzeBtn.disabled = true;
  statusEl.textContent = 'Analyzing image…';
  statusEl.classList.remove('error');

  try {
    const response = await fetch('/api/analyze', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis failed.');

    document.getElementById('item').textContent = data.item;
    document.getElementById('category').textContent = data.category;
    document.getElementById('confidence').textContent = `${Math.round(data.confidence * 100)}%`;
    document.getElementById('confidenceLabel').textContent = data.confidence_label || 'Model-estimated';
    document.getElementById('observation').textContent = data.observation || 'No additional observation.';
    document.getElementById('recommendation').textContent = data.recommendation;
    document.getElementById('source').textContent = data.grounded ? `Grounding: ${data.source_relevance}` : 'Grounding: limited or unavailable';

    const reviewBox = document.getElementById('reviewBox');
    if (data.review_required) {
      reviewBox.classList.remove('hidden');
      reviewBox.innerHTML = `<strong>⚠ Verification recommended</strong><ul>${(data.review_reasons || []).map(reason => `<li>${escapeHtml(reason)}</li>`).join('')}</ul>`;
    } else {
      reviewBox.classList.add('hidden');
      reviewBox.innerHTML = '';
    }

    resultEmpty.classList.add('hidden');
    result.classList.remove('hidden');
    statusEl.textContent = 'Analysis complete.';
  } catch (error) {
    statusEl.textContent = error.message;
    statusEl.classList.add('error');
  } finally {
    analyzeBtn.disabled = false;
  }
});

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}
