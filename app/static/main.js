const chatDiv     = document.getElementById('chat');
const textInput   = document.getElementById('textInput');
const sendTextBtn = document.getElementById('sendText');
const startRecBtn = document.getElementById('startRec');
const stopRecBtn  = document.getElementById('stopRec');
const statusDiv   = document.getElementById('status');
const spinner     = document.getElementById('spinner');   // ← our spinner
const replyAudio  = document.getElementById('replyAudio');

let mediaRecorder, audioChunks = [];

// Helpers
function timestamp() {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function addMessage(who, text) {
  const el = document.createElement('div');
  el.className = `message ${who}`;
  el.textContent = text;

  const time = document.createElement('div');
  time.className = 'time';
  time.textContent = timestamp();
  el.appendChild(time);

  chatDiv.append(el);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

// Send text message
async function sendText() {
  const txt = textInput.value.trim();
  if (!txt) return;
  addMessage('user', txt);
  textInput.value = '';
  await callApi({ user_id: 'alice', text: txt });
}

// Keyboard: Enter to send
textInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendText();
  }
});

sendTextBtn.addEventListener('click', sendText);

// Start recording
startRecBtn.addEventListener('click', async () => {
  if (!navigator.mediaDevices) {
    statusDiv.textContent = 'Audio capture not supported';
    return;
  }
  statusDiv.textContent = 'Recording…';
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.start();
  startRecBtn.disabled = true;
  stopRecBtn.disabled  = false;
});

// Stop & upload
stopRecBtn.addEventListener('click', () => {
  statusDiv.textContent = 'Processing audio…';
  mediaRecorder.stop();
  mediaRecorder.onstop = async () => {
    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    addMessage('user', '[voice message]');
    await callApi({ user_id: 'alice', audio: blob });
    startRecBtn.disabled = false;
    stopRecBtn.disabled  = true;
  };
});

// Core API fetch
async function callApi({ user_id, text = null, audio = null }) {
  // show spinner
  spinner.style.display = 'block';
  const form = new FormData();
  form.append('user_id', user_id);
  if (text  !== null) form.append('text', text);
  if (audio !== null) form.append('audio', audio, 'recording.webm');

  try {
    const res = await fetch('/chat/', { method: 'POST', body: form });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const { reply, audio_url } = await res.json();

    addMessage('sophie', reply);
    statusDiv.textContent = '';

    // Play back
    replyAudio.src = audio_url;
    replyAudio.hidden = false;
    await replyAudio.play().catch(() => {});

  } catch (err) {
    console.error(err);
    statusDiv.textContent = 'Error: ' + err.message;

  } finally {
    // hide spinner
    spinner.style.display = 'none';
  }
}
