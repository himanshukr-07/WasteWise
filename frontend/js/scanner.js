const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const uploadBox = document.getElementById('uploadBox');
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
let objectUrl = null;

function isSupportedImage(file) {
  return file && ['image/jpeg', 'image/png', 'image/webp'].includes(file.type);
}

function setSelectedFile(file) {
  if (!isSupportedImage(file)) {
    statusEl.textContent = 'Please choose a JPG, PNG, or WEBP image.';
    statusEl.classList.add('error');
    return;
  }
  selectedFile = file;
  currentHistoryId = null;
  result.classList.add('hidden');
  resultEmpty.classList.remove('hidden');
  feedbackBox.classList.add('hidden');
  correctionForm.classList.add('hidden');
  feedbackStatus.textContent = '';
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = URL.createObjectURL(file);
  preview.src = objectUrl;
  preview.classList.remove('hidden');
  analyzeBtn.disabled = false;
  clearBtn.classList.remove('hidden');
  statusEl.textContent = `${file.name} selected.`;
  statusEl.classList.remove('error');
}

imageInput.addEventListener('change', () => {
  const file = imageInput.files?.[0] ?? null;
  if (file) setSelectedFile(file);
});

['dragenter', 'dragover'].forEach((eventName) => {
  uploadBox.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadBox.classList.add('dragging');
  });
});

['dragleave', 'drop'].forEach((eventName) => {
  uploadBox.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadBox.classList.remove('dragging');
  });
});

uploadBox.addEventListener('drop', (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file) setSelectedFile(file);
});

uploadBox.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    imageInput.click();
  }
});

clearBtn.addEventListener('click', () => {
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = null;
  selectedFile = null;
  currentHistoryId = null;
  imageInput.value = '';
  preview.src = '';
  preview.classList.add('hidden');
  analyzeBtn.disabled = true;
  clearBtn.classList.add('hidden');
  result.classList.add('hidden');
  resultEmpty.classList.remove('hidden');
  feedbackBox.classList.add('hidden');
  correctionForm.classList.add('hidden');
  feedbackStatus.textContent = '';
  statusEl.textContent = 'Choose a waste image to begin.';
  statusEl.classList.remove('error');
});

analyzeBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append('file', selectedFile);

  analyzeBtn.disabled = true;
  clearBtn.disabled = true;
  analyzeBtn.classList.add('loading');
  analyzeBtn.textContent = 'Analyzing…';
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
    clearBtn.disabled = false;
    analyzeBtn.classList.remove('loading');
    analyzeBtn.textContent = 'Analyze Waste';
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
