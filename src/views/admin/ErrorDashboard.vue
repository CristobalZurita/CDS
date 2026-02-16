<template>
    <div class="error-dashboard">
        <div class="header">
            <h1>Error Monitoring Dashboard</h1>
            <div class="header-actions">
                <button @click="refreshStats" class="btn-refresh">
                    ⟲ Refresh
                </button>
                <button @click="exportLogs" class="btn-export">
                    ⬇ Export CSV
                </button>
                <button @click="clearLogs" class="btn-clear">
                    🗑 Clear
                </button>
            </div>
        </div>

        <!-- Statistics Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Logs</div>
                <div class="stat-value">{{ stats.totalLogs }}</div>
            </div>
            <div class="stat-card error">
                <div class="stat-label">Errors</div>
                <div class="stat-value">{{ stats.errorCount }}</div>
                <div class="stat-trend" :class="{ up: errorTrend > 0, down: errorTrend < 0 }">
                    {{ errorTrend > 0 ? '↑' : errorTrend < 0 ? '↓' : '→' }} {{ Math.abs(errorTrend) }}
                </div>
            </div>
            <div class="stat-card critical">
                <div class="stat-label">Critical</div>
                <div class="stat-value">{{ stats.criticalCount }}</div>
                <div class="stat-trend" :class="{ up: criticalTrend > 0, down: criticalTrend < 0 }">
                    {{ criticalTrend > 0 ? '↑' : criticalTrend < 0 ? '↓' : '→' }} {{ Math.abs(criticalTrend) }}
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg API Time</div>
                <div class="stat-value">{{ stats.avgDurationMs.toFixed(0) }}ms</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Slow Ops</div>
                <div class="stat-value">{{ stats.slowOperations.length }}</div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filters">
            <div class="filter-group">
                <label>Level:</label>
                <select v-model="selectedLevel">
                    <option value="">All</option>
                    <option value="DEBUG">Debug</option>
                    <option value="INFO">Info</option>
                    <option value="WARN">Warning</option>
                    <option value="ERROR">Error</option>
                    <option value="CRITICAL">Critical</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Limit:</label>
                <input v-model.number="limit" type="number" min="10" max="500" />
            </div>
            <div class="filter-group">
                <label>Search:</label>
                <input v-model="searchQuery" type="text" placeholder="Filter by message..." />
            </div>
        </div>

        <!-- Slow Operations Table -->
        <div v-if="stats.slowOperations.length > 0" class="section">
            <h2>Slow Operations (> 2s)</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Operation</th>
                        <th>Duration</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(op, idx) in stats.slowOperations.slice(0, 10)" :key="idx">
                        <td>{{ op.name }}</td>
                        <td class="metric">{{ op.duration.toFixed(2) }}ms</td>
                        <td class="time">{{ formatTime(op.timestamp) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Logs Table -->
        <div class="section">
            <h2>Recent Logs</h2>
            <div v-if="filteredLogs.length === 0" class="empty-state">
                No logs found
            </div>
            <table v-else class="data-table logs-table">
                <thead>
                    <tr>
                        <th>Level</th>
                        <th>Message</th>
                        <th>Context</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="log in filteredLogs" :key="log.id" :class="log.level.toLowerCase()">
                        <td>
                            <span class="badge" :class="log.level.toLowerCase()">
                                {{ log.level }}
                            </span>
                        </td>
                        <td class="message">{{ log.message }}</td>
                        <td class="context">
                            <code>{{ JSON.stringify(log.context, null, 1) }}</code>
                        </td>
                        <td class="time">{{ formatTime(log.timestamp) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { logger } from '@/services/logging'

const stats = ref({
    totalLogs: 0,
    errorCount: 0,
    criticalCount: 0,
    avgDurationMs: 0,
    slowOperations: []
})

const logs = ref([])
const selectedLevel = ref('')
const limit = ref(50)
const searchQuery = ref('')
const errorTrend = ref(0)
const criticalTrend = ref(0)
let previousErrorCount = 0
let previousCriticalCount = 0
let refreshInterval

const filteredLogs = computed(() => {
    return logs.value.filter(log => {
        const levelMatch = !selectedLevel.value || log.level === selectedLevel.value
        const searchMatch = !searchQuery.value || 
            log.message.toLowerCase().includes(searchQuery.value.toLowerCase())
        return levelMatch && searchMatch
    })
})

async function refreshStats() {
    try {
        const response = await fetch('/api/logs/stats')
        if (response.ok) {
            stats.value = await response.json()
            
            // Calculate trends
            errorTrend.value = stats.value.errorCount - previousErrorCount
            criticalTrend.value = stats.value.criticalCount - previousCriticalCount
            
            previousErrorCount = stats.value.errorCount
            previousCriticalCount = stats.value.criticalCount
        }
    } catch (error) {
        logger.error('Failed to fetch stats', { error: error.message })
    }
}

async function fetchLogs() {
    try {
        const url = new URL('/api/logs', window.location.origin)
        if (selectedLevel.value) {
            url.searchParams.append('level', selectedLevel.value)
        }
        url.searchParams.append('limit', limit.value)

        const response = await fetch(url)
        if (response.ok) {
            logs.value = await response.json()
        }
    } catch (error) {
        logger.error('Failed to fetch logs', { error: error.message })
    }
}

async function exportLogs() {
    try {
        const csv = [
            ['Level', 'Message', 'Context', 'Timestamp'],
            ...logs.value.map(log => [
                log.level,
                log.message,
                JSON.stringify(log.context),
                new Date(log.timestamp).toISOString()
            ])
        ]
        .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        .join('\n')

        const blob = new Blob([csv], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `logs_${Date.now()}.csv`
        a.click()
        URL.revokeObjectURL(url)
    } catch (error) {
        logger.error('Export failed', { error: error.message })
    }
}

async function clearLogs() {
    if (!confirm('Clear all logs? This cannot be undone.')) return
    
    try {
        const response = await fetch('/api/logs', { method: 'DELETE' })
        if (response.ok) {
            logs.value = []
            await refreshStats()
            logger.info('Logs cleared')
        }
    } catch (error) {
        logger.error('Failed to clear logs', { error: error.message })
    }
}

function formatTime(timestamp) {
    const date = new Date(timestamp)
    return date.toLocaleString()
}

onMounted(() => {
    refreshStats()
    fetchLogs()
    
    // Refresh stats every 30 seconds
    refreshInterval = setInterval(() => {
        refreshStats()
        fetchLogs()
    }, 30000)
})

onUnmounted(() => {
    if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style lang="scss" scoped>
.error-dashboard {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;

        h1 {
            margin: 0;
            font-size: 2rem;
            color: #333;
        }

        .header-actions {
            display: flex;
            gap: 0.5rem;

            button {
                padding: 0.6rem 1.2rem;
                border: none;
                border-radius: 4px;
                background: #f0f0f0;
                cursor: pointer;
                font-size: 0.9rem;
                transition: all 0.2s;

                &:hover {
                    background: #e0e0e0;
                }

                &.btn-refresh {
                    background: #2196F3;
                    color: white;
                    &:hover { background: #1976D2; }
                }

                &.btn-export {
                    background: #4CAF50;
                    color: white;
                    &:hover { background: #388E3C; }
                }

                &.btn-clear {
                    background: #f44336;
                    color: white;
                    &:hover { background: #d32f2f; }
                }
            }
        }
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #2196F3;

            &.error {
                border-left-color: #FF9800;
            }

            &.critical {
                border-left-color: #f44336;
            }

            .stat-label {
                font-size: 0.85rem;
                color: #666;
                margin-bottom: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .stat-value {
                font-size: 2rem;
                font-weight: bold;
                color: #333;
            }

            .stat-trend {
                font-size: 0.8rem;
                margin-top: 0.5rem;
                &.up { color: #f44336; }
                &.down { color: #4CAF50; }
            }
        }
    }

    .filters {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);

        .filter-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;

            label {
                font-weight: 600;
                color: #666;
                min-width: 60px;
            }

            select, input {
                padding: 0.5rem;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.9rem;
                min-width: 120px;

                &:focus {
                    outline: none;
                    border-color: #2196F3;
                    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
                }
            }
        }
    }

    .section {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;

        h2 {
            margin: 0 0 1rem 0;
            font-size: 1.3rem;
            color: #333;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 0.5rem;
        }

        .empty-state {
            text-align: center;
            color: #999;
            padding: 2rem;
            font-style: italic;
        }
    }

    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;

        thead {
            background: #f5f5f5;
            border-bottom: 2px solid #ddd;

            th {
                padding: 1rem;
                text-align: left;
                font-weight: 600;
                color: #666;
            }
        }

        tbody {
            tr {
                border-bottom: 1px solid #eee;
                transition: background 0.2s;

                &:hover {
                    background: #fafafa;
                }

                &.error {
                    td:first-child { background: #fff3e0; }
                }

                &.critical {
                    td:first-child { background: #ffebee; }
                }
            }
        }

        td {
            padding: 0.8rem 1rem;

            .badge {
                display: inline-block;
                padding: 0.3rem 0.6rem;
                border-radius: 3px;
                font-weight: 600;
                font-size: 0.8rem;

                &.debug { background: #E3F2FD; color: #1565C0; }
                &.info { background: #E0F2F1; color: #00695C; }
                &.warn { background: #FFF3E0; color: #E65100; }
                &.error { background: #FFEBEE; color: #C62828; }
                &.critical { background: #FCE4EC; color: #AD1457; }
            }

            &.message {
                max-width: 300px;
                word-break: break-word;
                color: #333;
            }

            &.context {
                max-width: 200px;
                overflow: auto;
                background: #f9f9f9;
                padding: 0.5rem;
                border-radius: 3px;
                font-family: monospace;
                font-size: 0.8rem;

                code {
                    color: #666;
                }
            }

            &.metric {
                font-weight: 600;
                color: #2196F3;
            }

            &.time {
                color: #999;
                font-size: 0.85rem;
                white-space: nowrap;
            }
        }
    }

    .logs-table {
        tbody tr {
            &.debug { border-left: 3px solid #64B5F6; }
            &.info { border-left: 3px solid #4DB6AC; }
            &.warn { border-left: 3px solid #FFB74D; }
            &.error { border-left: 3px solid #EF5350; }
            &.critical { border-left: 3px solid #EC407A; }
        }
    }

    @media (max-width: 768px) {
        padding: 1rem;

        .header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;

            h1 {
                font-size: 1.5rem;
            }
        }

        .stats-grid {
            grid-template-columns: 1fr;
        }

        .filters {
            flex-direction: column;
        }

        .data-table {
            font-size: 0.8rem;

            td {
                padding: 0.5rem;
            }

            &.logs-table {
                display: block;
                overflow: auto;
            }
        }
    }
}
</style>
