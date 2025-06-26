// LocalMind Collective - Oxford AI Summit 2025 Demo
// Real-time multi-agent research demonstration

class LocalMindDemo {
    constructor() {
        this.ws = null;
        this.isProcessing = false;
        this.currentQuery = null;
        this.startTime = null;
        this.agentStates = {
            principal: 'idle',
            domain: 'idle',
            web: 'idle',
            fact: 'idle',
            quality: 'idle'
        };
        this.agentDialogue = {}; // Store streaming agent responses
        
        this.init();
    }
    
    async init() {
        // Load system info
        await this.loadSystemInfo();
        
        // Load models
        await this.loadModels();
        
        // Load scenarios
        await this.loadScenarios();
        
        // Setup WebSocket
        this.setupWebSocket();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Update system info periodically
        setInterval(() => this.loadSystemInfo(), 30000);
    }
    
    async loadSystemInfo() {
        try {
            const response = await fetch('/api/system');
            const data = await response.json();
            
            document.getElementById('platform').textContent = data.platform;
            document.getElementById('gpu').textContent = data.gpu;
            document.getElementById('vram').textContent = `${data.vram.used_gb}/${data.vram.total_gb}GB (${data.vram.percent}%)`;
            document.getElementById('webSearch').textContent = data.brave_api;
            
            // CPU Temperature
            const cpuTempEl = document.getElementById('cpuTemp');
            if (data.cpu_temp !== null && data.cpu_temp !== undefined) {
                cpuTempEl.textContent = `${data.cpu_temp}°C`;
                cpuTempEl.style.color = data.cpu_temp > 80 ? 'var(--accent-orange)' : 'var(--accent-green)';
            } else {
                cpuTempEl.textContent = 'N/A';
                cpuTempEl.style.color = 'var(--text-secondary)';
            }
            
            // Fan Speed
            const fanSpeedEl = document.getElementById('fanSpeed');
            if (data.fans) {
                const fanList = Object.entries(data.fans).map(([name, rpm]) => `${rpm} RPM`).join(', ');
                fanSpeedEl.textContent = fanList;
                fanSpeedEl.style.color = 'var(--accent-green)';
            } else {
                fanSpeedEl.textContent = 'N/A';
                fanSpeedEl.style.color = 'var(--text-secondary)';
            }
        } catch (error) {
            console.error('Failed to load system info:', error);
        }
    }
    
    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const models = await response.json();
            
            const modelList = document.getElementById('modelList');
            modelList.innerHTML = models.map(model => `
                <div class="model-item ${!model.available ? 'model-unavailable' : ''}">
                    <span class="model-name">${model.id}</span>
                    <span class="model-size">${model.size} • ${model.context}</span>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    }
    
    async loadScenarios() {
        try {
            const response = await fetch('/api/scenarios');
            const scenarios = await response.json();
            
            const scenariosContainer = document.getElementById('scenarios');
            scenariosContainer.innerHTML = scenarios.map(scenario => `
                <div class="scenario-card" data-id="${scenario.id}" data-query="${scenario.query}" data-mode="${scenario.mode}">
                    <div class="scenario-title">${scenario.title}</div>
                    <div class="scenario-description">${scenario.description}</div>
                    <div class="scenario-meta">
                        <span>⏱️ ${scenario.expected_time}</span>
                        <span>🤖 ${scenario.agents.length} agents</span>
                    </div>
                </div>
            `).join('');
            
            // Add click handlers
            document.querySelectorAll('.scenario-card').forEach(card => {
                card.addEventListener('click', () => this.runScenario(card));
            });
        } catch (error) {
            console.error('Failed to load scenarios:', error);
        }
    }
    
    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.sendPing();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            setTimeout(() => this.setupWebSocket(), 5000);
        };
    }
    
    sendPing() {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'ping' }));
            setTimeout(() => this.sendPing(), 30000);
        }
    }
    
    setupEventListeners() {
        // Custom query button
        document.getElementById('runCustom').addEventListener('click', () => {
            const query = document.getElementById('customQuery').value.trim();
            const mode = document.getElementById('queryMode').value;
            
            if (query) {
                this.runResearch(query, mode);
            }
        });
        
        // Enter key in custom query
        document.getElementById('customQuery').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                document.getElementById('runCustom').click();
            }
        });
    }
    
    runScenario(card) {
        if (this.isProcessing) return;
        
        // Highlight active scenario
        document.querySelectorAll('.scenario-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        
        const query = card.dataset.query;
        const mode = card.dataset.mode;
        
        this.runResearch(query, mode);
    }
    
    runResearch(query, mode) {
        if (this.isProcessing || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        this.isProcessing = true;
        this.currentQuery = query;
        this.startTime = Date.now();
        
        // Update UI
        document.getElementById('runCustom').disabled = true;
        document.getElementById('runCustom').textContent = 'Processing...';
        
        // Clear previous results
        this.clearResults();
        
        // Reset agent states
        this.resetAgentStates();
        
        // Show metrics panel
        document.getElementById('performanceMetrics').style.display = 'block';
        
        // Send research request
        this.ws.send(JSON.stringify({
            type: 'research',
            query: query,
            mode: mode
        }));
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'init':
                this.addTimelineEvent('Starting research...', 'phase-analysis');
                break;
                
            case 'phase':
                this.handlePhaseUpdate(data);
                break;
                
            case 'agent_thinking':
                this.updateAgentState(data.agent, 'thinking');
                this.addTimelineEvent(`${data.agent} processing with ${data.model}`, 'agent-thinking');
                this.initializeAgentDialogue(data.agent);
                break;
                
            case 'agent_stream':
                this.handleAgentStream(data);
                break;
                
            case 'agent_response':
                this.updateAgentState(data.agent, 'active');
                if (data.complete) {
                    this.addTimelineEvent(`${data.agent} completed (${data.tokens} tokens)`, 'agent-response');
                }
                break;
                
            case 'agent_error':
                this.updateAgentState(data.agent, 'idle');
                this.addTimelineEvent(`${data.agent} error: ${data.error}`, 'agent-error');
                this.appendAgentDialogue(data.agent, `\n\n⚠️ Error: ${data.error}`);
                break;
                
            case 'web_search':
                this.updateAgentState('Web Harvester', 'thinking');
                this.addTimelineEvent('Performing live web search...', 'web-search');
                break;
                
            case 'web_results':
                this.addTimelineEvent(`Found ${data.count} web results`, 'web-results');
                break;
                
            case 'complete':
                this.handleComplete(data.result);
                break;
                
            case 'error':
                this.handleError(data.message);
                break;
                
            case 'pong':
                // Heartbeat response
                break;
        }
    }
    
    handlePhaseUpdate(data) {
        const phaseNames = {
            analysis: 'Query Analysis',
            research: 'Research Phase',
            validation: 'Fact Validation',
            synthesis: 'Synthesis Phase',
            quality: 'Quality Audit'
        };
        
        const phaseName = phaseNames[data.phase] || data.phase;
        
        if (data.agent) {
            this.updateAgentState(data.agent, 'active');
            this.addTimelineEvent(`${phaseName}: ${data.agent}`, `phase-${data.phase}`);
        } else if (data.agents) {
            this.addTimelineEvent(`${phaseName}: ${data.agents.join(', ')}`, `phase-${data.phase}`);
            data.agents.forEach(agent => this.updateAgentState(agent, 'pending'));
        }
    }
    
    updateAgentState(agentName, state) {
        const agentMap = {
            'Principal Synthesizer': 'principal',
            'Domain Specialist': 'domain',
            'Web Harvester': 'web',
            'Fact Validator': 'fact',
            'Quality Auditor': 'quality'
        };
        
        const agentId = agentMap[agentName] || agentName.toLowerCase();
        this.agentStates[agentId] = state;
        
        const card = document.querySelector(`[data-agent="${agentId}"]`);
        if (card) {
            card.classList.remove('active', 'thinking');
            if (state === 'active') card.classList.add('active');
            if (state === 'thinking') card.classList.add('thinking');
            
            const statusEl = card.querySelector('.agent-status');
            if (statusEl) {
                const statusText = {
                    idle: 'Idle',
                    pending: 'Pending',
                    thinking: 'Processing...',
                    active: 'Active'
                };
                statusEl.textContent = statusText[state] || state;
            }
        }
    }
    
    addTimelineEvent(content, className = '') {
        const container = document.getElementById('timelineContainer');
        const elapsed = this.startTime ? ((Date.now() - this.startTime) / 1000).toFixed(1) : '0.0';
        
        const event = document.createElement('div');
        event.className = `timeline-event ${className}`;
        event.innerHTML = `
            <span class="timeline-time">${elapsed}s</span>
            <span class="timeline-content">${content}</span>
        `;
        
        container.appendChild(event);
        container.scrollTop = container.scrollHeight;
    }
    
    handleComplete(result) {
        this.isProcessing = false;
        
        // Reset button
        document.getElementById('runCustom').disabled = false;
        document.getElementById('runCustom').textContent = 'Run Research';
        
        // Reset agent states
        this.resetAgentStates();
        
        // Display results
        this.displayResults(result);
        
        // Update metrics
        this.updateMetrics(result);
        
        // Add completion event
        this.addTimelineEvent('Research completed successfully', 'phase-complete');
    }
    
    handleError(message) {
        this.isProcessing = false;
        
        // Reset button
        document.getElementById('runCustom').disabled = false;
        document.getElementById('runCustom').textContent = 'Run Research';
        
        // Reset agent states
        this.resetAgentStates();
        
        // Show error
        const resultsContent = document.getElementById('resultsContent');
        resultsContent.innerHTML = `
            <div style="color: var(--accent-red); text-align: center; padding: 40px;">
                <h4>Error occurred during research</h4>
                <p>${message}</p>
            </div>
        `;
        
        this.addTimelineEvent(`Error: ${message}`, 'phase-error');
    }
    
    displayResults(result) {
        const resultsContent = document.getElementById('resultsContent');
        
        // Format the report with proper markdown parsing
        let formattedReport = this.parseMarkdown(result.report);
        
        resultsContent.innerHTML = `
            <div class="query-display">
                <h4>Query</h4>
                <p>${result.query}</p>
            </div>
            
            <div class="agents-used">
                <h4>Agents Deployed</h4>
                <p>${result.agents_used.join(' → ')}</p>
            </div>
            
            <div class="report-content">
                <h4>Research Report</h4>
                ${formattedReport}
            </div>
            
            ${result.web_search_used ? '<p style="font-size: 12px; color: var(--accent-green); margin-top: 20px;">✓ Live web search data included</p>' : ''}
        `;
    }
    
    parseMarkdown(text) {
        // Enhanced markdown parser for clean report display
        let html = text;
        
        // Headers
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
        
        // Bold and italic
        html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.+?)_/g, '<em>$1</em>');
        
        // Lists
        html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
        
        // Wrap consecutive list items
        html = html.replace(/(<li>.*<\/li>\n)+/g, (match) => {
            const isOrdered = match.includes('1.');
            return isOrdered ? `<ol>${match}</ol>` : `<ul>${match}</ul>`;
        });
        
        // Code blocks
        html = html.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Blockquotes
        html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
        
        // Paragraphs
        html = html.split('\n\n').map(paragraph => {
            paragraph = paragraph.trim();
            if (paragraph && !paragraph.startsWith('<')) {
                return `<p>${paragraph}</p>`;
            }
            return paragraph;
        }).join('\n');
        
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        // Clean up
        html = html.replace(/<br><h/g, '<h');
        html = html.replace(/<br><ul>/g, '<ul>');
        html = html.replace(/<br><ol>/g, '<ol>');
        html = html.replace(/<\/ul><br>/g, '</ul>');
        html = html.replace(/<\/ol><br>/g, '</ol>');
        
        return html;
    }
    
    updateMetrics(result) {
        const metrics = result.metrics || {};
        
        document.getElementById('totalTime').textContent = `${metrics.total_time || '-'}s`;
        document.getElementById('agentsUsed').textContent = metrics.agent_count || '-';
        
        if (metrics.vram_peak) {
            const vramDelta = (metrics.vram_peak.used_gb - metrics.vram_baseline.used_gb).toFixed(1);
            document.getElementById('vramPeak').textContent = `+${vramDelta}GB`;
        } else {
            document.getElementById('vramPeak').textContent = '-';
        }
        
        if (result.quality_score) {
            document.getElementById('qualityScore').textContent = `${result.quality_score.overall}/10`;
        } else {
            document.getElementById('qualityScore').textContent = '-';
        }
    }
    
    clearResults() {
        document.getElementById('resultsContent').innerHTML = `
            <div class="placeholder">
                <div class="loading"></div>
                <p style="margin-top: 20px;">Orchestrating AI agents...</p>
            </div>
        `;
        
        document.getElementById('timelineContainer').innerHTML = '';
        
        // Clear agent dialogue
        this.agentDialogue = {};
        this.updateAgentDialogueDisplay();
        
        // Show agent dialogue section
        const dialogueSection = document.getElementById('agentDialogue');
        if (dialogueSection) {
            dialogueSection.style.display = 'block';
        }
        
        // Reset metrics
        document.getElementById('totalTime').textContent = '-';
        document.getElementById('agentsUsed').textContent = '-';
        document.getElementById('vramPeak').textContent = '-';
        document.getElementById('qualityScore').textContent = '-';
    }
    
    resetAgentStates() {
        Object.keys(this.agentStates).forEach(agent => {
            this.agentStates[agent] = 'idle';
            this.updateAgentState(agent, 'idle');
        });
    }
    
    initializeAgentDialogue(agentName) {
        if (!this.agentDialogue[agentName]) {
            this.agentDialogue[agentName] = '';
            this.updateAgentDialogueDisplay();
        }
    }
    
    handleAgentStream(data) {
        const { agent, chunk } = data;
        if (!this.agentDialogue[agent]) {
            this.agentDialogue[agent] = '';
        }
        this.agentDialogue[agent] += chunk;
        this.updateAgentDialogueDisplay();
    }
    
    appendAgentDialogue(agentName, text) {
        if (!this.agentDialogue[agentName]) {
            this.agentDialogue[agentName] = '';
        }
        this.agentDialogue[agentName] += text;
        this.updateAgentDialogueDisplay();
    }
    
    updateAgentDialogueDisplay() {
        // Check if agent dialogue section exists, if not create it
        let dialogueSection = document.getElementById('agentDialogue');
        if (!dialogueSection) {
            const container = document.querySelector('.results-panel');
            const monitorSection = document.getElementById('agentMonitor');
            
            dialogueSection = document.createElement('div');
            dialogueSection.className = 'agent-dialogue';
            dialogueSection.id = 'agentDialogue';
            dialogueSection.innerHTML = '<h3>Agent Dialogue</h3><div class="dialogue-container" id="dialogueContainer"></div>';
            
            // Insert after agent monitor
            monitorSection.parentNode.insertBefore(dialogueSection, monitorSection.nextSibling);
        }
        
        const dialogueContainer = document.getElementById('dialogueContainer');
        const agents = Object.keys(this.agentDialogue).filter(agent => this.agentDialogue[agent]);
        
        if (agents.length === 0) {
            dialogueContainer.innerHTML = '<p class="dialogue-placeholder">Agent responses will appear here...</p>';
            return;
        }
        
        dialogueContainer.innerHTML = agents.map(agent => `
            <div class="agent-dialogue-item">
                <div class="agent-dialogue-header">
                    <span class="agent-icon">${this.getAgentIcon(agent)}</span>
                    <span class="agent-name">${agent}</span>
                </div>
                <div class="agent-dialogue-content">
                    ${this.formatAgentResponse(this.agentDialogue[agent])}
                </div>
            </div>
        `).join('');
        
        // Auto-scroll to latest content
        dialogueContainer.scrollTop = dialogueContainer.scrollHeight;
    }
    
    getAgentIcon(agentName) {
        const icons = {
            'Principal Synthesizer': '🧠',
            'Domain Specialist': '🎓',
            'Web Harvester': '🌐',
            'Fact Validator': '✓',
            'Quality Auditor': '⭐'
        };
        return icons[agentName] || '🤖';
    }
    
    formatAgentResponse(text) {
        // Convert markdown-like formatting to HTML
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
            .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>')
            .replace(/^### (.+)$/gm, '<h4>$1</h4>')
            .replace(/^## (.+)$/gm, '<h3>$1</h3>')
            .replace(/^# (.+)$/gm, '<h2>$1</h2>')
            .replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>');
    }
}

// Initialize demo when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.localMindDemo = new LocalMindDemo();
});