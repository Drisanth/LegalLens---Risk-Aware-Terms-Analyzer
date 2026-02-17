document.getElementById('analyze-btn').addEventListener('click', async () => {
    document.getElementById('initial-view').style.display = 'none';
    document.getElementById('loader').style.display = 'block';

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Request text from content script
        chrome.tabs.sendMessage(tab.id, { action: "getText" }, async (response) => {
            if (chrome.runtime.lastError || !response) {
                showError("Could not retrieve page text. Refresh and try again.");
                return;
            }

            // Call API
            try {
                const formData = new FormData();
                formData.append('text', response.text);

                const res = await fetch('http://localhost:8000/analyze', {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) throw new Error("API Error");

                const data = await res.json();
                displayResults(data);

            } catch (err) {
                showError("Backend API unreachable. Ensure server is running at localhost:8000");
                console.error(err);
            }
        });

    } catch (err) {
        showError("Extension Error: " + err.message);
    }
});

function displayResults(data) {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('results-view').style.display = 'block';

    // Score
    const scoreEl = document.getElementById('risk-score-display');
    const score = data.overall_risk_score;
    scoreEl.textContent = (score * 10).toFixed(1) + "/10";

    if (score > 0.7) scoreEl.className = "risk-score risk-high";
    else if (score > 0.4) scoreEl.className = "risk-score risk-medium";
    else scoreEl.className = "risk-score risk-low";

    // Clauses
    const list = document.getElementById('clauses-list');
    list.innerHTML = '';

    // Sort by final risk desc
    const sorted = data.clause_level_scores.sort((a, b) => b.final_risk - a.final_risk);
    const top3 = sorted.slice(0, 3);

    top3.forEach(c => {
        const div = document.createElement('div');
        div.className = 'clause-item';
        div.innerHTML = `
      <div style="color: #fb7185; font-weight: bold;">Risk: ${(c.final_risk * 100).toFixed(0)}%</div>
      <div style="color: #cbd5e1; max-height: 40px; overflow: hidden;">${c.text.substring(0, 80)}...</div>
    `;
        list.appendChild(div);
    });

    // View Full (opens dashboard)
    document.getElementById('view-full-btn').onclick = () => {
        chrome.tabs.create({ url: 'http://localhost:5173' }); // Assuming default vite port
    };
}

function showError(msg) {
    document.getElementById('loader').style.display = 'none';
    alert(msg);
    document.getElementById('initial-view').style.display = 'block';
}
