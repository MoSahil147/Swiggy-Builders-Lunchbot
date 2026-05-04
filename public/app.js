// user selection, sending messages, rendering chat bubbles, typing indicator

// track who's currently "logged in" as
let currentUser = 'Fernandes'

// each team member gets a distinct color so it's easy to follow in the chat
const userColors = {
  'Fernandes':   '#4f46e5',
  'Ila': '#db2777',
  'Shaikh':  '#059669'
}

// called when someone clicks a name pill
function selectUser(name, el) {
  currentUser = name

  // reset all pills then activate the clicked one
  document.querySelectorAll('.pill').forEach(p => {
    p.classList.remove('active')
    p.style.background = ''
    p.style.borderColor = ''
    p.style.color = ''
  })

  el.classList.add('active')
  el.style.background = userColors[name]
  el.style.borderColor = userColors[name]
  el.style.color = 'white'
}

// main send function — triggered by button click or Enter key
async function sendMessage() {
  const input = document.getElementById('msgInput')
  const text = input.value.trim()

  // don't send empty messages
  if (!text) return

  // show the user's message immediately
  appendMessage(currentUser, text, 'user')
  input.value = ''

  // show typing dots while waiting for response
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
    // something went wrong with the request
    removeTyping(typingId)
    appendMessage('LunchBot', 'Oops, something went wrong. Try again!', 'bot')
    console.error('Chat error:', err)
  }
}

// renders a message bubble in the chat window
function appendMessage(sender, text, type) {
  const chatWindow = document.getElementById('chatWindow')

  const wrapper = document.createElement('div')
  wrapper.className = type === 'bot' ? 'bot-message' : 'user-message'

  if (type === 'bot') {
    // bot messages: avatar on left, gray bubble
    wrapper.innerHTML = `
      <div class="avatar">🤖</div>
      <div class="bubble bot-bubble">${formatText(text)}</div>
    `
  } else {
    // user messages: colored left border to distinguish between team members
    const color = userColors[sender] || '#4f46e5'
    wrapper.innerHTML = `
      <div class="bubble user-bubble" style="border-left: 3px solid ${color}">
        <span class="sender-name" style="color: ${color}">${sender}</span>
        ${formatText(text)}
      </div>
    `
  }

  chatWindow.appendChild(wrapper)

  // auto scroll to latest message
  chatWindow.scrollTop = chatWindow.scrollHeight
}

// shows the animated typing dots while bot is thinking
function showTyping() {
  const chatWindow = document.getElementById('chatWindow')

  // unique id so we can remove it later
  const id = 'typing-' + Date.now()

  const div = document.createElement('div')
  div.className = 'bot-message'
  div.id = id
  div.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="bubble typing-bubble">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `

  chatWindow.appendChild(div)
  chatWindow.scrollTop = chatWindow.scrollHeight

  return id
}

// removes the typing indicator once response is ready
function removeTyping(id) {
  const el = document.getElementById(id)
  if (el) el.remove()
}

// basic text formatting so bot responses look decent
function formatText(text) {
  // **bold** → <strong>
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

  // newlines → <br>
  text = text.replace(/\n/g, '<br/>')

  return text
}

// resets the entire session — clears backend history + cart + frontend chat
async function resetSession() {
  try {
    await fetch('/reset', { method: 'POST' })
  } catch (err) {
    console.error('Reset failed:', err)
  }

  // clear the chat window and show the welcome message again
  const chatWindow = document.getElementById('chatWindow')
  chatWindow.innerHTML = `
    <div class="bot-message">
      <div class="avatar">🌮</div>
      <div class="bubble bot-bubble">
        Dear Ila I'm LunchBot from The LunchBox. Tell me what you're craving today and I'll sort out the group order!
      </div>
    </div>
  `

  // also reset the user selector back to Raj
  selectUser('Fernandes', document.querySelector('.pill'))
}