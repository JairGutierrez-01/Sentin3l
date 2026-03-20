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
        grid: document.getElementById('recent-carousel'), // Mantenemos el ID para no romper tu HTML
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

            // ¡MAGIA!: Actualizamos el feed global automáticamente después de un escaneo
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
            const response = await fetch('/api/v1/recent?limit=9'); // 9 queda perfecto en un grid de 3x3
            if (!response.ok) throw new Error("Failed to fetch recent activity");

            const data = await response.json();
            renderRecentGrid(data);
        } catch (err) {
            console.error("Live Activity Error:", err);
            uiRecent.grid.innerHTML = '<p class="text-red-400 text-sm col-span-full">Could not load recent scans.</p>';
        }
    }

    // --- FUNCIONES DE RENDERIZADO (UI) ---
    function renderResults(data) {
        ui.results.classList.remove('hidden');

        ui.score.innerText = data.suspicion_score;
        ui.level.innerText = data.risk_level;
        ui.explanation.innerText = data.explanation_text;

        applyRiskStyles(data.risk_level);
        renderFlags(data.flags);
    }

    function renderFlags(flags) {
        ui.flagsGrid.innerHTML = '';

        if (flags.length === 0) {
            ui.flagsGrid.innerHTML = '<p class="text-slate-500 italic col-span-full">No specific technical flags detected.</p>';
            return;
        }

        flags.forEach(flag => {
            const card = document.createElement('div');
            card.className = "bg-slate-800/60 border border-slate-700 p-4 rounded-xl";
            card.innerHTML = `
                <h4 class="text-emerald-400 font-bold text-sm mb-1">${flag.code}</h4>
                <p class="text-slate-300 text-sm leading-relaxed">${flag.evidence_summary}</p>
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
                'High': 'border-red-500/50 bg-red-900/20 text-red-400',
                'Medium': 'border-yellow-500/50 bg-yellow-900/20 text-yellow-400',
                'Safe': 'border-emerald-500/50 bg-emerald-900/20 text-emerald-400'
            };
            const style = colors[item.risk_level] || colors['Safe'];

            // 2. Extraer datos reales del backend
            const timeString = timeAgo(item.analyzed_at);
            const occurrences = item.times_analyzed_before || 1;
            const occurrenceText = occurrences === 1 ? '1st Scan' : `Seen ${occurrences} times`;

            const card = document.createElement('div');
            // Quitamos las clases de carrusel y dejamos un diseño limpio de Grid
            card.className = `p-5 rounded-xl border flex flex-col justify-between transition-transform hover:scale-[1.02] cursor-default ${style}`;

            card.innerHTML = `
                <div>
                    <div class="flex justify-between items-center mb-3">
                        <span class="font-bold text-xs uppercase tracking-widest">${item.risk_level}</span>
                        <span class="text-xl font-black opacity-80">${item.suspicion_score}</span>
                    </div>
                    <p class="text-slate-300 text-sm font-mono truncate" title="${item.target_url}">${item.target_url}</p>
                </div>
                
                <div class="mt-4 border-t border-slate-700/50 pt-3 flex justify-between items-center text-[10px] text-slate-400 uppercase tracking-wide">
                    <span>${timeString}</span>
                    <span class="bg-slate-800/80 px-2 py-1 rounded-md text-slate-300 font-semibold border border-slate-700">
                        ${occurrenceText}
                    </span>
                </div>
            `;

            uiRecent.grid.appendChild(card);
        });
    }

    function applyRiskStyles(level) {
        ui.verdictCard.className = "md:col-span-2 p-6 rounded-2xl border flex flex-col justify-center transition-colors duration-500 ";

        const styles = {
            'High': 'bg-red-900/20 border-red-500/50 text-red-400',
            'Medium': 'bg-yellow-900/20 border-yellow-500/50 text-yellow-400',
            'Safe': 'bg-emerald-900/20 border-emerald-500/50 text-emerald-400'
        };

        ui.verdictCard.classList.add(...(styles[level] || styles['Safe']).split(' '));
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