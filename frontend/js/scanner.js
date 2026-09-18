const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const analyzeBtn = document.getElementById('analyzeBtn');
const statusEl = document.getElementById('status');
const resultEmpty = document.getElementById('resultEmpty');
const result = document.getElementById('result');
const feedbackBox = document.getElementById('feedbackBox');
const correctionForm = document.getElementById('correctionForm');
const correctedCategory = document.getElementById('correctedCategory');
const feedbackStatus = document.getElementById('feedbackStatus');
const feedbackCorrect = document.getElementById('feedbackCorrect');
const feedbackIncorrect = document.getElementById('feedbackIncorrect');
const submitCorrection = document.getElementById('submitCorrection');

let selectedFile = null;
let currentHistoryId = null;

imageInput.addEventListener('change', () => {
  selectedFile = imageInput.files?.[0] ?? null;
  currentHistoryId = null;
  result.classList.add('hidden');
  resultEmpty.classList.remove('hidden');
  feedbackBox.classList.add('hidden');
  correctionForm.classList.add('hidden');
  feedbackStatus.textContent = '';

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
  feedbackBox.classList.add('hidden');
  correctionForm.classList.add('hidden');
  feedbackStatus.textContent = '';

  try {
    const response = await fetch('/api/analyze', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis failed.');

    currentHistoryId = data.history_id || null;
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
    feedbackBox.classList.toggle('hidden', !currentHistoryId);
    statusEl.textContent = 'Analysis complete.';
  } catch (error) {
    statusEl.textContent = error.message;
    statusEl.classList.add('error');
  } finally {
    analyzeBtn.disabled = false;
  }
});

feedbackCorrect.addEventListener('click', () => submitFeedback('correct'));
feedbackIncorrect.addEventListener('click', () => {
  correctionForm.classList.remove('hidden');
  feedbackStatus.textContent = 'Select the correct category, then submit your correction.';
});
submitCorrection.addEventListener('click', () => submitFeedback('incorrect', correctedCategory.value));

async function submitFeedback(feedback, corrected = null) {
  if (!currentHistoryId) return;
  feedbackCorrect.disabled = true;
  feedbackIncorrect.disabled = true;
  submitCorrection.disabled = true;
  feedbackStatus.textContent = 'Saving feedback…';

  try {
    const response = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ history_id: currentHistoryId, feedback, corrected_category: corrected }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Unable to save feedback.');
    feedbackStatus.textContent = 'Thank you. Your feedback was recorded.';
    correctionForm.classList.add('hidden');
  } catch (error) {
    feedbackStatus.textContent = error.message;
    feedbackCorrect.disabled = false;
    feedbackIncorrect.disabled = false;
    submitCorrection.disabled = false;
    return;
  }

  feedbackCorrect.disabled = true;
  feedbackIncorrect.disabled = true;
  submitCorrection.disabled = true;
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}
