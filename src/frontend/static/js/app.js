document.addEventListener('DOMContentLoaded', () => {
    // principal inteface
    const ui = {
        btn: document.getElementById('analyze-btn'),
        input: document.getElementById('url-input'),
        results: document.getElementById('results-container'),
        score: document.getElementById('risk-score'),
        level: document.getElementById('risk-level'),
        verdictCard: document.getElementById('verdict-card'),
        explanation: document.getElementById('explanation-text'),
        flagsGrid: document.getElementById('flags-grid')
    };

    // global feed
    const uiRecent = {
        grid: document.getElementById('recent-carousel'),
        loading: document.getElementById('carousel-loading')
    };

    ui.btn.addEventListener('click', handleAnalysis);

    // history
    loadRecentActivity();

    async function handleAnalysis() {
        const url = ui.input.value.trim();
        if (!url) return;

        setLoading(true);

        try {
            const data = await fetchAnalysis(url);
            renderResults(data);

            loadRecentActivity();

        } catch (err) {
            console.error("Analysis Error:", err);
            alert("Error analyzing the URL. Check console for details.");
        } finally {
            setLoading(false);
        }
    }

    // API communication
    async function fetchAnalysis(url) {
        const response = await fetch('/api/v1/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        if (!response.ok) throw new Error("API Connection Failed");
        return await response.json();
    }

    async function loadRecentActivity() {
        try {
            const response = await fetch('/api/v1/recent?limit=9');
            if (!response.ok) throw new Error("Failed to fetch recent activity");

            const data = await response.json();
            renderRecentGrid(data);
        } catch (err) {
            console.error("Live Activity Error:", err);
            uiRecent.grid.innerHTML = '<p class="text-red-400 text-sm col-span-full">Could not load recent scans.</p>';
        }
    }

    function renderResults(data) {
        ui.results.classList.remove('hidden');

        ui.level.innerText = data.risk_level;
        ui.explanation.innerText = data.explanation_text;

        const scoreBadge = document.getElementById('score-badge');
        const recommendationText = document.getElementById('recommendation-text');

        scoreBadge.innerText = data.suspicion_score;
        recommendationText.innerText = data.recommendation_text || "Be cautious with this URL.";

        applyRiskStyles(data.risk_level, data.suspicion_score);
        renderFlags(data.flags);
    }

    function renderFlags(flags) {
        ui.flagsGrid.innerHTML = '';

        if (!flags || flags.length === 0) {
            ui.flagsGrid.innerHTML = `
                <div class="col-span-full bg-emerald-900/20 border border-emerald-500/30 p-6 rounded-xl flex items-center gap-4 shadow-inner">
                    <i class="ph-fill ph-check-circle text-emerald-500 text-3xl"></i>
                    <p class="text-emerald-400 font-medium">No suspicious technical flags detected. This URL looks clean.</p>
                </div>
            `;
            return;
        }


        flags.forEach(flag => {

            let iconClass = "ph-warning";
            let colorClass = "text-yellow-500";

            if (flag.code.includes('BRAND') || flag.code.includes('TYPO')) {
                iconClass = "ph-buildings";
                colorClass = "text-red-400";
            } else if (flag.code.includes('IP_') || flag.code.includes('PORT')) {
                iconClass = "ph-hard-drives";
            } else if (flag.code.includes('URL') || flag.code.includes('PUNYCODE')) {
                iconClass = "ph-link-break";
            }

            const card = document.createElement('div');

            card.className = "bg-panel/40 border border-slate-700/50 p-5 rounded-xl flex flex-col gap-4 shadow-lg hover:border-slate-500 transition-colors";

            card.innerHTML = `
                <div class="flex items-center gap-3">
                    <i class="ph-fill ${iconClass} ${colorClass} text-2xl drop-shadow-md"></i>
                    <h4 class="text-slate-200 font-bold text-sm tracking-wide uppercase">${flag.name || flag.code}</h4>
                </div>
                
                <div class="text-slate-400 text-sm leading-relaxed border-l-2 border-slate-700 pl-3">
                    <span class="block text-[10px] uppercase tracking-widest text-slate-500 mb-1 font-semibold">What is this?</span>
                    ${flag.description || 'Suspicious indicator detected by the system.'}
                </div>
                
                <div class="mt-auto pt-4 border-t border-slate-800/80">
                    <span class="block text-[10px] uppercase tracking-widest text-emerald-500/70 mb-1 font-semibold flex items-center gap-1">
                        <i class="ph-fill ph-magnifying-glass"></i> Finding
                    </span>
                    <p class="text-slate-300 text-xs font-mono bg-[#0b1120] p-3 rounded-lg border border-slate-800/80 break-words leading-relaxed">
                        ${flag.evidence_summary}
                    </p>
                </div>
            `;
            ui.flagsGrid.appendChild(card);
        });
    }

    function renderRecentGrid(analyses) {
        uiRecent.grid.innerHTML = '';

        if (analyses.length === 0) {
            uiRecent.grid.innerHTML = '<p class="text-slate-500 italic col-span-full">No recent scans yet. Be the first!</p>';
            return;
        }

        analyses.forEach(item => {
            const colors = {
                'High': {
                    container: 'border-red-900/50 bg-gradient-to-br from-[#2a0808] to-panel',
                    text: 'text-red-500',
                    icon: '<i class="ph-fill ph-warning-octagon text-red-500 text-xl"></i>'
                },
                'Medium': {
                    container: 'border-yellow-900/50 bg-gradient-to-br from-[#2a1f08] to-panel',
                    text: 'text-yellow-500',
                    icon: '<i class="ph-fill ph-warning text-yellow-500 text-xl"></i>'
                },
                'Safe': {
                    container: 'border-emerald-900/50 bg-gradient-to-br from-[#062a1a] to-panel',
                    text: 'text-emerald-500',
                    icon: '<i class="ph-fill ph-shield-check text-emerald-500 text-xl"></i>'
                }
            };

            const style = colors[item.risk_level] || colors['Safe'];

            const timeString = timeAgo(item.analyzed_at);
            const occurrences = item.times_analyzed_before || 1;
            const occurrenceText = occurrences === 1 ? '1st Scan' : `Seen ${occurrences} times`;

            const card = document.createElement('div');
            card.className = `p-5 rounded-xl border flex flex-col justify-between shadow-lg ${style.container}`;

            card.innerHTML = `
                <div>
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center gap-2">
                            ${style.icon}
                            <span class="font-bold text-xs uppercase tracking-wider ${style.text}">${item.risk_level}</span>
                        </div>
                        <span class="text-sm font-bold opacity-50 text-white">Score: ${item.suspicion_score}</span>
                    </div>
                    <p class="text-slate-300 text-sm font-mono truncate" title="${item.target_url}">${item.target_url}</p>
                </div>
                
                <div class="mt-4 border-t border-slate-700/50 pt-3 flex justify-between items-center text-[10px] text-slate-400 uppercase tracking-wide">
                    <span class="flex items-center gap-1"><i class="ph ph-clock"></i> ${timeString}</span>
                    <span class="bg-black/30 px-2 py-1 rounded border border-slate-700/50 font-semibold text-slate-300">
                        ${occurrenceText}
                    </span>
                </div>
            `;
            uiRecent.grid.appendChild(card);
        });
    }

    function applyRiskStyles(level, score) {
        const gaugeArc = document.getElementById('gauge-arc');
        const scoreBadge = document.getElementById('score-badge');

        ui.verdictCard.className = "p-8 rounded-2xl border flex flex-col md:flex-row items-center gap-8 shadow-2xl relative overflow-hidden transition-all duration-500 ";

        const styles = {
            'High': {
                card: 'border-red-900/50 bg-gradient-to-br from-[#2a0808] to-panel',
                gaugeColor: '#ef4444',
                badge: 'bg-red-500'
            },
            'Medium': {
                card: 'border-yellow-900/50 bg-gradient-to-br from-[#2a1f08] to-panel',
                gaugeColor: '#f59e0b',
                badge: 'bg-yellow-500'
            },
            'Safe': {
                card: 'border-emerald-900/50 bg-gradient-to-br from-[#062a1a] to-panel',
                gaugeColor: '#10b981',
                badge: 'bg-emerald-500'
            }
        };

        const currentStyle = styles[level] || styles['Safe'];


        ui.verdictCard.classList.add(...currentStyle.card.split(' '));
        gaugeArc.setAttribute('stroke', currentStyle.gaugeColor);
        scoreBadge.className = `${currentStyle.badge} text-white text-sm font-bold px-3 py-1 rounded font-mono shadow-md`;

        updateGauge(score, currentStyle.gaugeColor);
    }

    function updateGauge(score, color) {
        const gaugeArc = document.getElementById('gauge-arc');
        const scoreDisplay = document.getElementById('risk-score');


        const MAX_PERIMETER = 125.6;

        const normalizedScore = Math.min(Math.max(score, 0), 100);


        const dashFilled = (normalizedScore / 100) * MAX_PERIMETER;

        gaugeArc.setAttribute('stroke-dasharray', `${dashFilled} ${MAX_PERIMETER}`);


        animateValue(scoreDisplay, 0, normalizedScore, 1000);
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerText = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    function setLoading(isLoading) {
        ui.btn.disabled = isLoading;
        ui.btn.innerText = isLoading ? "Scanning..." : "Analyze";
        if (isLoading) ui.results.classList.add('opacity-50');
        else ui.results.classList.remove('opacity-50');
    }

    // --- UTILS ---
    function timeAgo(dateString) {
        if (!dateString) return "Unknown time";
        const date = new Date(dateString + (dateString.includes('Z') ? '' : 'Z'));
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return "Just now";
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes} min${minutes !== 1 ? 's' : ''} ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours} hr${hours !== 1 ? 's' : ''} ago`;
        const days = Math.floor(hours / 24);
        return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
});