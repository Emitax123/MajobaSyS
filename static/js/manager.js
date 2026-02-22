// JavaScript específico para la app Manager
document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar dashboard del manager
    initializeManagerDashboard();
    
    // Funciones específicas del manager
    function initializeManagerDashboard() {
        // Actualizar barras de progreso
        updateProgressBars();
        
        // Inicializar gráficos si existe Chart.js
        if (typeof Chart !== 'undefined') {
            initializeCharts();
        }
        
        // Auto-refresh de notificaciones cada 5 minutos
        setInterval(refreshNotifications, 300000);
    }
    
    function updateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            const percentage = bar.dataset.percentage || 0;
            bar.style.width = percentage + '%';
        });
    }
    
    function refreshNotifications() {
        MajobaSyS.ajax('/manager/api/notifications/')
            .then(data => {
                updateNotificationCount(data.count);
            })
            .catch(error => {
                console.log('Error al actualizar notificaciones:', error);
            });
    }
    
    function updateNotificationCount(count) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }
    
    // Función para agregar puntos
    window.addPoints = function(amount, description = 'Puntos agregados') {
        MajobaSyS.ajax('/manager/api/add-points/', {
            method: 'POST',
            body: JSON.stringify({
                amount: amount,
                description: description
            })
        })
        .then(data => {
            if (data.success) {
                MajobaSyS.showNotification(`+${amount} puntos agregados`, 'success');
                updatePointsDisplay(data.new_total);
                updateLevelDisplay(data.new_level);
            }
        });
    };
    
    // Función para actualizar nivel
    function updateLevelDisplay(level) {
        const levelBadge = document.querySelector('.account-level');
        if (levelBadge) {
            levelBadge.className = `account-level level-${level}`;
            levelBadge.textContent = level.charAt(0).toUpperCase() + level.slice(1);
        }
    }
    
    // Inicializar gráficos
    function initializeCharts() {
        // Gráfico de puntos por mes
        const pointsChart = document.getElementById('pointsChart');
        if (pointsChart) {
            new Chart(pointsChart, {
                type: 'line',
                data: {
                    labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
                    datasets: [{
                        label: 'Puntos Ganados',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: 'rgb(37, 99, 235)',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Evolución de Puntos'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Gráfico de distribución de niveles
        const levelChart = document.getElementById('levelChart');
        if (levelChart) {
            new Chart(levelChart, {
                type: 'doughnut',
                data: {
                    labels: ['Bronce', 'Plata', 'Oro', 'Platino', 'Diamante'],
                    datasets: [{
                        data: [30, 25, 20, 15, 10],
                        backgroundColor: [
                            '#cd7f32',
                            '#c0c0c0',
                            '#ffd700',
                            '#e5e4e2',
                            '#b9f2ff'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Distribución de Niveles'
                        }
                    }
                }
            });
        }
    }
    
    // Funciones para gestión de premios
    window.togglePrizeAvailability = function(prizeId) {
        MajobaSyS.ajax(`/manager/api/prizes/${prizeId}/toggle/`, {
            method: 'POST'
        })
        .then(data => {
            if (data.success) {
                const statusBadge = document.querySelector(`[data-prize-id="${prizeId}"] .prize-status`);
                if (statusBadge) {
                    statusBadge.textContent = data.is_active ? 'Disponible' : 'No disponible';
                    statusBadge.className = `prize-status ${data.is_active ? 'status-available' : 'status-insufficient'}`;
                }
                MajobaSyS.showNotification('Estado del premio actualizado', 'success');
            }
        });
    };
    
    // Función para filtrar premios
    window.filterPrizes = function(category) {
        const prizes = document.querySelectorAll('.prize-card');
        prizes.forEach(prize => {
            if (category === 'all' || prize.dataset.category === category) {
                prize.style.display = 'block';
            } else {
                prize.style.display = 'none';
            }
        });
        
        // Actualizar botones de filtro
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${category}"]`).classList.add('active');
    };
    
    // Búsqueda en tiempo real
    const searchInput = document.getElementById('prizeSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const prizes = document.querySelectorAll('.prize-card');
            
            prizes.forEach(prize => {
                const title = prize.querySelector('.prize-title').textContent.toLowerCase();
                const description = prize.querySelector('.prize-description').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    prize.style.display = 'block';
                } else {
                    prize.style.display = 'none';
                }
            });
        });
    }
    
    // Cargar más actividades
    window.loadMoreActivities = function() {
        const button = document.getElementById('loadMoreBtn');
        const currentPage = parseInt(button.dataset.page) || 1;
        
        button.textContent = 'Cargando...';
        button.disabled = true;
        
        MajobaSyS.ajax(`/manager/api/activities/?page=${currentPage + 1}`)
            .then(data => {
                if (data.activities && data.activities.length > 0) {
                    const activityList = document.querySelector('.activity-list');
                    data.activities.forEach(activity => {
                        const activityHTML = createActivityHTML(activity);
                        activityList.insertAdjacentHTML('beforeend', activityHTML);
                    });
                    
                    button.dataset.page = currentPage + 1;
                    button.textContent = 'Cargar más';
                    button.disabled = false;
                    
                    if (!data.has_next) {
                        button.style.display = 'none';
                    }
                } else {
                    button.style.display = 'none';
                }
            })
            .catch(error => {
                button.textContent = 'Error al cargar';
                button.disabled = false;
            });
    };
    
    function createActivityHTML(activity) {
        return `
            <div class="activity-item">
                <div class="activity-icon ${activity.type}">
                    ${activity.type === 'points-gained' ? '+' : '-'}
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                </div>
                <div class="activity-time">
                    ${MajobaSyS.formatDate(activity.created_at)}
                </div>
            </div>
        `;
    }
    
    // Inicializar tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
    
    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = e.target.dataset.tooltip;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            pointer-events: none;
            z-index: 1000;
        `;
        document.body.appendChild(tooltip);
        
        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        e.target.tooltip = tooltip;
    }
    
    function hideTooltip(e) {
        if (e.target.tooltip) {
            e.target.tooltip.remove();
            delete e.target.tooltip;
        }
    }
});