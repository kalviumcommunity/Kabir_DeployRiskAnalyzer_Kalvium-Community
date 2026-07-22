document.addEventListener('DOMContentLoaded', () => {
    const btnRun = document.getElementById('btn-run-profiling');
    const fileInput = document.getElementById('file-input-profile');
    const filepathInput = document.getElementById('filepath-input');
    const resultsPanel = document.getElementById('profile-results');
    const loadingPanel = document.getElementById('profile-loading');
    
    btnRun.addEventListener('click', async () => {
        resultsPanel.style.display = 'none';
        loadingPanel.style.display = 'block';
        
        const formData = new FormData();
        if (fileInput.files.length > 0) {
            formData.append('file', fileInput.files[0]);
        } else {
            formData.append('filepath', filepathInput.value);
        }
        
        try {
            const response = await fetch('/api/profile', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            loadingPanel.style.display = 'none';
            if (data.status === 'SUCCESS') {
                renderReport(data.report);
                resultsPanel.style.display = 'block';
            } else {
                alert("Error running profile: " + data.message);
            }
        } catch (e) {
            loadingPanel.style.display = 'none';
            alert("API Error: " + e.message);
        }
    });

    function renderReport(report) {
        document.getElementById('profile-timestamp').innerText = new Date().toLocaleString();
        document.getElementById('stat-records').innerText = report.record_count;
        document.getElementById('stat-columns').innerText = report.column_count;
        document.getElementById('stat-dups').innerText = report.nulls_and_duplicates.duplicate_percentage + "%";
        
        const issuesContainer = document.getElementById('issues-container');
        issuesContainer.innerHTML = '';
        document.getElementById('issues-count').innerText = report.quality_issues.length;
        
        if (report.quality_issues.length === 0) {
            issuesContainer.innerHTML = '<p style="color: #4ade80;">No major quality issues detected!</p>';
        } else {
            report.quality_issues.forEach(issue => {
                const div = document.createElement('div');
                div.className = `issue-card ${issue.severity.toLowerCase()}`;
                div.innerHTML = `
                    <div class="issue-title">[${issue.severity}] ${issue.type} in '${issue.column}'</div>
                    <div>Value: <strong>${issue.value}</strong></div>
                    <div class="issue-rec">→ ${issue.recommendation}</div>
                `;
                issuesContainer.appendChild(div);
            });
        }
        
        document.getElementById('profile-json-viewer').innerText = JSON.stringify(report, null, 2);
    }
});
