// app.js
// handles user selection, sending messages, rendering chat bubbles, typing indicator

let currentUser = 'Fernandes'

// swiggy palette: orange, black, dark orange
const userColors = {
  'Fernandes': '#FC8019',
  'Ila':       '#282C3F',
  'Shaikh':    '#e8701a',
}

const userInitials = {
  'Fernandes': 'F',
  'Ila':       'I',
  'Shaikh':    'S',
}

function getGreeting(name) {
  const dear = name === 'Ila' ? `Dear Ila` : `Hey team`
  return `
    👋 ${dear}! I'm <strong>LunchBot</strong> — your group lunch coordinator.<br/>
    Tell me what you're craving and I'll sort out the order! 🍕🍛🥗
  `
}

function selectUser(name, el) {
  currentUser = name

  // reset all pills
  document.querySelectorAll('.pill').forEach(p => {
    p.classList.remove('active')
    const av = p.querySelector('.pill-avatar')
    if (av && av.dataset.color) {
      av.style.background = av.dataset.color
    }
  })

  // activate clicked pill
  el.classList.add('active')
}

async function sendMessage() {
  const input = document.getElementById('msgInput')
  const text = input.value.trim()
  if (!text) return

  appendMessage(currentUser, text, 'user')
  input.value = ''

  const typingId = showTyping()

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user: currentUser, message: text })
    })
    const data = await res.json()
    removeTyping(typingId)
    appendMessage('LunchBot', data.reply, 'bot')
  } catch (err) {
    removeTyping(typingId)
    appendMessage('LunchBot', 'Oops, something went wrong. Try again!', 'bot')
    console.error('Chat error:', err)
  }
}

function appendMessage(sender, text, type) {
  const chatWindow = document.getElementById('chatWindow')
  const wrapper = document.createElement('div')

  if (type === 'bot') {
    wrapper.className = 'bot-message'
    wrapper.innerHTML = `
      <div class="avatar">🤖</div>
      <div class="bubble bot-bubble">${formatText(text)}</div>
    `
  } else {
    const color = userColors[sender] || '#FC8019'
    const initial = userInitials[sender] || sender[0]
    wrapper.className = 'user-message'
    wrapper.innerHTML = `
      <div class="bubble user-bubble" style="background:${color}">
        <span class="sender-name">${sender}</span>
        ${formatText(text)}
      </div>
      <div class="user-avatar" style="background:${color}">${initial}</div>
    `
  }

  chatWindow.appendChild(wrapper)
  chatWindow.scrollTop = chatWindow.scrollHeight
}

function showTyping() {
  const chatWindow = document.getElementById('chatWindow')
  const id = 'typing-' + Date.now()
  const div = document.createElement('div')
  div.className = 'bot-message'
  div.id = id
  div.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="bubble typing-bubble">
      <span></span><span></span><span></span>
    </div>
  `
  chatWindow.appendChild(div)
  chatWindow.scrollTop = chatWindow.scrollHeight
  return id
}

function removeTyping(id) {
  const el = document.getElementById(id)
  if (el) el.remove()
}

function formatText(text) {
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\n/g, '<br/>')
  return text
}

async function resetSession() {
  try {
    await fetch('/reset', { method: 'POST' })
  } catch (err) {
    console.error('Reset failed:', err)
  }

  const chatWindow = document.getElementById('chatWindow')
  chatWindow.innerHTML = `
    <div class="date-chip">Today</div>
    <div class="bot-message">
      <div class="avatar">🤖</div>
      <div class="bubble bot-bubble">${getGreeting(currentUser)}</div>
    </div>
  `

  selectUser('Fernandes', document.querySelector('.pill'))
}
