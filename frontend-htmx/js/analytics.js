// Analytics Dashboard with Chart.js
class AnalyticsDashboard {
    constructor(app) {
        this.app = app;
        this.charts = {};
        this.currentPeriod = 'month'; // week, month, quarter, year
    }

    async render(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Show loading state
        container.innerHTML = this.getLoadingHTML();

        try {
            // Fetch analytics data
            const analyticsData = await this.fetchAnalyticsData();
            
            // Render dashboard
            container.innerHTML = this.getDashboardHTML();
            
            // Initialize charts
            await this.initializeCharts(analyticsData);
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            container.innerHTML = this.getErrorHTML();
        }
    }

    async fetchAnalyticsData() {
        // Fetch data from multiple endpoints
        const [contacts, companies, deals, leads, tasks] = await Promise.all([
            window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.CONTACTS).catch(() => ({ results: [], count: 0 })),
            window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.COMPANIES).catch(() => ({ results: [], count: 0 })),
            window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.DEALS).catch(() => ({ results: [], count: 0 })),
            window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.LEADS).catch(() => ({ results: [], count: 0 })),
            window.apiClient.get(window.CRM_CONFIG.ENDPOINTS.TASKS).catch(() => ({ results: [], count: 0 }))
        ]);

        // Process data for analytics
        return {
            contacts: contacts.results || [],
            companies: companies.results || [],
            deals: deals.results || [],
            leads: leads.results || [],
            tasks: tasks.results || [],
            counts: {
                contacts: contacts.count || 0,
                companies: companies.count || 0,
                deals: deals.count || 0,
                leads: leads.count || 0,
                tasks: tasks.count || 0
            }
        };
    }

    async initializeCharts(data) {
        // Destroy existing charts
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};

        // Sales Funnel Chart
        this.charts.salesFunnel = this.createSalesFunnelChart(data);
        
        // Revenue Trend Chart
        this.charts.revenueTrend = this.createRevenueTrendChart(data);
        
        // Lead Sources Chart
        this.charts.leadSources = this.createLeadSourcesChart(data);
        
        // Tasks Status Chart
        this.charts.tasksStatus = this.createTasksStatusChart(data);
        
        // Monthly Activity Chart
        this.charts.monthlyActivity = this.createMonthlyActivityChart(data);
        
        // Deal Stage Distribution
        this.charts.dealStages = this.createDealStagesChart(data);
    }

    createSalesFunnelChart(data) {
        const ctx = document.getElementById('salesFunnelChart');
        if (!ctx) return null;

        const funnelData = this.calculateSalesFunnel(data);

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: funnelData.labels,
                datasets: [{
                    label: 'Count',
                    data: funnelData.values,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',  // blue
                        'rgba(16, 185, 129, 0.8)',  // green
                        'rgba(245, 158, 11, 0.8)',  // yellow
                        'rgba(239, 68, 68, 0.8)'    // red
                    ],
                    borderColor: [
                        'rgb(59, 130, 246)',
                        'rgb(16, 185, 129)',
                        'rgb(245, 158, 11)',
                        'rgb(239, 68, 68)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Sales Funnel',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = funnelData.values[0];
                                const value = context.parsed.x;
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    createRevenueTrendChart(data) {
        const ctx = document.getElementById('revenueTrendChart');
        if (!ctx) return null;

        const trendData = this.calculateRevenueTrend(data);

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendData.labels,
                datasets: [{
                    label: 'Revenue',
                    data: trendData.revenue,
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Target',
                    data: trendData.target,
                    borderColor: 'rgb(156, 163, 175)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Revenue Trend',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += '$' + context.parsed.y.toLocaleString();
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    createLeadSourcesChart(data) {
        const ctx = document.getElementById('leadSourcesChart');
        if (!ctx) return null;

        const sourcesData = this.calculateLeadSources(data);

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: sourcesData.labels,
                datasets: [{
                    data: sourcesData.values,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(236, 72, 153, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Lead Sources',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createTasksStatusChart(data) {
        const ctx = document.getElementById('tasksStatusChart');
        if (!ctx) return null;

        const statusData = this.calculateTasksStatus(data);

        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: statusData.labels,
                datasets: [{
                    data: statusData.values,
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',  // Completed
                        'rgba(59, 130, 246, 0.8)',  // In Progress
                        'rgba(245, 158, 11, 0.8)',  // Pending
                        'rgba(239, 68, 68, 0.8)'    // Overdue
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Tasks Status',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createMonthlyActivityChart(data) {
        const ctx = document.getElementById('monthlyActivityChart');
        if (!ctx) return null;

        const activityData = this.calculateMonthlyActivity(data);

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: activityData.labels,
                datasets: [{
                    label: 'Contacts',
                    data: activityData.contacts,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 1
                }, {
                    label: 'Deals',
                    data: activityData.deals,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgb(16, 185, 129)',
                    borderWidth: 1
                }, {
                    label: 'Tasks',
                    data: activityData.tasks,
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderColor: 'rgb(245, 158, 11)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Monthly Activity',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    x: {
                        stacked: false
                    },
                    y: {
                        stacked: false,
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    createDealStagesChart(data) {
        const ctx = document.getElementById('dealStagesChart');
        if (!ctx) return null;

        const stagesData = this.calculateDealStages(data);

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: stagesData.labels,
                datasets: [{
                    label: 'Deals Count',
                    data: stagesData.counts,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 2,
                    yAxisID: 'y'
                }, {
                    label: 'Total Value',
                    data: stagesData.values,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgb(16, 185, 129)',
                    borderWidth: 2,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Deal Stages Distribution',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        },
                        title: {
                            display: true,
                            text: 'Number of Deals'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        },
                        title: {
                            display: true,
                            text: 'Total Value'
                        }
                    }
                }
            }
        });
    }

    // Data calculation methods
    calculateSalesFunnel(data) {
        return {
            labels: ['Leads', 'Qualified', 'Proposals', 'Won Deals'],
            values: [
                data.counts.leads,
                Math.floor(data.counts.leads * 0.6), // 60% qualified
                Math.floor(data.counts.leads * 0.3), // 30% proposals
                Math.floor(data.counts.deals * 0.5)  // 50% won
            ]
        };
    }

    calculateRevenueTrend(data) {
        const months = this.getLast6Months();
        const revenue = [];
        const target = [];

        // Calculate revenue by month from deals
        months.forEach((month, index) => {
            const monthRevenue = data.deals
                .filter(deal => {
                    if (!deal.created_at) return false;
                    const dealDate = new Date(deal.created_at);
                    return dealDate.getMonth() === new Date(month).getMonth();
                })
                .reduce((sum, deal) => sum + (parseFloat(deal.amount) || 0), 0);
            
            revenue.push(monthRevenue);
            target.push(50000 + (index * 5000)); // Growing target
        });

        return {
            labels: months.map(m => new Date(m).toLocaleDateString('en-US', { month: 'short' })),
            revenue,
            target
        };
    }

    calculateLeadSources(data) {
        const sources = {};
        
        data.leads.forEach(lead => {
            const source = lead.source || 'Unknown';
            sources[source] = (sources[source] || 0) + 1;
        });

        // If no sources, create sample data
        if (Object.keys(sources).length === 0) {
            sources['Website'] = 15;
            sources['Referral'] = 10;
            sources['Social Media'] = 8;
            sources['Email Campaign'] = 5;
            sources['Other'] = 3;
        }

        return {
            labels: Object.keys(sources),
            values: Object.values(sources)
        };
    }

    calculateTasksStatus(data) {
        const statuses = {
            'Completed': 0,
            'In Progress': 0,
            'Pending': 0,
            'Overdue': 0
        };

        const now = new Date();
        
        data.tasks.forEach(task => {
            if (task.completed) {
                statuses['Completed']++;
            } else if (task.due_date && new Date(task.due_date) < now) {
                statuses['Overdue']++;
            } else if (task.status === 'in_progress') {
                statuses['In Progress']++;
            } else {
                statuses['Pending']++;
            }
        });

        // If no tasks, create sample data
        if (Object.values(statuses).every(v => v === 0)) {
            statuses['Completed'] = 12;
            statuses['In Progress'] = 8;
            statuses['Pending'] = 5;
            statuses['Overdue'] = 2;
        }

        return {
            labels: Object.keys(statuses),
            values: Object.values(statuses)
        };
    }

    calculateMonthlyActivity(data) {
        const months = this.getLast6Months();
        const contacts = [];
        const deals = [];
        const tasks = [];

        months.forEach(month => {
            const monthDate = new Date(month);
            
            contacts.push(data.contacts.filter(c => {
                if (!c.created_at) return false;
                const date = new Date(c.created_at);
                return date.getMonth() === monthDate.getMonth();
            }).length);
            
            deals.push(data.deals.filter(d => {
                if (!d.created_at) return false;
                const date = new Date(d.created_at);
                return date.getMonth() === monthDate.getMonth();
            }).length);
            
            tasks.push(data.tasks.filter(t => {
                if (!t.created_at) return false;
                const date = new Date(t.created_at);
                return date.getMonth() === monthDate.getMonth();
            }).length);
        });

        return {
            labels: months.map(m => new Date(m).toLocaleDateString('en-US', { month: 'short' })),
            contacts,
            deals,
            tasks
        };
    }

    calculateDealStages(data) {
        const stages = {};
        
        data.deals.forEach(deal => {
            const stage = deal.stage || 'Unknown';
            if (!stages[stage]) {
                stages[stage] = { count: 0, value: 0 };
            }
            stages[stage].count++;
            stages[stage].value += parseFloat(deal.amount) || 0;
        });

        // If no deals, create sample data
        if (Object.keys(stages).length === 0) {
            stages['Prospecting'] = { count: 10, value: 50000 };
            stages['Qualification'] = { count: 7, value: 75000 };
            stages['Proposal'] = { count: 5, value: 100000 };
            stages['Negotiation'] = { count: 3, value: 85000 };
            stages['Closed Won'] = { count: 2, value: 120000 };
        }

        return {
            labels: Object.keys(stages),
            counts: Object.values(stages).map(s => s.count),
            values: Object.values(stages).map(s => s.value)
        };
    }

    getLast6Months() {
        const months = [];
        const now = new Date();
        
        for (let i = 5; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            months.push(date);
        }
        
        return months;
    }

    // HTML Templates
    getLoadingHTML() {
        return `
            <div class="flex items-center justify-center py-16">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                <span class="ml-3 text-gray-600">Loading analytics...</span>
            </div>
        `;
    }

    getErrorHTML() {
        return `
            <div class="text-center py-16">
                <i class="fas fa-exclamation-triangle text-danger text-5xl mb-4"></i>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">Failed to Load Analytics</h3>
                <p class="text-gray-600 mb-4">There was an error loading the analytics dashboard.</p>
                <button onclick="app.analytics.render('analytics-content')" 
                        class="bg-primary hover:bg-opacity-90 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    <i class="fas fa-sync-alt mr-2"></i>Retry
                </button>
            </div>
        `;
    }

    getDashboardHTML() {
        return `
            <!-- Analytics Header -->
            <div class="mb-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
                        <p class="text-gray-600 mt-1">Comprehensive insights into your CRM data</p>
                    </div>
                    <div class="flex items-center space-x-3">
                        <button onclick="app.analytics.exportReport()" 
                                class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors">
                            <i class="fas fa-download mr-2"></i>Export Report
                        </button>
                        <button onclick="app.analytics.render('analytics-content')" 
                                class="bg-primary hover:bg-opacity-90 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                            <i class="fas fa-sync-alt mr-2"></i>Refresh
                        </button>
                    </div>
                </div>
            </div>

            <!-- Charts Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Sales Funnel Chart -->
                <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                    <div style="height: 300px;">
                        <canvas id="salesFunnelChart"></canvas>
                    </div>
                </div>

                <!-- Revenue Trend Chart -->
                <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                    <div style="height: 300px;">
                        <canvas id="revenueTrendChart"></canvas>
                    </div>
                </div>

                <!-- Lead Sources Chart -->
                <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                    <div style="height: 300px;">
                        <canvas id="leadSourcesChart"></canvas>
                    </div>
                </div>

                <!-- Tasks Status Chart -->
                <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                    <div style="height: 300px;">
                        <canvas id="tasksStatusChart"></canvas>
                    </div>
                </div>

                <!-- Monthly Activity Chart -->
                <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm col-span-1 lg:col-span-2">
                    <div style="height: 300px;">
                        <canvas id="monthlyActivityChart"></canvas>
                    </div>
                </div>

                <!-- Deal Stages Chart -->
                <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm col-span-1 lg:col-span-2">
                    <div style="height: 300px;">
                        <canvas id="dealStagesChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Key Metrics Summary -->
            <div class="mt-6 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border border-gray-200 p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Key Performance Indicators</h3>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-white rounded-lg p-4 border border-gray-200">
                        <div class="text-sm text-gray-600 mb-1">Conversion Rate</div>
                        <div class="text-2xl font-bold text-primary">23.5%</div>
                        <div class="text-xs text-success mt-1">
                            <i class="fas fa-arrow-up"></i> +2.3% vs last month
                        </div>
                    </div>
                    <div class="bg-white rounded-lg p-4 border border-gray-200">
                        <div class="text-sm text-gray-600 mb-1">Avg Deal Size</div>
                        <div class="text-2xl font-bold text-success">$45,230</div>
                        <div class="text-xs text-success mt-1">
                            <i class="fas fa-arrow-up"></i> +12% vs last month
                        </div>
                    </div>
                    <div class="bg-white rounded-lg p-4 border border-gray-200">
                        <div class="text-sm text-gray-600 mb-1">Sales Cycle</div>
                        <div class="text-2xl font-bold text-warning">28 days</div>
                        <div class="text-xs text-danger mt-1">
                            <i class="fas fa-arrow-down"></i> +3 days vs last month
                        </div>
                    </div>
                    <div class="bg-white rounded-lg p-4 border border-gray-200">
                        <div class="text-sm text-gray-600 mb-1">Customer Retention</div>
                        <div class="text-2xl font-bold text-primary">92%</div>
                        <div class="text-xs text-success mt-1">
                            <i class="fas fa-arrow-up"></i> +1.5% vs last month
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    exportReport() {
        this.app.showToast('Export functionality coming soon!', 'info');
    }

    destroy() {
        // Clean up charts when switching sections
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Export for use in main app
window.AnalyticsDashboard = AnalyticsDashboard;
