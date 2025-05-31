document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    // Load user info
    loadUserInfo();
    
    // Load dashboard data
    loadDashboardStats();
    loadRecentActivity();
    loadGPUStatus();
});

async function loadUserInfo() {
    try {
        const response = await fetch('/api/v1/auth/me', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            document.getElementById('username').textContent = user.username;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/v1/dashboard/stats', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalModels').textContent = stats.total_models;
            document.getElementById('activeApiKeys').textContent = stats.active_api_keys;
            document.getElementById('totalInferences').textContent = stats.total_inferences;
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch('/api/v1/dashboard/activity', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const activities = await response.json();
            const activityList = document.getElementById('activityList');
            activityList.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <p>${activity.description}</p>
                    <small>${new Date(activity.timestamp).toLocaleString()}</small>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

async function loadGPUStatus() {
    try {
        const response = await fetch('/api/v1/dashboard/gpu-status', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const gpus = await response.json();
            const gpuStatus = document.getElementById('gpuStatus');
            gpuStatus.innerHTML = gpus.map(gpu => `
                <div class="gpu-card">
                    <h4>${gpu.name}</h4>
                    <p>Memory: ${gpu.memory_used}MB / ${gpu.memory_total}MB</p>
                    <div class="gpu-status-bar">
                        <div class="gpu-status-fill" style="width: ${(gpu.memory_used / gpu.memory_total) * 100}%"></div>
                    </div>
                    <p>Status: ${gpu.status}</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading GPU status:', error);
    }
} 