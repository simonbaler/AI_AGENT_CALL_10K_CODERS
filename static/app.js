const callForm = document.getElementById('callForm')
const callBtn = document.getElementById('callBtn')
const status = document.getElementById('status')
const connecting = document.getElementById('connecting')
const statusLight = document.querySelector('.status-light')
const customerFile = document.getElementById('customerFile')
const automationToggle = document.getElementById('automationToggle')
const logRows = document.getElementById('logRows')
const logSummary = document.getElementById('logSummary')
const agentState = document.getElementById('agentState')
const coursesToggle = document.getElementById('coursesToggle')
const coursesPanel = document.getElementById('coursesPanel')
const courseCards = document.getElementById('courseCards')
const chatForm = document.getElementById('chatForm')
const chatInput = document.getElementById('chatInput')
const chatMessages = document.getElementById('chatMessages')
const sidebarToggle = document.getElementById('sidebarToggle')
let selectedCourses = []

function renderLogs(logs){
  logSummary.textContent = `${logs.length} records`
  logRows.innerHTML = logs.length ? logs.map(log => `<tr><td><strong>${log.name || 'Unknown customer'}</strong><small>${log.age || '--'} years</small></td><td>${log.phone || '--'}</td><td>${log.language || '--'}</td><td><span class="log-status">${log.status || log.event || '--'}</span></td><td>${log.duration || '--'} sec</td><td>${log.timestamp || '--'}</td></tr>`).join('') : '<tr><td colspan="6" class="empty-logs">No call activity yet.</td></tr>'
}

async function refreshLogs(){
  const response = await fetch('/call_logs')
  if(response.ok){ const data = await response.json(); renderLogs(data.logs); if(data.agent) agentState.textContent = data.agent.running ? `Calling queue · ${data.agent.queued} remaining` : `${data.agent.completed || 0} completed · ready to assist` }
}

function setConnecting(on){
  connecting.style.visibility = on ? 'visible' : 'hidden'
  callBtn.disabled = on
  status.textContent = on ? 'Connecting...' : 'Ready when you are'
  statusLight.classList.toggle('active', on)
}

callForm.addEventListener('submit', async (event)=>{
  event.preventDefault()
  if(!callForm.reportValidity()) return

  setConnecting(true)
  const formData = new FormData(callForm)

  try{
    const resp = await fetch('/trigger_call',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name: formData.get('name').trim(), age: formData.get('age').trim(), college: formData.get('college').trim(), phone: formData.get('phone').trim(), language: formData.get('language')})
    })
    const data = await resp.json()
    if(resp.ok){
      status.textContent = data.status === 'simulated' ? 'Simulation complete' : 'Call started successfully'
    } else {
      status.textContent = data.error || 'Error'
    }
  }catch(err){
    status.textContent = err.message || 'Network error'
  }finally{
    setTimeout(()=>setConnecting(false), 1600)
  }
})

customerFile.addEventListener('change', async () => {
  if(!customerFile.files[0]) return
  const body = new FormData(); body.append('file', customerFile.files[0])
  agentState.textContent = 'Agent is importing leads...'
  const response = await fetch('/upload_customers', {method:'POST', body})
  const data = await response.json()
  agentState.textContent = response.ok ? `${data.imported} customers queued` : (data.error || 'Import failed')
  customerFile.value = ''
})

automationToggle.addEventListener('change', async () => {
  if(!automationToggle.checked){ agentState.textContent = 'Automation paused'; fetch('/automation', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({enabled:false})}); return }
  agentState.textContent = 'Agent is starting the queue...'
  const response = await fetch('/automation', {method:'POST'})
  const data = await response.json()
  agentState.textContent = response.ok && data.started ? 'Agent is calling one by one' : (data.agent?.queued ? 'Queue already running' : 'Import a CSV first')
  refreshLogs()
})
document.getElementById('refreshLogs').addEventListener('click', refreshLogs)
coursesToggle.addEventListener('click', async () => {
  const opening = coursesPanel.hidden
  coursesPanel.hidden = !opening
  coursesToggle.setAttribute('aria-expanded', String(opening))
  coursesToggle.innerHTML = opening ? 'Hide booked sessions <span>−</span>' : 'Show booked sessions <span>+</span>'
  if(!opening) return
  const response = await fetch('/selected_courses')
  const data = await response.json()
  selectedCourses = data.courses
  renderCourses('all')
})
function renderCourses(filter){
  const courses = filter === 'all' ? selectedCourses : selectedCourses.filter(course => (course.course_name || '').toLowerCase().includes(filter))
  document.getElementById('bookingCount').textContent = selectedCourses.length
  document.getElementById('pythonCount').textContent = selectedCourses.filter(course => (course.course_name || '').toLowerCase().includes('python')).length
  document.getElementById('javaCount').textContent = selectedCourses.filter(course => (course.course_name || '').toLowerCase().includes('java')).length
  courseCards.innerHTML = courses.length ? courses.map(course => `<article class="course-card"><span class="course-icon">◈</span><div><strong>${course.course_name || 'Course'}</strong><small>${course.student_name || 'Customer'} · ${course.college || 'College not recorded'}</small></div><div class="course-slot"><b>${course.demo_date || '--'}</b><span>${course.demo_time || '--'} · ${course.language || '--'}</span></div><em>${course.booking_status || 'confirmed'}</em></article>`).join('') : '<p class="empty-logs">No booked demos for this role.</p>'
}
document.querySelectorAll('.course-filter').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('.course-filter').forEach(item => item.classList.remove('active')); button.classList.add('active'); renderCourses(button.dataset.filter) }))
setInterval(refreshLogs, 10000)

function addChatMessage(text, role){
  const message = document.createElement('div'); message.className = `chat-message ${role}-message`
  message.innerHTML = role === 'agent' ? `<span class="chat-avatar">✦</span><p></p>` : '<p></p>'
  message.querySelector('p').textContent = text
  chatMessages.appendChild(message); chatMessages.scrollTop = chatMessages.scrollHeight
}
async function askAssistant(question){
  addChatMessage(question, 'user'); chatInput.value = ''
  const response = await fetch('/assistant', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message: question})})
  const data = await response.json(); addChatMessage(response.ok ? data.answer : (data.error || 'Assistant unavailable.'), 'agent')
}
chatForm.addEventListener('submit', (event) => { event.preventDefault(); if(chatInput.value.trim()) askAssistant(chatInput.value.trim()) })
document.querySelectorAll('.assistant-suggestions button').forEach(button => button.addEventListener('click', () => askAssistant(button.dataset.question)))
sidebarToggle.addEventListener('click', () => document.getElementById('sidebar').classList.toggle('open'))
document.querySelectorAll('.side-link').forEach(link => link.addEventListener('click', () => document.getElementById('sidebar').classList.remove('open')))
