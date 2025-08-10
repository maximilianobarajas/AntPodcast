/* App state & UI logic wired to YOUR FastAPI endpoints.
   Ant-themed, pastel, empty subtopic list at start, 50/50 split by default.
   Routes used:
   - POST /generate_subtopics?main_topic=&num_topics=
   - POST /generate_intro
   - POST /generate_subtopic_paragraph
   - POST /podcast/build-openai (returns audio/mpeg body)
*/

const API = {
  BASE: "http://127.0.0.1:8000", // change if served elsewhere
  SUBTOPICS: "/generate_subtopics",
  INTRO: "/generate_intro",
  SUBTOPIC_P: "/generate_subtopic_paragraph",
  PODCAST_BUILD: "/podcast/build-openai",
};

// ===== DOM =====
const stepsEl = document.getElementById('steps');
const addBtn = document.getElementById('add-step');
const filterEl = document.getElementById('filter');
const topicEl = document.getElementById('topic');
const targetEl = document.getElementById('target');
const outputEl = document.getElementById('output');
const generateBtn = document.getElementById('btn-generate');
const copyBtn = document.getElementById('btn-copy');
const importBtn = document.getElementById('btn-import');
const exportBtn = document.getElementById('btn-export');
const clearBtn  = document.getElementById('btn-clear');
const savedBadge= document.getElementById('saved-indicator');
const resizer = document.getElementById('resizer');
const root = document.documentElement;

// 50/50 split by default (still adjustable)
root.style.setProperty('--left-pane', Math.round(window.innerWidth/2) + 'px');

// normalize built-in buttons
[generateBtn, copyBtn, importBtn, exportBtn, clearBtn, addBtn]
  .filter(Boolean)
  .forEach(b => b.setAttribute('type','button'));

// Brand ant 🐜
const brandH1 = document.querySelector('.brand h1');
if (brandH1) brandH1.innerHTML = 'Ant Podcaster <span class="ant-emoji" aria-hidden="true">🐜</span>';

// Extra toolbar controls (Intro, Subtopics, Podcast)
let introBtn = null;
let suggestBtn = null;
let podcastBtn = null;
let audioEl = null;

// ===== State: start with 0 subtopics =====
let steps = []; // ⬅️ empty on launch

let draggingId = null;
let placeholderEl = document.createElement('li');
placeholderEl.className = 'placeholder';

hydrateComposeToolbar();
render();
updateWordcount();

/* ================= Toolbar (adds intro/subtopics/podcast) ================= */

function hydrateComposeToolbar(){
  const toolbar = document.querySelector('.toolbar');

  introBtn = document.createElement('button');
  introBtn.className = 'btn secondary';
  introBtn.textContent = 'AI Intro';
  introBtn.setAttribute('type','button');
  introBtn.addEventListener('click', onGenerateIntro);
  toolbar.appendChild(introBtn);

  suggestBtn = document.createElement('button');
  suggestBtn.className = 'btn secondary';
  suggestBtn.textContent = 'Forage subtopics 🐜';
  suggestBtn.setAttribute('type','button');
  suggestBtn.addEventListener('click', onSuggestSubtopics);
  toolbar.appendChild(suggestBtn);

  podcastBtn = document.createElement('button');
  podcastBtn.className = 'btn secondary';
  podcastBtn.textContent = 'Build Podcast';
  podcastBtn.setAttribute('type','button');
  podcastBtn.addEventListener('click', onBuildPodcast);
  toolbar.appendChild(podcastBtn);

  audioEl = document.createElement('audio');
  audioEl.controls = true;
  audioEl.setAttribute('preload','none');
  audioEl.setAttribute('controlsList','nodownload');
  audioEl.style.marginLeft = '8px';
  toolbar.appendChild(audioEl);
}

/* ================= Rendering & Cards ================= */

function render(list = steps) {
  const prevScroll = stepsEl.scrollTop;
  stepsEl.innerHTML = '';
  const q = (filterEl.value || '').toLowerCase();

  list
    .filter(s => s.title.toLowerCase().includes(q))
    .forEach(s => stepsEl.appendChild(cardEl(s)));

  stepsEl.scrollTop = prevScroll;
  flashSaved('Ready');
}

function cardEl(step){
  const li = document.createElement('li');
  li.className = 'card';
  li.draggable = true;
  li.dataset.id = step.id;

  const title = document.createElement('input');
  title.className = 'input title';
  title.placeholder = 'Subtopic (what are the ants carrying?)';
  title.value = step.title;
  title.addEventListener('input', e => { step.title = e.target.value; });

  const notes = document.createElement('textarea');
  notes.className = 'textarea notes';
  notes.placeholder = 'Notes…';
  notes.value = step.notes;
  notes.addEventListener('input', e => { step.notes = e.target.value; });

  const actions = document.createElement('div');
  actions.className = 'actions';

  const handle = document.createElement('span');
  handle.className = 'handle';
  handle.title = 'Drag to reorder (ant trail)';
  handle.textContent = '🐜'; // ant handle

  const dup = button('Duplicate', 'secondary', () => {
    const idx = steps.findIndex(s => s.id === step.id);
    steps.splice(idx + 1, 0, { id: uid(), title: step.title, notes: step.notes });
    render();
  });

  const copyTitle = button('Copy title→notes', 'secondary', () => {
    step.notes = step.title;
    notes.value = step.notes;
  });

  // AI paragraph for this subtopic
  const aiPara = button('AI paragraph', 'primary', async () => {
    const baseWords = parseInt(targetEl.value || '0', 10);
    const defaultWC = (Number.isFinite(baseWords) && baseWords > 0)
      ? Math.max(80, Math.min(300, Math.floor(baseWords/4)))
      : 180;
    const wcStr = prompt('Target words for this paragraph?', String(defaultWC));
    const wc = Math.max(40, Math.min(800, parseInt(wcStr || defaultWC, 10)));

    try{
      aiPara.disabled = true; aiPara.textContent = 'Foraging…';
      const res = await fetch(API.BASE + API.SUBTOPIC_P, {
        method: 'POST',
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
          text: notes.value || '',
          subtopic: title.value || '',
          word_count: wc
        })
      });
      const data = await res.json();
      const para = data.paragraph || '';
      if (para) {
        step.notes = para;
        notes.value = para;
      } else {
        alert('No paragraph returned.');
      }
    }catch(e){
      alert('Paragraph generation failed.');
    }finally{
      aiPara.disabled = false; aiPara.textContent = 'AI paragraph';
    }
  });

  const del = button('Delete', 'danger', () => {
    steps = steps.filter(s => s.id !== step.id);
    render();
  });

  actions.append(handle, dup, copyTitle, aiPara, del);

  // Drag
  li.addEventListener('dragstart', e => {
    draggingId = step.id;
    li.classList.add('dragging');
    const img = new Image();
    img.src = 'data:image/svg+xml;base64,PHN2ZyBmaWxsPSJub25lIiBoZWlnaHQ9IjEiIHdpZHRoPSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciLz4=';
    e.dataTransfer.setDragImage(img, 0, 0);
  });
  li.addEventListener('dragend', () => {
    li.classList.remove('dragging');
    draggingId = null;
    placeholderEl.remove();
  });

  stepsEl.addEventListener('dragover', onDragOver);
  stepsEl.addEventListener('drop', onDrop);

  // Keyboard reorder
  li.addEventListener('keydown', e => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown'){
      e.preventDefault();
      const idx = steps.findIndex(s => s.id === step.id);
      const delta = e.key === 'ArrowUp' ? -1 : 1;
      const j = idx + delta;
      if (j >= 0 && j < steps.length){
        const [moved] = steps.splice(idx,1);
        steps.splice(j,0,moved);
        render();
        const el = stepsEl.querySelector(`[data-id="${moved.id}"] .title`);
        el?.focus();
      }
    }
  });

  li.appendChild(title);
  li.appendChild(actions);
  li.appendChild(notes);
  return li;
}

function button(label, variant, onClick){
  const b = document.createElement('button');
  b.className = `btn ${variant}`;
  b.type = 'button';
  b.textContent = label;
  b.addEventListener('click', onClick);
  return b;
}

/* ================= DnD helpers ================= */

function onDragOver(e){
  e.preventDefault();
  const afterElement = getDragAfterElement(stepsEl, e.clientY);
  if (afterElement == null){
    if (stepsEl.lastElementChild !== placeholderEl){
      stepsEl.appendChild(placeholderEl);
    }
  } else {
    stepsEl.insertBefore(placeholderEl, afterElement);
  }
}

function onDrop(e){
  e.preventDefault();
  const targetIndex = [...stepsEl.children].indexOf(placeholderEl);
  if (targetIndex === -1 || draggingId == null) return;

  const fromIndex = steps.findIndex(s => s.id === draggingId);
  const [moved] = steps.splice(fromIndex, 1);

  const q = (filterEl.value || '').toLowerCase();
  const visibleIds = steps
    .slice(0, fromIndex)
    .concat([moved])
    .concat(steps.slice(fromIndex))
    .filter(s => s.title.toLowerCase().includes(q))
    .map(s => s.id);

  const movedVisibleIndex = visibleIds.indexOf(moved.id);
  visibleIds.splice(movedVisibleIndex, 1);
  visibleIds.splice(targetIndex, 0, moved.id);

  const newOrder = [];
  const placed = new Set();
  for (const vid of visibleIds){
    const s = vid === moved.id ? moved : steps.find(x => x.id === vid);
    if (s && !placed.has(s.id)){ newOrder.push(s); placed.add(s.id); }
  }
  for (const s of steps){
    if (!placed.has(s.id)){ newOrder.push(s); placed.add(s.id); }
  }
  steps = newOrder;
  placeholderEl.remove();
  render();
}

function getDragAfterElement(container, y){
  const els = [...container.querySelectorAll('.card:not(.dragging)')];
  let closest = { offset: Number.NEGATIVE_INFINITY, element: null };
  for (const el of els){
    const box = el.getBoundingClientRect();
    const offset = y - (box.top + box.height / 2);
    if (offset < 0 && offset > closest.offset){
      closest = { offset, element: el };
    }
  }
  return closest.element;
}

/* ================= Compose actions ================= */

generateBtn.addEventListener('click', () => {
  const topic = (topicEl.value || '').trim();
  const target = (targetEl.value || '').trim();
  const body = steps.map(s => s.notes.trim()).filter(Boolean).join('\n\n');
  const header = [
    topic ? `Title: ${topic}` : null,
    target ? `~${target} words` : null
  ].filter(Boolean).join(' · ');
  outputEl.value = `${header ? header + '\n\n' : ''}${body}`;
  updateWordcount();
  flashSaved('Composed');
});

copyBtn.addEventListener('click', async () => {
  try{
    await navigator.clipboard.writeText(outputEl.value);
    flashSaved('Copied');
  }catch{
    flashSaved('Copy failed');
  }
});

importBtn.addEventListener('click', async () => {
  const text = prompt('Paste JSON to import (steps/topic/target):');
  if (!text) return;
  try{
    const data = JSON.parse(text);
    if (Array.isArray(data.steps)){
      steps = data.steps.map(s => ({ id: uid(), title: s.title||'', notes: s.notes||'' }));
    }
    if (typeof data.topic === 'string') topicEl.value = data.topic;
    if (typeof data.target === 'string' || typeof data.target === 'number') targetEl.value = String(data.target);
    render();
  }catch{
    alert('Invalid JSON');
  }
});

exportBtn.addEventListener('click', () => {
  const data = JSON.stringify({
    topic: topicEl.value || '',
    target: targetEl.value || '',
    steps
  }, null, 2);
  prompt('Copy your JSON:', data);
});

clearBtn.addEventListener('click', () => {
  if (!confirm('Clear all steps and compose fields?')) return;
  steps = [];
  topicEl.value = '';
  targetEl.value = '';
  outputEl.value = '';
  render();
});

/* ===== Intro from server ===== */
async function onGenerateIntro(){
  const main_topic = (topicEl.value || '').trim();
  if (!main_topic){ alert('Set a Topic first.'); return; }
  const wcStr = prompt('Target words for the introduction?', '120');
  const word_count = Math.max(50, Math.min(600, parseInt(wcStr || '120', 10)));

  try{
    introBtn.disabled = true; introBtn.textContent = 'Writing…';
    const res = await fetch(API.BASE + API.INTRO, {
      method: 'POST',
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ main_topic, word_count })
    });
    const data = await res.json();
    const intro = data.introduction || '';
    if (!intro){ alert('No introduction returned.'); }
    else {
      const existing = outputEl.value.trim();
      outputEl.value = intro + (existing ? '\n\n' + existing : '');
      updateWordcount();
      flashSaved('Intro added');
    }
  }catch(e){
    alert('Intro generation failed.');
  }finally{
    introBtn.disabled = false; introBtn.textContent = 'AI Intro';
  }
}

/* ===== Subtopics from server ===== */
async function onSuggestSubtopics(){
  const main_topic = (topicEl.value || '').trim();
  if (!main_topic) { alert('Set a Topic first.'); return; }
  const numStr = prompt('How many subtopics?', '6');
  const num_topics = Math.max(1, Math.min(50, parseInt(numStr || '6', 10)));

  try{
    suggestBtn.disabled = true; suggestBtn.textContent = 'Foraging…';
    const url = `${API.BASE}${API.SUBTOPICS}?` + new URLSearchParams({ main_topic, num_topics }).toString();
    const res = await fetch(url, { method: 'POST' });
    const data = await res.json();
    const arr = data.subtopics || [];
    if (!Array.isArray(arr) || arr.length === 0) {
      alert(data.msg || 'No subtopics returned.');
      return;
    }
    for (const s of arr){
      steps.push({ id: uid(), title: s, notes: '' });
    }
    render();
    flashSaved('Subtopics added');
  } catch(e){
    alert('Subtopics failed.');
  } finally {
    suggestBtn.disabled = false; suggestBtn.textContent = 'Forage subtopics 🐜';
  }
}

/* ===== Podcast build (TTS) — STREAMED MP3 → BLOB URL ===== */
async function onBuildPodcast(){
  const text = (outputEl.value || '').trim();
  if (!text){ alert('Compose or paste an essay first.'); return; }
  const title = (topicEl.value || 'Podcast Episode').trim();
  const minutesStr = prompt('Target minutes (3–60)?', '8');
  const target_minutes = Math.max(3, Math.min(60, parseInt(minutesStr || '8', 10)));
  const segmentsStr = prompt('Number of segments (3–12)?', '4');
  const segments = Math.max(3, Math.min(12, parseInt(segmentsStr || '4', 10)));
  const tone = 'friendly and informative';
  const voice = 'onyx';

  try{
    podcastBtn.disabled = true; podcastBtn.textContent = 'Building…';
    const res = await fetch(API.BASE + API.PODCAST_BUILD, {
      method: 'POST',
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ source_text: text, title, target_minutes, segments, tone, voice })
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    // stable audio swap
    audioEl.pause();
    audioEl.removeAttribute('src');
    audioEl.load();
    audioEl.setAttribute('controlsList','nodownload');
    audioEl.setAttribute('preload','none');

    audioEl.src = url;

    await new Promise((resolve, reject) => {
      const onCanPlay = () => { cleanup(); resolve(); };
      const onError   = () => { cleanup(); reject(new Error('audio error')); };
      const cleanup = () => {
        audioEl.removeEventListener('canplay', onCanPlay);
        audioEl.removeEventListener('error', onError);
      };
      audioEl.addEventListener('canplay', onCanPlay, { once:true });
      audioEl.addEventListener('error', onError, { once:true });
      audioEl.load();
    });

    await audioEl.play();
    flashSaved('Podcast ready');
  }catch(e){
    console.error(e);
    alert('Podcast build failed.');
  }finally{
    podcastBtn.disabled = false; podcastBtn.textContent = 'Build Podcast';
  }
}

/* ================= Misc (import/export/filter/wordcount) ================= */

filterEl.addEventListener('input', () => render());

addBtn.addEventListener('click', () => {
  const title = prompt('New subtopic title:');
  if (!title) return;
  steps.push({ id: uid(), title: title.trim(), notes: '' });
  render();
});

outputEl.addEventListener('input', updateWordcount);
function updateWordcount(){
  const words = (outputEl.value.trim().match(/\b\w+\b/g) || []).length;
  document.getElementById('wordcount').textContent = `${words} word${words===1?'':'s'}`;
}

/* ================= Resizer (no-overlap layout) ================= */

let resizing = false;
resizer.addEventListener('mousedown', e => { resizing = true; document.body.style.cursor = 'col-resize'; });
window.addEventListener('mouseup',   e => { resizing = false; document.body.style.cursor = 'default'; });
window.addEventListener('mousemove', e => {
  if (!resizing) return;
  const px = Math.min(820, Math.max(320, e.clientX));
  root.style.setProperty('--left-pane', px + 'px');
});
resizer.addEventListener('keydown', e => {
  const cur = parseInt(getComputedStyle(root).getPropertyValue('--left-pane'));
  const step = (e.shiftKey ? 40 : 20);
  if (e.key === 'ArrowLeft'){
    root.style.setProperty('--left-pane', Math.max(320, cur - step) + 'px');
  } else if (e.key === 'ArrowRight'){
    root.style.setProperty('--left-pane', Math.min(820, cur + step) + 'px');
  }
});

/* ================= Utils ================= */

function uid(){ return Math.random().toString(36).slice(2,9); }
function flashSaved(text){
  savedBadge.textContent = text;
  savedBadge.style.opacity = '1';
  clearTimeout(savedBadge._t);
  savedBadge._t = setTimeout(()=> savedBadge.style.opacity = '0.7', 800);
}
