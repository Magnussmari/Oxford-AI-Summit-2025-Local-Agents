// LocalMind Collective - Modern Dashboard JavaScript

class LocalMindDashboard {
    constructor() {
        this.ws = null;
        this.currentMode = 'auto';
        this.isProcessing = false;
        this.startTime = null;
        this.performanceChart = null;
        this.availableModels = [];
        
        // Agent output tracking
        this.agentOutputs = {};
        this.agentWebsites = {}; // Store website info per agent
        
        // Performance tracking
        this.totalTokens = 0;
        this.agentTokens = {}; // Track tokens per agent
        this.activeAgents = 0;
        this.currentVRAM = 0;
        this.elapsedTimer = null;
        
        // Initialize markdown renderer
        this.initializeMarkdown();
        
        this.initializeElements();
        this.initializeWebSocket();
        this.initializeEventListeners();
        // this.initializeChart(); // Removed performance chart
        this.loadAvailableModels();
        this.updateSystemInfo();
        this.loadDemoScenarios();
    }
    
    initializeMarkdown() {
        // Configure marked.js for better markdown rendering
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {}
                    }
                    return code;
                },
                langPrefix: 'hljs language-',
                breaks: true,
                gfm: true
            });
        }
    }
    
    initializeElements() {
        // Input elements
        this.researchInput = document.getElementById('researchInput');
        this.modeButtons = document.querySelectorAll('.mode-btn');
        this.actionButtons = document.querySelectorAll('.action-btn');
        
        // Display elements
        this.agentGrid = document.getElementById('agentGrid');
        this.resultsContent = document.getElementById('resultsContent');
        this.timeline = document.getElementById('timeline');
        this.elapsedTimeTimeline = document.getElementById('elapsedTimeTimeline'); // Timeline panel time
        
        // Metrics elements (removed from UI)
        // this.totalTime = document.getElementById('totalTime');
        // this.tokensGenerated = document.getElementById('tokensGenerated');
        // this.agentsUsed = document.getElementById('agentsUsed');
        // this.successRate = document.getElementById('successRate');
        
        // System info
        this.gpuInfo = document.getElementById('gpuInfo');
        this.webSearchStatus = document.getElementById('webSearchStatus');
        this.enhancedModeStatus = document.getElementById('enhancedModeStatus');
        this.activeAgentCount = document.getElementById('activeAgentCount');
        
        // Header stats (these are in the header)
        this.totalTokensDisplay = document.getElementById('totalTokens');
        this.elapsedTimeDisplay = document.getElementById('elapsedTime'); // This is the header one
        this.activeAgentCountHeader = document.getElementById('activeAgentCountHeader');
        
        // Initialize agents
        this.initializeAgents();
    }
    
    initializeAgents() {
        const researchAgents = [
            { id: 'principal', name: 'Principal Synthesizer', icon: '🧠', model: 'deepseek-r1:8b' },
            { id: 'domain', name: 'Domain Specialist', icon: '🎓', model: 'qwen3:8b' },
            { id: 'web', name: 'Web Harvester', icon: '🌐', model: 'qwen3:4b' },
            { id: 'fact', name: 'Fact Validator', icon: '✅', model: 'phi4-mini' },
            { id: 'quality', name: 'Quality Auditor', icon: '⭐', model: 'phi4-mini' }
        ];
        
        // Display research agents
        this.displayAgents(researchAgents);
    }
    
    displayAgents(agents) {
        this.agentGrid.innerHTML = agents.map(agent => `
            <div class="agent-card" data-agent="${agent.id}">
                <div class="agent-icon">${agent.icon}</div>
                <div class="agent-name">${agent.name}</div>
                <div class="agent-status">Idle</div>
            </div>
        `).join('');
    }
    
    initializeWebSocket() {
        const wsUrl = `ws://${window.location.host}/ws`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            // Attempt to reconnect after 2 seconds
            setTimeout(() => this.initializeWebSocket(), 2000);
        };
    }
    
    initializeEventListeners() {
        // Research input
        this.researchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.startResearch();
            }
        });
        
        // Mode buttons
        this.modeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentMode = btn.dataset.mode;
                this.modeButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        
        // Quick action buttons
        this.actionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.researchInput.value = btn.dataset.prompt;
                this.startResearch();
            });
        });
        
        // Voice input button
        document.querySelector('.voice-btn')?.addEventListener('click', () => {
            this.startVoiceInput();
        });
        
        // Panel action buttons
        document.querySelectorAll('.action-icon').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.getAttribute('title').toLowerCase();
                this.handlePanelAction(action);
            });
        });
    }
    
    initializeChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Token Generation Rate',
                    data: [],
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
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
                    x: {
                        display: false
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            font: {
                                size: 10
                            }
                        }
                    }
                }
            }
        });
    }
    
    startResearch() {
        const query = this.researchInput.value.trim();
        if (!query || this.isProcessing) return;
        
        this.isProcessing = true;
        this.startTime = Date.now();
        this.clearResults();
        
        // Reset agent display
        this.initializeAgents();
        
        // Start elapsed time counter
        this.startElapsedTimer();
        
        // Send research request
        this.ws.send(JSON.stringify({
            type: 'research',
            query: query,
            mode: this.currentMode
        }));
        
        // Add to timeline
        this.addTimelineEvent('Research started', 'info');
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'init':
                this.addTimelineEvent('Initializing research system', 'info');
                break;
                
            case 'phase':
                // Handle phase messages from backend
                if (data.agent) {
                    this.updateAgentStatus(data.agent, 'thinking', `${data.phase} phase`);
                    this.addTimelineEvent(`${data.agent} - ${data.phase} phase started`, 'agent');
                    this.updateActiveAgentCount();
                }
                break;
                
            case 'agent_start':
                this.updateAgentStatus(data.agent, 'thinking', data.message);
                this.addTimelineEvent(`${data.agent} started`, 'agent');
                this.updateActiveAgentCount();
                break;
                
            case 'performance':
                if (data.vram) {
                    this.currentVRAM = data.vram.used_gb || 0;
                }
                break;
                
            case 'agent_stream':
                this.appendAgentOutput(data.agent, data.chunk || data.content || '');
                if (data.tokens && data.agent) {
                    this.updateTokenCount(data.agent, data.tokens);
                }
                break;
                
            case 'agent_complete':
                this.updateAgentStatus(data.agent, 'complete', 'Completed');
                this.addTimelineEvent(`${data.agent} completed`, 'success');
                this.updateActiveAgentCount();
                
                // Append any stored website info for this agent
                if (this.agentWebsites && this.agentWebsites[data.agent]) {
                    this.appendAgentOutput(data.agent, this.agentWebsites[data.agent]);
                    delete this.agentWebsites[data.agent];
                }
                break;
                
            case 'agent_response':
                // Handle completion from agent_response type
                if (data.agent && data.complete) {
                    this.updateAgentStatus(data.agent, 'complete', 'Completed');
                    this.updateActiveAgentCount();
                    // Update final token count for this agent
                    if (data.tokens) {
                        this.updateTokenCount(data.agent, data.tokens);
                    }
                }
                break;
                
            case 'web_results':
                // Handle web search results
                if (data.websites && data.websites.length > 0) {
                    this.addTimelineEvent(
                        `Web Harvester explored ${data.websites.length} websites`,
                        'agent'
                    );
                    // Add websites info to a special section
                    const websiteList = data.websites.map(w => 
                        `• [${w.title}](${w.url})`
                    ).join('\n');
                    
                    const websiteInfo = `\n\n📌 **Websites Explored:**\n${websiteList}\n`;
                    
                    // Store this info to append after agent completes
                    if (!this.agentWebsites) this.agentWebsites = {};
                    this.agentWebsites[data.agent] = websiteInfo;
                }
                break;
                
            case 'complete':
                this.handleResearchComplete(data.result);
                break;
                
            case 'error':
                this.handleError(data.message);
                break;
                
            case 'performance':
                this.updatePerformanceMetrics(data.data);
                break;
        }
    }
    
    updateAgentStatus(agentName, status, message = '') {
        // Map full agent names to their IDs
        const agentNameMap = {
            'Principal Synthesizer': 'principal',
            'Domain Specialist': 'domain',
            'Web Harvester': 'web',
            'Fact Validator': 'fact',
            'Quality Auditor': 'quality'
        };
        
        // Try to find agent by ID or by mapped name
        const agentId = agentNameMap[agentName] || agentName;
        const agentCard = this.agentGrid.querySelector(`[data-agent="${agentId}"]`);
        if (!agentCard) return;
        
        agentCard.classList.remove('active', 'thinking', 'complete');
        if (status === 'thinking') {
            agentCard.classList.add('thinking');
            agentCard.querySelector('.agent-status').textContent = 'Processing...';
        } else if (status === 'complete') {
            agentCard.classList.add('complete');
            agentCard.querySelector('.agent-status').textContent = 'Complete';
        } else {
            agentCard.querySelector('.agent-status').textContent = 'Idle';
        }
    }
    
    appendAgentOutput(agent, content) {
        // Initialize agent output if not exists
        if (!this.agentOutputs[agent]) {
            this.agentOutputs[agent] = '';
            
            // Clear empty state or loading state if present ONLY once
            const currentContent = this.resultsContent.innerHTML;
            if (currentContent.includes('empty-state') || currentContent.includes('loading-state')) {
                this.resultsContent.innerHTML = '';
            }
        }
        
        // Check if agent section already exists
        const agentId = `agent-output-${agent.replace(/\s+/g, '-')}`;
        let agentSection = document.getElementById(agentId);
        
        if (!agentSection) {
            // Create initial section for this agent only if it doesn't exist
            agentSection = document.createElement('div');
            agentSection.className = 'agent-output';
            agentSection.id = agentId;
            agentSection.innerHTML = `
                <h3 style="color: var(--primary-blue); margin-bottom: var(--space-2);">${agent}</h3>
                <div class="agent-content"></div>
            `;
            this.resultsContent.appendChild(agentSection);
        }
        
        // Append content to existing agent output
        this.agentOutputs[agent] += content;
        
        // Update the agent's content section with smooth transition
        const contentDiv = agentSection.querySelector('.agent-content');
        if (contentDiv) {
            // Use requestAnimationFrame to prevent flashing
            requestAnimationFrame(() => {
                contentDiv.innerHTML = this.formatContent(this.agentOutputs[agent]);
            });
        }
    }
    
    formatContent(content) {
        // Handle undefined or null content
        if (!content) return '';
        
        // Use marked.js for proper markdown rendering if available
        if (typeof marked !== 'undefined') {
            try {
                const html = marked.parse(content);
                // Apply syntax highlighting if available
                if (typeof hljs !== 'undefined') {
                    setTimeout(() => {
                        document.querySelectorAll('pre code').forEach((block) => {
                            if (!block.classList.contains('hljs')) {
                                hljs.highlightElement(block);
                            }
                        });
                    }, 100);
                }
                return html;
            } catch (error) {
                console.warn('Markdown parsing error:', error);
                // Fallback to simple formatting
            }
        }
        
        // Fallback: Simple markdown-like formatting
        return content
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/#{3}\s*(.*)/g, '<h3>$1</h3>')
            .replace(/#{2}\s*(.*)/g, '<h2>$1</h2>')
            .replace(/#{1}\s*(.*)/g, '<h1>$1</h1>')
            .replace(/^\s*[-*+]\s+(.*)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
            .replace(/\n/g, '<br>');
    }
    
    handleResearchComplete(result) {
        this.isProcessing = false;
        this.stopElapsedTimer();
        
        // Reset agent outputs for next query
        this.agentOutputs = {};
        this.agentTokens = {};
        
        // Don't replace agent outputs - append final synthesis if provided
        if (result.synthesis) {
            const finalSection = document.createElement('div');
            finalSection.className = 'final-result';
            finalSection.style.cssText = 'margin-top: var(--space-6); padding-top: var(--space-4); border-top: 2px solid var(--border-color);';
            finalSection.innerHTML = `
                <h2 style="color: var(--primary-blue); margin-bottom: var(--space-4);">Final Synthesis</h2>
                <div>${this.formatContent(result.synthesis)}</div>
            `;
            this.resultsContent.appendChild(finalSection);
        }
        
        // Update metrics (now in header)
        const elapsed = (Date.now() - this.startTime) / 1000;
        // this.totalTime.textContent = this.formatTime(elapsed);
        // this.tokensGenerated.textContent = result.total_tokens || 0;
        // this.agentsUsed.textContent = result.agents_used?.length || 0;
        // this.successRate.textContent = '100%';
        
        // Update final header metrics
        const minutes = Math.floor(elapsed / 60);
        const seconds = Math.floor(elapsed % 60);
        const formatted = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Final update of header stats
        if (this.totalTokensDisplay) {
            this.totalTokensDisplay.textContent = result.total_tokens || this.totalTokens;
        }
        if (this.elapsedTimeDisplay) {
            this.elapsedTimeDisplay.textContent = formatted;
        }
        if (this.activeAgentCountHeader) {
            this.activeAgentCountHeader.textContent = '0';
        }
        
        // Add to timeline
        this.addTimelineEvent('Research completed successfully', 'success');
        
        // Update chart (removed)
        // this.updateChart();
    }
    
    handleError(message) {
        this.isProcessing = false;
        this.stopElapsedTimer();
        
        this.resultsContent.innerHTML = `
            <div class="error-state" style="color: var(--accent-red); text-align: center; padding: var(--space-8);">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: var(--space-4);">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <p>${message}</p>
            </div>
        `;
        
        this.addTimelineEvent(`Error: ${message}`, 'error');
    }
    
    clearResults() {
        this.resultsContent.innerHTML = `
            <div class="loading-state" style="text-align: center; padding: var(--space-8);">
                <div class="loading" style="margin: 0 auto var(--space-2);"></div>
                <p style="color: var(--gray-500); font-size: 14px;">Processing your research query...</p>
            </div>
        `;
        
        this.timeline.innerHTML = '';
        // Metrics now in header
        // this.totalTime.textContent = '--:--';
        // this.tokensGenerated.textContent = '0';
        // this.agentsUsed.textContent = '0';
        // this.successRate.textContent = '--%';
        
        // Reset all agent statuses
        this.agentGrid.querySelectorAll('.agent-card').forEach(card => {
            card.classList.remove('active', 'thinking', 'complete');
            card.querySelector('.agent-status').textContent = 'Idle';
        });
    }
    
    addTimelineEvent(message, type = 'info') {
        const time = this.startTime ? ((Date.now() - this.startTime) / 1000).toFixed(1) : '0.0';
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        
        const dotColor = {
            info: 'var(--gray-400)',
            agent: 'var(--primary-blue)',
            success: 'var(--accent-green)',
            error: 'var(--accent-red)'
        }[type] || 'var(--gray-400)';
        
        timelineItem.innerHTML = `
            <div class="timeline-time">${time}s</div>
            <div class="timeline-dot" style="background: ${dotColor}"></div>
            <div class="timeline-content">${message}</div>
        `;
        
        this.timeline.appendChild(timelineItem);
        this.timeline.scrollTop = this.timeline.scrollHeight;
    }
    
    startElapsedTimer() {
        this.totalTokens = 0;
        this.agentTokens = {}; // Reset per-agent token counts
        this.activeAgents = 0;
        
        this.elapsedInterval = setInterval(() => {
            const elapsed = (Date.now() - this.startTime) / 1000;
            const formatted = this.formatTime(elapsed);
            
            // Update header displays
            if (this.elapsedTimeDisplay) {
                this.elapsedTimeDisplay.textContent = formatted;
            }
            
            if (this.totalTokensDisplay) {
                this.totalTokensDisplay.textContent = this.totalTokens.toLocaleString();
            }
            
            if (this.activeAgentCountHeader) {
                this.activeAgentCountHeader.textContent = this.activeAgents;
            }
            
            // Update elapsed time in timeline panel
            const timelineElapsed = document.getElementById('elapsedTimeTimeline');
            if (timelineElapsed) {
                timelineElapsed.textContent = formatted;
            }
            
            // Header metrics are already updated above
        }, 100);
    }
    
    stopElapsedTimer() {
        if (this.elapsedInterval) {
            clearInterval(this.elapsedInterval);
            this.elapsedInterval = null;
        }
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = (seconds % 60).toFixed(1);
        return `${mins.toString().padStart(2, '0')}:${secs.padStart(4, '0')}`;
    }
    
    updateSystemInfo() {
        // Fetch system info from API
        fetch('/api/system')
            .then(res => res.json())
            .then(data => {
                this.gpuInfo.textContent = `${data.gpu || 'Not detected'}`;
                
                // Update web search status
                this.webSearchStatus.classList.toggle('active', data.brave_api === 'Active');
                
                // Enhanced mode is always active
                this.enhancedModeStatus.classList.add('active');
            })
            .catch(err => console.error('Failed to fetch system info:', err));
        
        // Refresh every 5 seconds
        setTimeout(() => this.updateSystemInfo(), 5000);
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) {
            statusDot.classList.toggle('active', connected);
        }
    }
    
    updateActiveAgentCount() {
        const activeCount = this.agentGrid.querySelectorAll('.agent-card.thinking').length;
        this.activeAgentCount.textContent = `${activeCount} Active`;
        this.activeAgents = activeCount;
    }
    
    updateTokenCount(agent, tokens) {
        // Track tokens per agent
        this.agentTokens[agent] = tokens;
        
        // Calculate total tokens across all agents
        this.totalTokens = Object.values(this.agentTokens).reduce((sum, count) => sum + count, 0);
    }
    
    updateHeaderMetrics(metrics) {
        // Header metrics are updated directly in the interval
        // This method is no longer needed but kept for compatibility
    }
    
    async loadAvailableModels() {
        try {
            const response = await fetch('/api/models');
            this.availableModels = await response.json();
            this.renderAvailableModels();
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    }
    
    renderAvailableModels() {
        const container = document.getElementById('availableModels');
        if (!container) return;
        
        container.innerHTML = this.availableModels.map(model => {
            const statusClass = model.available ? 'available' : 'missing';
            const statusIcon = model.available ? '✅' : '❌';
            return `
                <div class="model-item ${statusClass}">
                    <span>${statusIcon} ${model.id}</span>
                    <span class="model-size">${model.size}</span>
                </div>
            `;
        }).join('');
        
        // Add click handlers
        container.querySelectorAll('.query-item').forEach(item => {
            item.addEventListener('click', () => {
                this.researchInput.value = item.dataset.query;
                this.startResearch();
            });
        });
    }
    
    
    updateChart() {
        if (!this.performanceChart) return;
        
        // Add random data point for demo
        const currentData = this.performanceChart.data.datasets[0].data;
        currentData.push(Math.random() * 100 + 50);
        
        // Keep only last 20 points
        if (currentData.length > 20) {
            currentData.shift();
        }
        
        this.performanceChart.data.labels = currentData.map((_, i) => i);
        this.performanceChart.update();
    }
    
    startVoiceInput() {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Voice input is not supported in your browser');
            return;
        }
        
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            this.researchInput.placeholder = 'Listening...';
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.researchInput.value = transcript;
            this.researchInput.placeholder = 'What would you like to research?';
        };
        
        recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            this.researchInput.placeholder = 'What would you like to research?';
        };
        
        recognition.start();
    }
    
    handlePanelAction(action) {
        switch (action) {
            case 'copy':
                this.copyResults();
                break;
            case 'download':
                this.downloadResults();
                break;
            case 'fullscreen':
                this.toggleFullscreen();
                break;
        }
    }
    
    copyResults() {
        const text = this.resultsContent.innerText;
        navigator.clipboard.writeText(text).then(() => {
            // Show success notification
            this.showNotification('Results copied to clipboard');
        });
    }
    
    downloadResults() {
        const text = this.resultsContent.innerText;
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `research-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    toggleFullscreen() {
        const panel = document.querySelector('.results-panel');
        if (panel.classList.contains('fullscreen')) {
            panel.classList.remove('fullscreen');
        } else {
            panel.classList.add('fullscreen');
        }
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: var(--space-4);
            right: var(--space-4);
            background: var(--gray-900);
            color: white;
            padding: var(--space-3) var(--space-4);
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            animation: slideUp 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    loadDemoScenarios() {
        fetch('/api/scenarios')
            .then(res => res.json())
            .then(scenarios => {
                // Update quick action buttons with demo scenarios
                const actionGrid = document.querySelector('.action-grid');
                if (actionGrid && scenarios.length > 0) {
                    // Take first 6 scenarios for quick actions
                    const quickScenarios = scenarios.slice(0, 6);
                    actionGrid.innerHTML = quickScenarios.map(scenario => `
                        <button class="action-btn" data-prompt="${scenario.query}" data-mode="${scenario.mode}">
                            ${scenario.title.replace(/[🎵🔬🎨📖🌍💡]/g, '').trim()}
                        </button>
                    `).join('');
                    
                    // Re-attach event listeners
                    actionGrid.querySelectorAll('.action-btn').forEach(btn => {
                        btn.addEventListener('click', () => {
                            this.researchInput.value = btn.dataset.prompt;
                            if (btn.dataset.mode) {
                                this.currentMode = btn.dataset.mode;
                                this.modeButtons.forEach(b => b.classList.remove('active'));
                                document.querySelector(`.mode-btn[data-mode="${btn.dataset.mode}"]`)?.classList.add('active');
                            }
                            this.startResearch();
                        });
                    });
                }
            })
            .catch(err => console.error('Failed to load scenarios:', err));
    }
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(20px);
        }
    }
    
    .results-panel.fullscreen {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1000;
        margin: 0;
        border-radius: 0;
    }
`;
document.head.appendChild(style);

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new LocalMindDashboard();
});