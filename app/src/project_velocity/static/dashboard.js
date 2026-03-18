async function fetchJson(url, options) {
  const response = await fetch(url, options)
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Request failed')
  return data
}

function renderList(id, items, formatter) {
  const container = document.getElementById(id)
  container.innerHTML = ''
  items.forEach((item) => {
    const node = document.createElement('div')
    node.className = 'tile'
    node.innerHTML = formatter(item)
    container.appendChild(node)
  })
}

function renderBulletList(id, items, formatter) {
  const list = document.getElementById(id)
  list.innerHTML = ''
  items.forEach((item) => {
    const li = document.createElement('li')
    li.innerHTML = formatter(item)
    list.appendChild(li)
  })
}

function setMessage(text, isError = false) {
  const node = document.getElementById('message')
  node.textContent = text || ''
  node.className = isError ? 'message error' : 'message'
}

function hydrate(data) {
  document.getElementById('goal').textContent = data.program.goal
  renderList('accounts', data.accounts, (item) => `<strong>${item.ownerName}</strong><div class="meta">${item.accountId} · $${item.balance}</div>`)
  renderList('transfers', data.recentTransfers, (item) => `<strong>$${item.amount}</strong><div class="meta">${item.sourceAccount} → ${item.destinationAccount}</div><div>${item.reference}</div>`)
  renderBulletList('incidents', data.incidents, (item) => `<strong>${item.title}</strong>: ${item.summary}`)
  renderBulletList('risks', data.businessRisks, (item) => `<strong>${item.name}</strong>: ${item.description}`)
  renderBulletList('checks', data.requiredChecks, (item) => item)
  renderList('drills', data.demoExercises, (item) => `<strong>${item.name}</strong><div>${item.objective}</div><div class="meta">Blocked by: ${item.blockedBy.join(', ')}</div><div class="meta">${item.steps.join(' ')}</div>`)
}

async function loadDashboard() {
  try {
    const data = await fetchJson('/api/dashboard')
    hydrate(data)
  } catch (error) {
    setMessage(error.message, true)
  }
}

document.getElementById('transfer-form').addEventListener('submit', async (event) => {
  event.preventDefault()
  const formData = new FormData(event.target)
  const payload = Object.fromEntries(formData.entries())
  try {
    const data = await fetchJson('/api/transfers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    hydrate(data)
    setMessage(data.message)
    event.target.reset()
  } catch (error) {
    setMessage(error.message, true)
  }
})

loadDashboard()
