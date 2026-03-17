const API_URL = 'http://localhost:8000/agent';
const TASKS_URL = 'http://localhost:8000/tasks';
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const exampleBtns = document.querySelectorAll('.example-btn');
const tasksList = document.getElementById('tasksList');

function addMessage(text, type = 'agent') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function loadTasks() {
    try {
        const response = await fetch(TASKS_URL);
        const data = await response.json();
        displayTasks(data.tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function displayTasks(tasks) {
    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = '<div class="empty-state">אין משימות כרגע</div>';
        return;
    }

    tasksList.innerHTML = tasks.map(task => {
        const date = task.created_at ? new Date(task.created_at).toLocaleString('he-IL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : '';
        
        return `
        <div class="task-item ${task.completed ? 'completed' : ''}" data-task-id="${task.id}">
            <span class="task-id">#${task.id}</span>
            <div class="task-title">${task.title}</div>
            ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
            ${date ? `<div class="task-date">📅 נוצר: ${date}</div>` : ''}
            <span class="task-status ${task.completed ? 'completed' : 'pending'}">
                ${task.completed ? '✓ הושלמה' : '⏳ ממתינה'}
            </span>
        </div>
    `;
    }).join('');
}

async function sendMessage(message) {
    if (!message.trim()) return;

    addMessage(message, 'user');
    messageInput.value = '';
    sendBtn.disabled = true;

    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message loading';
    loadingMsg.textContent = '⏳ Agent מעבד את הבקשה...';
    messagesDiv.appendChild(loadingMsg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        loadingMsg.remove();

        if (!response.ok) {
            throw new Error('שגיאה בתקשורת עם השרת');
        }

        const data = await response.json();
        
        if (data.error) {
            addMessage(`❌ שגיאה: ${data.error}`, 'error');
        } else if (data.choices && data.choices[0] && data.choices[0].message) {
            const agentResponse = data.choices[0].message.content;
            addMessage(agentResponse, 'agent');
            await loadTasks();
        } else {
            addMessage('❌ תשובה לא תקינה מהשרת', 'error');
            console.error('Response:', data);
        }

    } catch (error) {
        loadingMsg.remove();
        addMessage(`❌ שגיאה: ${error.message}`, 'error');
        console.error('Error:', error);
    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

sendBtn.addEventListener('click', () => {
    sendMessage(messageInput.value);
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage(messageInput.value);
    }
});

exampleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const message = btn.getAttribute('data-msg');
        messageInput.value = message;
        sendMessage(message);
    });
});

addMessage('👋 שלום! אני Agent לניהול משימות. איך אוכל לעזור לך היום?', 'agent');
loadTasks();
