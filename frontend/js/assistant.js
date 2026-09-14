const form = document.getElementById('chatForm');
const input = document.getElementById('question');
const messages = document.getElementById('messages');
const statusEl = document.getElementById('chatStatus');

function addSourceCard(sources) {
  const card = document.createElement('div');
  card.className = 'source-card';
  const title = document.createElement('strong');
  title.textContent = '📚 Sources';
  card.appendChild(title);
  sources.forEach((source, index) => {
    const row = document.createElement('div');
    row.className = 'source-item';
    const label = document.createElement('span');
    label.textContent = `${index + 1}. ${source.title}`;
    row.appendChild(label);
    if (source.url && /^https?:\/\//i.test(source.url)) {
      const link = document.createElement('a');
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Open';
      row.appendChild(link);
    }
    card.appendChild(row);
  });
  messages.appendChild(card);
  messages.scrollTop = messages.scrollHeight;
}

function addMessage(text, role) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, 'user');
  input.value = '';
  statusEl.textContent = 'Thinking…';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Chat failed.');
    addMessage(data.answer, 'assistant');
    if (Array.isArray(data.sources) && data.sources.length) {
      const unique = data.sources.slice(0, 3);
      addSourceCard(unique);
    }
    statusEl.textContent = data.grounded ? 'Grounded in the WasteWise knowledge base.' : 'No sufficiently relevant grounded source found. Verify locally.';
  } catch (error) {
    addMessage(`Error: ${error.message}`, 'assistant');
    statusEl.textContent = 'Request failed.';
    statusEl.classList.add('error');
  }
});
