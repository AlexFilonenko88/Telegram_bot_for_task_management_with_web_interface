const API_URL = 'http://localhost:8000';
let currentUserId = null;
let allTasks = [];
let weeklyChart = null;

document.getElementById('load-data').addEventListener('click', loadData);
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        filterTasks(e.target.dataset.filter);
    });
});

async function loadData() {
    const userId = document.getElementById('user-id').value;
    if (!userId) {
        showError('Пожалуйста, введите Telegram ID');
        return;
    }

    currentUserId = parseInt(userId);
    hideError();

    try {
        await Promise.all([
            loadTasks(),
            loadWeeklyStats()
        ]);

        document.getElementById('stats-section').classList.remove('hidden');
    } catch (error) {
        showError('Ошибка при загрузке данных: ' + error.message);
    }
}

async function loadTasks() {
    // API пагинирован: {"items": [...], "total": N, "limit": L, "offset": O}
    const response = await fetch(
        `${API_URL}/api/tasks?user_id=${currentUserId}&limit=100`
    );
    if (!response.ok) throw new Error('Не удалось загрузить задачи');
    const page = await response.json();
    allTasks = page.items;
    renderTasks(allTasks);
}

async function loadWeeklyStats() {
    const response = await fetch(`${API_URL}/api/tasks/stats/weekly?user_id=${currentUserId}`);
    if (!response.ok) throw new Error('Не удалось загрузить статистику');
    const stats = await response.json();
    renderStats(stats);
    renderChart(stats.daily_stats);
}

function renderStats(stats) {
    document.getElementById('total-tasks').textContent = stats.total;
    document.getElementById('done-tasks').textContent = stats.done;
    document.getElementById('active-tasks').textContent = stats.active;
    document.getElementById('percentage').textContent = stats.percentage + '%';
}

function renderChart(dailyStats) {
    const ctx = document.getElementById('weekly-chart').getContext('2d');
    
    if (weeklyChart) {
        weeklyChart.destroy();
    }

    const labels = dailyStats.map(stat => {
        const date = new Date(stat.date);
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    });
    const data = dailyStats.map(stat => stat.completed);

    weeklyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Выполнено задач',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function renderTasks(tasks) {
    const tasksList = document.getElementById('tasks-list');
    tasksList.innerHTML = '';

    if (tasks.length === 0) {
        tasksList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Нет задач</p>';
        return;
    }

    tasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    tasks.forEach(task => {
        const taskItem = document.createElement('div');
        taskItem.className = `task-item ${task.is_done ? 'done' : ''}`;
        
        const createdDate = new Date(task.created_at).toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        taskItem.innerHTML = `
            <div class="task-info">
                <div class="task-title">${escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                <div class="task-meta">
                    <span>ID: ${task.id}</span>
                    <span>Создано: ${createdDate}</span>
                </div>
            </div>
            <div class="task-status ${task.is_done ? 'done' : 'active'}">
                ${task.is_done ? '✅ Выполнено' : '⏳ В работе'}
            </div>
        `;
        
        tasksList.appendChild(taskItem);
    });
}

function filterTasks(filter) {
    let filteredTasks = allTasks;
    
    if (filter === 'active') {
        filteredTasks = allTasks.filter(task => !task.is_done);
    } else if (filter === 'done') {
        filteredTasks = allTasks.filter(task => task.is_done);
    }
    
    renderTasks(filteredTasks);
}

function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

function hideError() {
    document.getElementById('error-message').classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
