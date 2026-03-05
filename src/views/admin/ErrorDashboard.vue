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
    import { buildLoggingRequestHeaders, logger } from '@/services/logging'

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
        const response = await fetch('/api/logs/stats', {
            headers: buildLoggingRequestHeaders(false)
        })
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

        const response = await fetch(url, {
            headers: buildLoggingRequestHeaders(false)
        })
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
        const response = await fetch('/api/logs', {
            method: 'DELETE',
            headers: buildLoggingRequestHeaders(false)
        })
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
