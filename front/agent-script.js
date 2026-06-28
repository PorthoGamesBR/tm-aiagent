const token = localStorage.getItem('token');
if (!token) {
  window.location.href = '/';
}
loginUser();

// ═══════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════

let currentUser = null;
// TODO: Should save this chat things in the browser localStorage to not use too much of firestore
let chatIds     = [];
let chats       = {};     // { id: { id, title, type, messages: [] } }
let activeChatId = null;
let isStreaming   = false;
let contextDoc = null;
let selectedAgentName = null;

// ═══════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════

async function get_endpoint(endpoint_url){
  try {
    const response = await fetch(endpoint_url, {
  headers: {
    'Authorization': `Bearer ${token}`
  }}); // Relative path automatically points to the same server

    if(!response.ok) {
      throw new Error(`Response Status: ${response.status}`)
    }

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
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"},
    body: JSON.stringify(request)});
     
    if(!response.ok) {
      throw new Error(`Response Status: ${response.status}`)
    }

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

async function deleteContextDoc() {
  await post_endpoint("/api/contextdoc/delete")
}

async function loadChat(id) {
  if (!chats[id]) {
    let chat_json =  (await get_endpoint("/api/history/" + id))
    if (chat_json["messages"])
      if (chat_json["messages"].length > 0)
        chats[id] = { id: id, title: chat_json["messages"][0]["content"], messages: chat_json["messages"] }
      else
        chats[id] = { id: id, title: "New Chat", messages: chat_json["messages"] }
  }
}

async function loadChats() {
  chatIds = (await get_endpoint("/api/chats"))["id_list"]
  chatIds.forEach(id => {
    loadChat(id)
  })
}


async function updateAgentStatus() {
  // NOTE: Right now we dont have the logic to actually select what agent we should use, so for the business rule not be hardcoded here, we will use the first available agent
  const agentStatus = (await get_endpoint("/api/agents"));
  
  const a1dot   = document.getElementById("agent1-dot");
  const a1name  = document.getElementById("agent1-name");
  const a1badge = document.getElementById("agent1-badge");
  const a1item  = document.getElementById("agent1-item");

  const a2dot   = document.getElementById("agent2-dot");
  const a2name  = document.getElementById("agent2-name");
  const a2badge = document.getElementById("agent2-badge");
  const a2item  = document.getElementById("agent2-item");

  const ctxLabel = document.getElementById("view-ctx-label");

  console.log(agentStatus)
  if (agentStatus['researcher'] == 'available') {
     selectedAgentName = 'researcher'
     console.log("AGENTNAME " + selectedAgentName)
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
  }else if (agentStatus['manager'] == 'available'){
    // Agent 1 — locked
    selectedAgentName = 'manager'
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
  loadChats();
  const list  = document.getElementById("chat-list");
  const ids   = chatIds.sort();
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

    const item = document.createElement("div");
    item.className = `chat-item${isSelected ? " selected" : ""}`;
    item.dataset.id = id;

    const iconPath = chat.type === "onboarding"
      ? `<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>`
      : `<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-4 0v2M12 12v4M10 14h4"/>`;

    item.innerHTML = `
      <div class="chat-item-icon">
        <svg width="14" height="14" fill="none" stroke="#60A5FA" stroke-width="1.8" viewBox="0 0 24 24">${iconPath}</svg>
      </div>
      <span class="chat-item-title">${escapeHtml(chat.title)}</span>
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

async function createNewChat() {
  const hasCtx = isContextDocAvailable();
  // const type   = hasCtx ? "ops" : "onboarding";

  // const id = generateId();
  // const title = type === "onboarding"
  //  ? `Onboarding — ${new Date().toLocaleDateString("pt-BR")}`
  //  : `Chat Ops — ${new Date().toLocaleDateString("pt-BR")} ${new Date().toLocaleTimeString("pt-BR", {hour:"2-digit",minute:"2-digit"})}`;

  const id = (await post_endpoint("/api/chat/newchat"))["chat_id"]
  await loadChat(id);
  openChat(id);
}

async function deleteChat(id) {
  // TODO: Create endpoint to delete chats
  print("Chat deletion endpoint not implemented yet")
  return null
  delete chats[id];
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
  tagEl.className = "topbar-tag tag-ops";
  tagEl.textContent = "Gerente Operacional";

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

function initials(name) {
  return name.split(" ").slice(0, 2).map(w => w[0]).join("").toUpperCase();
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
  const senderName  = isUser ? "" : "Gerente Operacional";

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
  appendMessage({ role: "user", content });

  isStreaming = true;
  disableInput();
  const typingRow = showTyping();

  let apiMessages;

  const reply = (await post_endpoint("/api/chat/" + selectedAgentName + "/message/" + activeChatId, 
     {message: content}))["response"]
  removeTyping();

  console.log(reply)

  if (!chats[activeChatId]) { isStreaming = false; return; }

  chats[activeChatId].messages.push({ role: "assistant", content: reply });
  appendMessage({ role: "assistant", content: reply });

  isStreaming = false;
  enableInput();

  checkForContextDoc();
}

// ═══════════════════════════════════════════════
//  CONTEXT DOC DETECTION
// ═══════════════════════════════════════════════

function checkForContextDoc() {
  getContextDoc();

  updateAgentStatus();
  updateTopbar(chats[activeChatId]);
  renderChatList();

  // show confirmation in chat
  if (isContextDocAvailable()) {
    setTimeout(() => {
      const notif = document.createElement("div");
      notif.style.cssText = "display:flex;align-items:center;gap:10px;background:#ECFDF5;border:1px solid #A7F3D0;border-radius:8px;padding:10px 14px;font-size:13px;color:#065F46;margin:4px 0;";
      notif.innerHTML = `<svg width="16" height="16" fill="none" stroke="#059669" stroke-width="2" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <span><strong>Documento de contexto gerado.</strong> O Gerente Operacional já está disponível.</span>`;
      document.getElementById("messages").appendChild(notif);
      scrollToBottom();
    }, 300);
  }
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
  try {
    currentUser = (await get_endpoint("/api/user"))["user"]
  } catch (e) {
    console.log(e)
    window.location.href = '/';
  }

  localStorage.setItem("ops_agent_current_user", currentUser);

  document.getElementById("gate").style.display = "none";
  document.getElementById("user-avatar").textContent = initials(currentUser);
  document.getElementById("identity-name").textContent = currentUser;

  await getContextDoc();
  await loadChats();
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