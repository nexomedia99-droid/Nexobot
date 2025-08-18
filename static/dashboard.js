// Dashboard JavaScript
let charts = {};
let updateInterval;
let currentTheme = localStorage.getItem('theme') || 'light';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeCharts();
    loadInitialData();
    startAutoRefresh();
    setupEventListeners();
});

// Theme Management
function initializeTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon();
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeIcon();

    // Update charts for new theme
    setTimeout(() => {
        updateChartColors();
    }, 100);
}

function updateThemeIcon() {
    const themeIcon = document.querySelector('#theme-toggle i');
    if (themeIcon) {
        themeIcon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

function updateChartColors() {
    const isDark = currentTheme === 'dark';
    const textColor = isDark ? '#ffffff' : '#5a5c69';
    const gridColor = isDark ? '#495057' : '#e3e6f0';

    Object.values(charts).forEach(chart => {
        if (chart.options.scales) {
            chart.options.scales.x.ticks.color = textColor;
            chart.options.scales.y.ticks.color = textColor;
            chart.options.scales.x.grid.color = gridColor;
            chart.options.scales.y.grid.color = gridColor;
        }
        if (chart.options.plugins && chart.options.plugins.legend) {
            chart.options.plugins.legend.labels.color = textColor;
        }
        chart.update();
    });
}

// Chart Initialization
function initializeCharts() {
    // Activity Chart
    const activityCtx = document.getElementById('activityChart').getContext('2d');
    charts.activity = new Chart(activityCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Registrations',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Job Applications',
                data: [],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'AI Requests',
                data: [],
                borderColor: '#17a2b8',
                backgroundColor: 'rgba(23, 162, 184, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Daily Activity Trends'
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Count'
                    },
                    beginAtZero: true
                }
            }
        }
    });

    // Job Status Chart
    const jobStatusCtx = document.getElementById('jobStatusChart').getContext('2d');
    charts.jobStatus = new Chart(jobStatusCtx, {
        type: 'doughnut',
        data: {
            labels: ['Active', 'Closed', 'Paid'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    '#28a745',
                    '#dc3545',
                    '#ffc107'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Job Status Distribution'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Data Loading Functions
async function loadInitialData() {
    try {
        showLoading();
        await Promise.all([
            loadStats(),
            loadActivities(),
            loadAnalytics()
        ]);
        hideLoading();
    } catch (error) {
        console.error('Error loading initial data:', error);
        showError('Failed to load dashboard data');
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        updateStatsDisplay(data);
        updateSystemStatus(data);

    } catch (error) {
        console.error('Error loading stats:', error);
        showError('Failed to load statistics');
    }
}

async function loadActivities() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        updateActivitiesDisplay(data.recent_activities || []);

    } catch (error) {
        console.error('Error loading activities:', error);
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        updateChartsData(data);

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Display Update Functions
function updateStatsDisplay(data) {
    // Update stat cards
    document.getElementById('total-users').textContent = data.total_users?.toLocaleString() || '0';
    document.getElementById('active-jobs').textContent = data.active_jobs?.toLocaleString() || '0';
    document.getElementById('ai-requests').textContent = data.ai_requests?.toLocaleString() || '0';
    document.getElementById('total-points').textContent = data.total_points?.toLocaleString() || '0';

    // Update status indicator
    const statusIndicator = document.getElementById('status-indicator');
    if (statusIndicator) {
        statusIndicator.textContent = data.bot_status === 'online' ? 'Online' : 'Offline';
        statusIndicator.className = data.bot_status === 'online' ? 'text-success' : 'text-danger';
    }
}

function updateSystemStatus(data) {
    // Update uptime
    const uptimeElement = document.getElementById('uptime');
    if (uptimeElement) {
        uptimeElement.textContent = data.uptime || 'Unknown';
    }

    // Update environment status
    const envStatus = data.environment_vars || {};
    updateStatusElement('bot-token-status', envStatus.bot_token);
    updateStatusElement('gemini-api-status', envStatus.gemini_api);
    updateStatusElement('owner-id-status', envStatus.owner_id);

    // Update last activity
    const lastActivityElement = document.getElementById('last-activity');
    if (lastActivityElement) {
        lastActivityElement.textContent = data.last_activity || 'Unknown';
    }
}

function updateStatusElement(elementId, status) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = status || 'Unknown';
        element.className = status?.includes('✅') ? 'fw-bold status-configured' : 'fw-bold status-missing';
    }
}

function updateActivitiesDisplay(activities) {
    const activitiesList = document.getElementById('activities-list');
    if (!activitiesList) return;

    if (!activities || activities.length === 0) {
        activitiesList.innerHTML = '<div class="text-center text-muted">No recent activities</div>';
        return;
    }

    const activitiesHtml = activities.map(activity => {
        const typeIcon = getActivityIcon(activity.type);
        const timeAgo = getTimeAgo(activity.timestamp);

        return `
            <div class="activity-item fade-in">
                <div class="activity-type">
                    <i class="${typeIcon} me-2"></i>${formatActivityType(activity.type)}
                </div>
                <div class="activity-description">${activity.description || 'No description'}</div>
                <div class="activity-time">${timeAgo}</div>
            </div>
        `;
    }).join('');

    activitiesList.innerHTML = activitiesHtml;
}

function updateChartsData(data) {
    // Update job status chart
    if (data.job_status_distribution && charts.jobStatus) {
        const jobData = data.job_status_distribution;
        charts.jobStatus.data.datasets[0].data = [
            jobData.aktif || 0,
            jobData.close || 0,
            jobData.cair || 0
        ];
        charts.jobStatus.update();
    }

    // Update activity chart
    if (data.registration_trend && charts.activity) {
        const trend = data.registration_trend;
        charts.activity.data.labels = trend.map(item => item.date);
        charts.activity.data.datasets[0].data = trend.map(item => item.count);
        charts.activity.update();
    }
}

// User Management
async function showUserModal() {
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
    await loadUsers();
}

async function loadUsers(page = 1, search = '') {
    try {
        const params = new URLSearchParams({ page, limit: 20 });
        if (search) params.append('search', search);

        const response = await fetch(`/api/users?${params}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        updateUsersTable(data);

    } catch (error) {
        console.error('Error loading users:', error);
        showError('Failed to load users');
    }
}

function updateUsersTable(data) {
    const tableContainer = document.getElementById('users-table');
    if (!tableContainer) return;

    const tableHtml = `
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>Username</th>
                    <th>Points</th>
                    <th>Badges</th>
                    <th>Referrals</th>
                    <th>Applies</th>
                    <th>Joined</th>
                </tr>
            </thead>
            <tbody>
                ${data.users.map(user => `
                    <tr>
                        <td><strong>${user.username}</strong></td>
                        <td><span class="badge bg-primary">${user.points || 0}</span></td>
                        <td><small>${user.badges?.join(', ') || 'None'}</small></td>
                        <td>${user.referrals || 0}</td>
                        <td>${user.total_applies || 0}</td>
                        <td><small>${new Date(user.created_at).toLocaleDateString()}</small></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>

        <div class="d-flex justify-content-between align-items-center mt-3">
            <small class="text-muted">
                Showing ${data.users.length} of ${data.total} users
            </small>
            <nav>
                <ul class="pagination pagination-sm mb-0">
                    ${generatePagination(data.page, data.pages)}
                </ul>
            </nav>
        </div>
    `;

    tableContainer.innerHTML = tableHtml;
}

// Job Management
async function showJobModal() {
    const modal = new bootstrap.Modal(document.getElementById('jobModal'));
    modal.show();
    await loadJobs();
}

async function loadJobs(page = 1, status = '') {
    try {
        const params = new URLSearchParams({ page, limit: 20 });
        if (status) params.append('status', status);

        const response = await fetch(`/api/jobs?${params}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        updateJobsTable(data);

    } catch (error) {
        console.error('Error loading jobs:', error);
        showError('Failed to load jobs');
    }
}

function updateJobsTable(data) {
    const tableContainer = document.getElementById('jobs-table');
    if (!tableContainer) return;

    const tableHtml = `
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Fee</th>
                    <th>Status</th>
                    <th>Applicants</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
                ${data.jobs.map(job => `
                    <tr>
                        <td><strong>#${job.id}</strong></td>
                        <td>${job.title.substring(0, 50)}${job.title.length > 50 ? '...' : ''}</td>
                        <td><span class="badge bg-success">${job.fee}</span></td>
                        <td><span class="badge bg-${getStatusColor(job.status)}">${job.status.toUpperCase()}</span></td>
                        <td>${job.applicant_count || 0}</td>
                        <td><small>${new Date(job.created_at).toLocaleDateString()}</small></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>

        <div class="d-flex justify-content-between align-items-center mt-3">
            <small class="text-muted">
                Showing ${data.jobs.length} of ${data.total} jobs
            </small>
            <nav>
                <ul class="pagination pagination-sm mb-0">
                    ${generatePagination(data.page, data.pages)}
                </ul>
            </nav>
        </div>
    `;

    tableContainer.innerHTML = tableHtml;
}

// Utility Functions
function getActivityIcon(type) {
    const icons = {
        'registration': 'fas fa-user-plus',
        'job_apply': 'fas fa-briefcase',
        'ai_request': 'fas fa-robot',
        'job_posted': 'fas fa-plus-circle',
        'edit_info': 'fas fa-edit',
        'bot_start': 'fas fa-play-circle',
        'error': 'fas fa-exclamation-triangle'
    };
    return icons[type] || 'fas fa-info-circle';
}

function formatActivityType(type) {
    const types = {
        'registration': 'New Registration',
        'job_apply': 'Job Application',
        'ai_request': 'AI Request',
        'job_posted': 'Job Posted',
        'edit_info': 'Profile Edit',
        'bot_start': 'Bot Started',
        'error': 'Error'
    };
    return types[type] || type;
}

function getTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 30) return `${diffDays}d ago`;
    return time.toLocaleDateString();
}

function getStatusColor(status) {
    const colors = {
        'aktif': 'success',
        'close': 'danger',
        'cair': 'warning'
    };
    return colors[status] || 'secondary';
}

function generatePagination(currentPage, totalPages) {
    if (totalPages <= 1) return '';

    let pagination = '';
    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);

    if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1);
    }

    // Previous button
    pagination += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Previous</a>
        </li>
    `;

    // Page numbers
    for (let i = start; i <= end; i++) {
        pagination += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }

    // Next button
    pagination += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Next</a>
        </li>
    `;

    return pagination;
}

// Event Handlers
function setupEventListeners() {
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

    // Job status filter
    document.querySelectorAll('input[name="status-filter"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            loadJobs(1, e.target.value);
        });
    });

    // User search
    document.getElementById('user-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchUsers();
        }
    });
}

// Action Functions
function refreshAllData() {
    loadInitialData();
    showSuccess('All data refreshed');
}

function refreshActivities() {
    loadActivities();
}

function refreshUsers() {
    loadUsers();
}

function refreshJobs() {
    loadJobs();
}

function searchUsers() {
    const searchTerm = document.getElementById('user-search').value;
    loadUsers(1, searchTerm);
}

function changePage(page) {
    // This will be implemented based on which modal is open
    const userModal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
    const jobModal = bootstrap.Modal.getInstance(document.getElementById('jobModal'));

    if (userModal && userModal._isShown) {
        const search = document.getElementById('user-search').value;
        loadUsers(page, search);
    } else if (jobModal && jobModal._isShown) {
        const status = document.querySelector('input[name="status-filter"]:checked').value;
        loadJobs(page, status);
    }
}

// Auto Refresh
function startAutoRefresh() {
    updateInterval = setInterval(() => {
        loadStats();
        loadActivities();
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
}

// UI Helper Functions
function showLoading() {
    // Implementation for loading state
}

function hideLoading() {
    // Implementation for hiding loading state
}

function showError(message) {
    console.error(message);
    // Could implement toast notifications here
}

function showSuccess(message) {
    console.log(message);
    // Could implement toast notifications here
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});
