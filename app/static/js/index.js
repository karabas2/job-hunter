let currentUserId = 1; // Default for prototype

function showSection(id, el) {
    document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
    document.getElementById(id).style.display = 'block';
    if (el) {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        el.classList.add('active');
    }
    document.getElementById('section-title').innerText = id.charAt(0).toUpperCase() + id.slice(1);
}

async function fetchJobs() {
    try {
        const response = await fetch('/api/jobs');
        const jobs = await response.json();

        const feed = document.getElementById('job-feed');
        feed.innerHTML = '';

        document.getElementById('stat-total').innerText = jobs.length;
        document.getElementById('stat-matches').innerText = jobs.filter(j => j.match_score > 0.0).length;

        if (jobs.length === 0) {
            feed.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 5rem; color: var(--text-secondary); font-weight: 600;">No jobs found yet. Click "Start Scan" to find matches.</div>';
            return;
        }

        jobs.sort((a, b) => b.id - a.id).forEach(job => {
            const card = document.createElement('div');
            card.className = 'job-card fade-in';
            card.innerHTML = `
                <div class="match-badge">${Math.round(job.match_score * 100)}% Match</div>
                <div class="job-title">${job.title}</div>
                <div class="company-name"><i data-lucide="building-2" style="width:16px"></i> ${job.company}</div>
                <div class="company-name"><i data-lucide="map-pin" style="width:16px"></i> ${job.location}</div>
                <div>
                    <span class="seniority-tag ${job.seniority_requirement?.toLowerCase()}">${job.seniority_requirement || 'Any'}</span>
                </div>
                <div class="job-footer">
                    <a href="${job.url}" target="_blank" class="view-btn">View Link <i data-lucide="external-link" style="width:14px"></i></a>
                    <span style="font-size: 0.75rem; color: var(--text-secondary)">ID: ${job.linkedin_job_id.substring(0, 8)}...</span>
                </div>
            `;
            feed.appendChild(card);
        });
        lucide.createIcons();
    } catch (err) {
        console.error("Fetch error:", err);
    }
}

async function triggerScan() {
    const btn = document.querySelector('.btn-primary');
    const oldText = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Searching...';
    lucide.createIcons();

    try {
        await fetch(`/api/trigger/${currentUserId}`, { method: 'POST' });
        document.getElementById('status-badge').innerHTML = '<span class="pulse"></span> Initializing...';
        checkStatus();
    } catch (err) {
        alert("Scan failed to trigger.");
        btn.innerHTML = oldText;
        lucide.createIcons();
    }
}

async function checkStatus() {
    const statusBadge = document.getElementById('status-badge');
    const scanBtn = document.querySelector('.btn-primary');
    const progressBar = document.getElementById('scan-progress-bar');
    const progressContainer = document.getElementById('scan-progress-container');

    progressContainer.style.display = 'block';
    let progress = 0;

    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${currentUserId}`);
            const data = await response.json();

            if (data.is_scanning) {
                progress += (95 - progress) * 0.1;
                progressBar.style.width = progress + '%';
                statusBadge.innerHTML = '<span class="pulse"></span> Scanning LinkedIn...';
            } else {
                progressBar.style.width = '100%';
                statusBadge.innerHTML = '<i data-lucide="check-circle" style="color: var(--success)"></i> Scan Complete';
                document.getElementById('stat-last').innerText = new Date().toLocaleTimeString();

                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressBar.style.width = '0%';
                }, 3000);

                scanBtn.innerHTML = '<i data-lucide="refresh-cw"></i> Start Scan';
                fetchJobs();
                lucide.createIcons();
                clearInterval(interval);
            }
        } catch (err) {
            console.error("Status check failed:", err);
            clearInterval(interval);
        }
    }, 2500);
}

async function saveProfile() {
    const cv = document.getElementById('cv-input').value;
    await updateUserData({ cv_text: cv });
    alert("AI Profile Updated!");
}

async function saveSettings() {
    const data = {
        email: document.getElementById('pref-email').value,
        linkedin_search_url: document.getElementById('pref-url').value,
        keywords: document.getElementById('pref-keywords').value,
        exclude_keywords: document.getElementById('pref-exclude').value,
        target_status: document.getElementById('pref-status').value
    };
    await updateUserData(data);
    alert("Preferences Saved!");
}

async function updateUserData(data) {
    try {
        await fetch(`/api/users/${currentUserId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    } catch (err) {
        console.error("Update failed:", err);
    }
}

async function loadUserData() {
    try {
        const response = await fetch(`/api/users/${currentUserId}`);
        if (!response.ok) return;
        const user = await response.json();

        document.getElementById('cv-input').value = user.cv_text || '';
        document.getElementById('pref-email').value = user.email || '';
        document.getElementById('pref-url').value = user.linkedin_search_url || '';
        document.getElementById('pref-keywords').value = user.keywords || '';
        document.getElementById('pref-exclude').value = user.exclude_keywords || '';
        document.getElementById('pref-status').value = user.target_status || 'Student';
    } catch (err) {
        console.log("No user data yet.");
    }
}

window.onload = () => {
    fetchJobs();
    loadUserData();
};
