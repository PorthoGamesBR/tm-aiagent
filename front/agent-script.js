const token = localStorage.getItem('token');
if (!token) {
  window.location.href = '/';
}
loginUser();

// TODO: Change this dependencies to the backend
const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
const GROQ_MODEL = "llama-3.3-70b-versatile"
function storageKey(suffix) { return null }
function ctxKey() { return null }
function getAgent1SystemPrompt() { return null }
function getAgent2SystemPrompt(userName, contextDoc) { return null }

// ═══════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════

let currentUser = null;
let chats       = {};     // { id: { id, title, type, messages: [] } }
let activeChatId = null;
let isStreaming   = false;
let contextDoc = null;

// ═══════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════

async function get_endpoint(endpoint_url){
  try {
    const response = await fetch(endpoint_url, {
  headers: {
    'Authorization': `Bearer ${token}`
  }}); // Relative path automatically points to the same server
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching local data:', error);
    return null;
  }
}

async function post_endpoint(endpoint_url, request){
  try {
    const response = await fetch(endpoint_url, {
    method: "POST",
    headers: {
    "Content-Type": "application/json",
    'Authorization': `Bearer ${token}`},
    body: JSON.stringify(request)}); // Relative path automatically points to the same server
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching local data:', error);
    return null;
  }
}

async function getContextDoc() {
  try {
    const response = await get_endpoint("/api/contextdoc");
    // Safely pull the content, or set to null if it doesn't exist
    contextDoc = response ? response["content"] : null;
  } catch (error) {
    console.error("Failed to fetch context document:", error);
    contextDoc = null; 
  }
}

function isContextDocAvailable() {
  if (contextDoc !== null) {
    return true;
  }
  return false;
}

function saveContextDoc(doc) {
  localStorage.setItem(ctxKey(), doc);
}

function deleteContextDoc() {
  localStorage.removeItem(ctxKey());
}

function loadChats() {
  const raw = localStorage.getItem(storageKey("chats"));
  chats = raw ? JSON.parse(raw) : {};
}

function saveChats() {
  localStorage.setItem(storageKey("chats"), JSON.stringify(chats));
}

function initials(name) {
  return name.split(" ").slice(0, 2).map(w => w[0]).join("").toUpperCase();
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}



async function updateAgentStatus() {
  // TODO: Add call to endpoint /agents
  const agentStatus = await get_endpoint("/api/agents");

  const a1dot   = document.getElementById("agent1-dot");
  const a1name  = document.getElementById("agent1-name");
  const a1badge = document.getElementById("agent1-badge");
  const a1item  = document.getElementById("agent1-item");

  const a2dot   = document.getElementById("agent2-dot");
  const a2name  = document.getElementById("agent2-name");
  const a2badge = document.getElementById("agent2-badge");
  const a2item  = document.getElementById("agent2-item");

  const ctxLabel = document.getElementById("view-ctx-label");

  if (agentStatus['researcher']['status'] === 'available') {
     // Agent 1 — active/pending
    a1dot.className   = "agent-dot dot-pending";
    a1name.className  = "agent-name";
    a1badge.className = "agent-badge badge-pending";
    a1badge.textContent = "aguardando";
    a1item.classList.add("active-agent");

    // Agent 2 — locked
    a2dot.className   = "agent-dot dot-locked";
    a2name.className  = "agent-name dimmed";
    a2badge.className = "agent-badge badge-locked";
    a2badge.textContent = "bloqueado";
    a2item.classList.remove("active-agent");

    ctxLabel.textContent = "Documento de contexto";
  }else if (agentStatus['manager']['status'] === 'available'){
        // Agent 1 — locked
    a1dot.className   = "agent-dot dot-locked";
    a1name.className  = "agent-name dimmed";
    a1badge.className = "agent-badge badge-locked";
    a1badge.textContent = "concluído";
    a1item.classList.remove("active-agent");

    // Agent 2 — active
    a2dot.className   = "agent-dot dot-active";
    a2name.className  = "agent-name";
    a2badge.className = "agent-badge badge-active";
    a2badge.textContent = "ativo";
    a2item.classList.add("active-agent");

    ctxLabel.textContent = "Ver documento de contexto";
  }
}

// ═══════════════════════════════════════════════
//  CHAT LIST RENDER
// ═══════════════════════════════════════════════

function renderChatList() {
  const list  = document.getElementById("chat-list");
  const ids   = Object.keys(chats).sort((a,b) => b - a);
  const hasCtx = isContextDocAvailable();

  list.innerHTML = "";

  if (ids.length === 0) {
    list.innerHTML = `<div class="chat-list-label">Sem histórico</div>`;
    return;
  }

  list.innerHTML = `<div class="chat-list-label">Histórico</div>`;

  ids.forEach(id => {
    const chat = chats[id];
    const isSelected = id === activeChatId;
    const typeLabel = chat.type === "onboarding" ? "Onboarding" : "Ops";

    const item = document.createElement("div");
    item.className = `chat-item${isSelected ? " selected" : ""}`;
    item.dataset.id = id;

    const iconPath = chat.type === "onboarding"
      ? `<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>`
      : `<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-4 0v2M12 12v4M10 14h4"/>`;

    item.innerHTML = `
      <div class="chat-item-icon">
        <svg width="14" height="14" fill="none" stroke="${chat.type === 'onboarding' ? '#FCD34D' : '#60A5FA'}" stroke-width="1.8" viewBox="0 0 24 24">${iconPath}</svg>
      </div>
      <span class="chat-item-title">${escapeHtml(chat.title)}</span>
      <span class="chat-item-type">${typeLabel}</span>
      <button class="chat-delete-btn" data-del="${id}" title="Excluir chat" aria-label="Excluir chat">
        <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>`;

    item.addEventListener("click", (e) => {
      if (e.target.closest("[data-del]")) return;
      openChat(id);
    });

    item.querySelector("[data-del]").addEventListener("click", (e) => {
      e.stopPropagation();
      deleteChat(id);
    });

    list.appendChild(item);
  });
}

// ═══════════════════════════════════════════════
//  OPEN / CREATE CHAT
// ═══════════════════════════════════════════════

function openChat(id) {
  activeChatId = id;
  const chat = chats[id];
  renderChatList();
  renderMessages(chat);
  updateTopbar(chat);
  enableInput();
}

function createNewChat() {
  const hasCtx = isContextDocAvailable();
  const type   = hasCtx ? "ops" : "onboarding";

  const id = generateId();
  const title = type === "onboarding"
    ? `Onboarding — ${new Date().toLocaleDateString("pt-BR")}`
    : `Chat Ops — ${new Date().toLocaleDateString("pt-BR")} ${new Date().toLocaleTimeString("pt-BR", {hour:"2-digit",minute:"2-digit"})}`;

  chats[id] = { id, title, type, messages: [] };
  saveChats();
  openChat(id);

  if (type === "onboarding") {
    sendAgentGreeting(id);
  } else {
    sendOpsGreeting(id);
  }
}

function deleteChat(id) {
  delete chats[id];
  saveChats();
  if (activeChatId === id) {
    activeChatId = null;
    clearMain();
  }
  renderChatList();
}

// ═══════════════════════════════════════════════
//  TOPBAR
// ═══════════════════════════════════════════════

function updateTopbar(chat) {
  const hasCtx = isContextDocAvailable();
  const titleEl  = document.getElementById("chat-title");
  const tagEl    = document.getElementById("chat-tag");
  const ctxEl    = document.getElementById("context-status");

  titleEl.textContent = chat.title;

  tagEl.style.display = "inline-flex";
  if (chat.type === "onboarding") {
    tagEl.className = "topbar-tag tag-onboarding";
    tagEl.textContent = "Onboarding";
  } else {
    tagEl.className = "topbar-tag tag-ops";
    tagEl.textContent = "Gerente Operacional";
  }

  ctxEl.style.display = "inline-flex";
  if (hasCtx) {
    ctxEl.className = "context-status ctx-ready";
    ctxEl.innerHTML = `<svg width="10" height="10" fill="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg> Contexto ativo`;
  } else {
    ctxEl.className = "context-status ctx-missing";
    ctxEl.innerHTML = `<svg width="10" height="10" fill="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg> Sem contexto`;
  }
}

function clearMain() {
  document.getElementById("chat-title").textContent = "Selecione ou inicie um chat";
  document.getElementById("chat-tag").style.display = "none";
  document.getElementById("context-status").style.display = "none";
  document.getElementById("messages").innerHTML = `
    <div id="empty-state">
      <div class="es-icon">
        <svg width="22" height="22" fill="none" stroke="#94A3B8" stroke-width="1.5" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </div>
      <p id="empty-title">Nenhum chat aberto</p>
      <span id="empty-sub">Clique em "Novo chat" para começar.</span>
    </div>`;
  document.getElementById("msg-input").disabled = true;
  document.getElementById("send-btn").disabled  = true;
}

// ═══════════════════════════════════════════════
//  MESSAGES RENDER
// ═══════════════════════════════════════════════

function escapeHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function formatMarkdown(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/^#{3}\s(.+)$/gm, "<h4 style='margin:8px 0 4px;font-size:13px;font-weight:600;color:#0F172A'>$1</h4>")
    .replace(/^#{2}\s(.+)$/gm, "<h3 style='margin:10px 0 5px;font-size:14px;font-weight:600;color:#0F172A'>$1</h3>")
    .replace(/^#{1}\s(.+)$/gm, "<h2 style='margin:12px 0 6px;font-size:15px;font-weight:600;color:#0F172A'>$1</h2>")
    .replace(/^[-•]\s(.+)$/gm, "<li style='margin:2px 0 2px 16px'>$1</li>")
    .replace(/\n/g, "<br>");
}

function renderMessages(chat) {
  const container = document.getElementById("messages");
  container.innerHTML = "";

  if (chat.messages.length === 0) {
    container.innerHTML = `<div id="empty-state" style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;color:#94A3B8">
      <svg width="28" height="28" fill="none" stroke="#CBD5E1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      <span style="font-size:13px;color:#94A3B8">Aguardando resposta do agente…</span>
    </div>`;
    return;
  }

  chat.messages.forEach(msg => appendMessage(msg, false));
  scrollToBottom();
}

function appendMessage(msg, scroll=true) {
  const container = document.getElementById("messages");
  const empState  = container.querySelector("#empty-state");
  if (empState) empState.remove();

  const isUser = msg.role === "user";
  const userInitials = initials(currentUser);

  const row = document.createElement("div");
  row.className = `msg-row ${isUser ? "user" : "agent"}`;

  const avatarLabel = isUser ? userInitials : "AG";
  const avatarClass = isUser ? "user-av" : "agent-av";
  const senderName  = isUser ? "" : (activeChatId && chats[activeChatId]?.type === "onboarding" ? "Agente Onboarding" : "Gerente Operacional");

  const content = isUser
    ? `<div class="msg-bubble user">${escapeHtml(msg.content)}</div>`
    : `<div class="msg-bubble agent"><div class="msg-sender">${senderName}</div>${formatMarkdown(msg.content)}</div>`;

  row.innerHTML = `
    <div class="msg-avatar ${avatarClass}">${avatarLabel}</div>
    ${content}`;

  container.appendChild(row);
  if (scroll) scrollToBottom();
}

function scrollToBottom() {
  const c = document.getElementById("messages");
  c.scrollTop = c.scrollHeight;
}

function showTyping() {
  const container = document.getElementById("messages");
  const empState  = container.querySelector("#empty-state");
  if (empState) empState.remove();

  const row = document.createElement("div");
  row.className = "msg-row agent";
  row.id = "typing-row";
  const chat = chats[activeChatId];
  const name = chat?.type === "onboarding" ? "Agente Onboarding" : "Gerente Operacional";
  row.innerHTML = `
    <div class="msg-avatar agent-av">AG</div>
    <div class="msg-bubble agent">
      <div class="msg-sender">${name}</div>
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>`;
  container.appendChild(row);
  scrollToBottom();
  return row;
}

function removeTyping() {
  const row = document.getElementById("typing-row");
  if (row) row.remove();
}

// ═══════════════════════════════════════════════
//  INPUT
// ═══════════════════════════════════════════════

function enableInput() {
  document.getElementById("msg-input").disabled = false;
  document.getElementById("send-btn").disabled  = false;
  document.getElementById("msg-input").focus();
}

function disableInput() {
  document.getElementById("msg-input").disabled = true;
  document.getElementById("send-btn").disabled  = true;
}

// ═══════════════════════════════════════════════
//  API CALL
// ═══════════════════════════════════════════════

async function callGroq(messages) {
  if (!GROQ_API_KEY) {
    return "[Erro: GROQ_API_KEY não configurada. Abra o arquivo HTML e cole sua chave no topo do script.]";
  }

  try {
    const res = await fetch(GROQ_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: GROQ_MODEL,
        messages,
        temperature: 0.7,
        max_tokens: 1500,
        stream: false
      })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return `[Erro da API: ${res.status} — ${err.error?.message || "Erro desconhecido"}]`;
    }

    const data = await res.json();
    return data.choices?.[0]?.message?.content || "[Resposta vazia do modelo]";
  } catch (e) {
    return `[Erro de rede: ${e.message}]`;
  }
}

// ═══════════════════════════════════════════════
//  AGENT GREETINGS
// ═══════════════════════════════════════════════

async function sendAgentGreeting(chatId) {
  disableInput();
  const typingRow = showTyping();

  const systemPrompt = getAgent1SystemPrompt();
  const intro = [
    { role: "system", content: systemPrompt },
    { role: "user", content: `Olá, meu nome é ${currentUser}.` }
  ];

  const reply = await callGroq(intro);
  removeTyping();

  if (!chats[chatId]) return;

  chats[chatId].messages.push({ role: "user",      content: `Olá, meu nome é ${currentUser}.` });
  chats[chatId].messages.push({ role: "assistant", content: reply });
  saveChats();

  appendMessage({ role: "assistant", content: reply });
  enableInput();

  checkForContextDoc(chatId, reply);
}

async function sendOpsGreeting(chatId) {
  disableInput();
  const typingRow = showTyping();

  const ctx = contextDoc;
  const systemPrompt = getAgent2SystemPrompt(currentUser, ctx);
  const intro = [
    { role: "system", content: systemPrompt },
    { role: "user",   content: `[QUEM ESTÁ FALANDO]: ` + currentUser + ` [DOCUMENTO_DE_CONTEXTO]: ` + ctx + ` [MESSAGE]: Olá.` }
  ];

  const reply = await callGroq(intro);
  removeTyping();

  if (!chats[chatId]) return;

  chats[chatId].messages.push({ role: "user",   content: `[QUEM ESTÁ FALANDO]: ` + currentUser + ` [DOCUMENTO_DE_CONTEXTO]: ` + ctx + ` [MESSAGE]: Olá.` });
  chats[chatId].messages.push({ role: "assistant", content: reply });
  saveChats();

  appendMessage({ role: "assistant", content: reply });
  enableInput();
}

// ═══════════════════════════════════════════════
//  SEND MESSAGE
// ═══════════════════════════════════════════════

async function sendMessage() {
  if (isStreaming || !activeChatId) return;
  const input   = document.getElementById("msg-input");
  const content = input.value.trim();
  if (!content) return;

  input.value = "";
  input.style.height = "auto";

  const chat = chats[activeChatId];
  chat.messages.push({ role: "user", content });
  saveChats();
  appendMessage({ role: "user", content });

  isStreaming = true;
  disableInput();
  const typingRow = showTyping();

  let apiMessages;

  if (chat.type === "onboarding") {
    apiMessages = [
      { role: "system", content: getAgent1SystemPrompt() },
      ...chat.messages.map(m => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.content }))
    ];
  } else {
    const ctx = contextDoc;
    apiMessages = [
      { role: "system", content: getAgent2SystemPrompt(currentUser, ctx) },
      ...chat.messages.map(m => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.content }))
    ];
  }

  const reply = await callGroq(apiMessages);
  removeTyping();

  if (!chats[activeChatId]) { isStreaming = false; return; }

  chats[activeChatId].messages.push({ role: "assistant", content: reply });
  saveChats();
  appendMessage({ role: "assistant", content: reply });

  isStreaming = false;
  enableInput();

  if (chat.type === "onboarding") {
    checkForContextDoc(activeChatId, reply);
  }
}

// ═══════════════════════════════════════════════
//  CONTEXT DOC DETECTION
// ═══════════════════════════════════════════════

function checkForContextDoc(chatId, text) {
  const startMarker = "===DOCUMENTO_DE_CONTEXTO_INICIO===";
  const endMarker   = "===DOCUMENTO_DE_CONTEXTO_FIM===";
 
  const startIdx = text.indexOf(startMarker);
  const endIdx   = text.indexOf(endMarker);
 
  if (startIdx === -1 || endIdx === -1) return;
 
  const doc = text.slice(startIdx + startMarker.length, endIdx).trim();
  saveContextDoc(doc);

  updateAgentStatus();
  updateTopbar(chats[chatId]);
  renderChatList();

  // show confirmation in chat
  setTimeout(() => {
    const notif = document.createElement("div");
    notif.style.cssText = "display:flex;align-items:center;gap:10px;background:#ECFDF5;border:1px solid #A7F3D0;border-radius:8px;padding:10px 14px;font-size:13px;color:#065F46;margin:4px 0;";
    notif.innerHTML = `<svg width="16" height="16" fill="none" stroke="#059669" stroke-width="2" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <span><strong>Documento de contexto gerado.</strong> O Gerente Operacional já está disponível.</span>`;
    document.getElementById("messages").appendChild(notif);
    scrollToBottom();
  }, 300);
}

// ═══════════════════════════════════════════════
//  CONTEXT DOC VIEWER
// ═══════════════════════════════════════════════

function openCtxViewer() {
  const doc = contextDoc;
  if (!doc) return;
  document.getElementById("ctx-viewer-body").textContent = doc;
  document.getElementById("ctx-viewer").classList.remove("hidden");
}

function closeCtxViewer() {
  document.getElementById("ctx-viewer").classList.add("hidden");
}

// ═══════════════════════════════════════════════
//  USER LOGIN
// ═══════════════════════════════════════════════

async function loginUser() {
  currentUser = (await get_endpoint("/api/user"))["user"]
  localStorage.setItem("ops_agent_current_user", currentUser);

  document.getElementById("gate").style.display = "none";
  document.getElementById("user-avatar").textContent = initials(currentUser);
  document.getElementById("identity-name").textContent = currentUser;

  await getContextDoc();
  loadChats();
  await updateAgentStatus();
  renderChatList();
  clearMain();
}

// ═══════════════════════════════════════════════
//  EVENTS
// ═══════════════════════════════════════════════

// New chat
document.getElementById("new-chat-btn").addEventListener("click", () => {
  if (!currentUser) return;
  createNewChat();
});

// Send
document.getElementById("send-btn").addEventListener("click", sendMessage);

document.getElementById("msg-input").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Auto-resize textarea
document.getElementById("msg-input").addEventListener("input", function() {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 140) + "px";
});

// Context doc viewer
document.getElementById("view-ctx-btn").addEventListener("click", () => {
  if (isContextDocAvailable()) {
    openCtxViewer();
  }
});

document.getElementById("ctx-viewer-close").addEventListener("click", closeCtxViewer);
document.getElementById("ctx-close-btn").addEventListener("click", closeCtxViewer);
document.getElementById("ctx-viewer").addEventListener("click", e => {
  if (e.target === document.getElementById("ctx-viewer")) closeCtxViewer();
});

document.getElementById("ctx-delete-btn").addEventListener("click", () => {
  if (!confirm("Excluir o documento de contexto? O Gerente Operacional ficará bloqueado até um novo onboarding.")) return;
  deleteContextDoc();
  closeCtxViewer();
  updateAgentStatus();
  if (activeChatId) updateTopbar(chats[activeChatId]);
  renderChatList();
});