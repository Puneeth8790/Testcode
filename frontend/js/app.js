/**
 * TaskStream Frontend Logic
 * Interacts with FastAPI backend endpoints (/api/v1/items, /api/v1/health)
 */

const API_BASE = '/api/v1';

// DOM Elements
const taskGrid = document.getElementById('taskGrid');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const statusTabs = document.getElementById('statusTabs');
const priorityFilter = document.getElementById('priorityFilter');
const healthPill = document.getElementById('healthPill');
const healthText = document.getElementById('healthText');

// Stat Counters
const statTotal = document.getElementById('statTotal');
const statPending = document.getElementById('statPending');
const statInProgress = document.getElementById('statInProgress');
const statCompleted = document.getElementById('statCompleted');
const statHigh = document.getElementById('statHigh');

// Modal Elements
const taskModal = document.getElementById('taskModal');
const modalTitle = document.getElementById('modalTitle');
const taskForm = document.getElementById('taskForm');
const taskIdInput = document.getElementById('taskId');
const taskTitleInput = document.getElementById('taskTitleInput');
const taskDescInput = document.getElementById('taskDescInput');
const taskPriorityInput = document.getElementById('taskPriorityInput');
const taskStatusInput = document.getElementById('taskStatusInput');
const openCreateModalBtn = document.getElementById('openCreateModalBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelModalBtn = document.getElementById('cancelModalBtn');

// State Management
let currentStatusFilter = '';
let currentPriorityFilter = '';
let searchQuery = '';
let debounceTimer = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    fetchStats();
    fetchTasks();

    setupEventListeners();
});

function setupEventListeners() {
    // Search input listener with debounce
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            searchQuery = e.target.value.trim();
            fetchTasks();
        }, 300);
    });

    // Status filter tabs
    statusTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-btn')) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            currentStatusFilter = e.target.dataset.status;
            fetchTasks();
        }
    });

    // Priority filter dropdown
    priorityFilter.addEventListener('change', (e) => {
        currentPriorityFilter = e.target.value;
        fetchTasks();
    });

    // Stat card quick filters
    document.querySelectorAll('.stat-card').forEach(card => {
        card.addEventListener('click', () => {
            if (card.dataset.filter !== undefined) {
                const targetStatus = card.dataset.filter === 'all' ? '' : card.dataset.filter;
                currentStatusFilter = targetStatus;
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.status === targetStatus);
                });
                fetchTasks();
            } else if (card.dataset.priority) {
                currentPriorityFilter = card.dataset.priority;
                priorityFilter.value = card.dataset.priority;
                fetchTasks();
            }
        });
    });

    // Modal triggers
    openCreateModalBtn.addEventListener('click', () => openModal());
    closeModalBtn.addEventListener('click', closeModal);
    cancelModalBtn.addEventListener('click', closeModal);
    taskModal.addEventListener('click', (e) => {
        if (e.target === taskModal) closeModal();
    });

    // Form submission
    taskForm.addEventListener('submit', handleTaskSubmit);
}

// Health Check
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            healthText.textContent = "System Online";
            healthPill.querySelector('.status-dot').className = "status-dot green";
        } else {
            throw new Error();
        }
    } catch {
        healthText.textContent = "Offline / Connecting...";
        healthPill.querySelector('.status-dot').className = "status-dot red";
    }
}

// Fetch Stats
async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/items/stats`);
        if (!res.ok) return;
        const stats = await res.json();
        
        statTotal.textContent = stats.total;
        statPending.textContent = stats.pending;
        statInProgress.textContent = stats.in_progress;
        statCompleted.textContent = stats.completed;
        statHigh.textContent = stats.high_priority;
    } catch (err) {
        console.error('Failed to load task stats:', err);
    }
}

// Fetch Tasks
async function fetchTasks() {
    try {
        const params = new URLSearchParams();
        if (currentStatusFilter) params.append('status', currentStatusFilter);
        if (currentPriorityFilter) params.append('priority', currentPriorityFilter);
        if (searchQuery) params.append('search', searchQuery);

        const res = await fetch(`${API_BASE}/items?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch tasks");

        const tasks = await res.json();
        renderTasks(tasks);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Render Tasks to DOM
function renderTasks(tasks) {
    taskGrid.innerHTML = '';
    
    if (tasks.length === 0) {
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    tasks.forEach(task => {
        const card = document.createElement('div');
        card.className = 'task-card';
        
        const priorityClass = `badge-${task.priority}`;
        const formattedDate = new Date(task.created_at).toLocaleDateString(undefined, {
            month: 'short', day: 'numeric'
        });

        card.innerHTML = `
            <div class="task-header">
                <h4 class="task-title">${escapeHtml(task.title)}</h4>
                <span class="badge ${priorityClass}">${task.priority}</span>
            </div>
            <p class="task-desc">${escapeHtml(task.description || 'No description provided.')}</p>
            <div class="task-footer">
                <select class="status-select" data-id="${task.id}">
                    <option value="pending" ${task.status === 'pending' ? 'selected' : ''}>Pending</option>
                    <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                    <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>Completed</option>
                </select>
                <div class="task-actions">
                    <button class="btn-icon edit" data-id="${task.id}" title="Edit Task">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-icon delete" data-id="${task.id}" title="Delete Task">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </div>
        `;

        // Event listeners for inline actions
        const statusSelect = card.querySelector('.status-select');
        statusSelect.addEventListener('change', (e) => updateTaskStatus(task.id, e.target.value));

        const editBtn = card.querySelector('.btn-icon.edit');
        editBtn.addEventListener('click', () => openModal(task));

        const deleteBtn = card.querySelector('.btn-icon.delete');
        deleteBtn.addEventListener('click', () => deleteTask(task.id));

        taskGrid.appendChild(card);
    });
}

// Create or Update Task
async function handleTaskSubmit(e) {
    e.preventDefault();
    const id = taskIdInput.value;
    const payload = {
        title: taskTitleInput.value.trim(),
        description: taskDescInput.value.trim() || null,
        priority: taskPriorityInput.value,
        status: taskStatusInput.value,
    };

    try {
        let res;
        if (id) {
            res = await fetch(`${API_BASE}/items/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } else {
            res = await fetch(`${API_BASE}/items`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }

        if (!res.ok) throw new Error("Failed to save task item");

        showToast(id ? 'Task updated successfully' : 'New task created!', 'success');
        closeModal();
        fetchTasks();
        fetchStats();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Update Status directly
async function updateTaskStatus(id, newStatus) {
    try {
        const res = await fetch(`${API_BASE}/items/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error("Failed to update status");

        showToast("Task status updated", "success");
        fetchStats();
    } catch (err) {
        showToast(err.message, "error");
        fetchTasks();
    }
}

// Delete Task
async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        const res = await fetch(`${API_BASE}/items/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error("Failed to delete task");

        showToast("Task deleted successfully", "success");
        fetchTasks();
        fetchStats();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Modal Helpers
function openModal(task = null) {
    if (task) {
        modalTitle.textContent = "Edit Task";
        taskIdInput.value = task.id;
        taskTitleInput.value = task.title;
        taskDescInput.value = task.description || '';
        taskPriorityInput.value = task.priority;
        taskStatusInput.value = task.status;
    } else {
        modalTitle.textContent = "Create New Task";
        taskForm.reset();
        taskIdInput.value = '';
    }
    taskModal.classList.remove('hidden');
}

function closeModal() {
    taskModal.classList.add('hidden');
    taskForm.reset();
}

// Toast Helpers
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
    
    document.getElementById('toastContainer').appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3500);
}

function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}
