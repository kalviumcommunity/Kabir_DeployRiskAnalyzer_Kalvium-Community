document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const presetBtns = document.querySelectorAll('.btn-preset');
    const btnRun = document.getElementById('btn-run-validation');
    const schemaInput = document.getElementById('schema-input');
    
    let selectedFile = null;
    let activeSample = 'valid';

    // Drag & Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            selectedFile = e.dataTransfer.files[0];
            activeSample = null;
            updateDropZoneUI(selectedFile.name);
            presetBtns.forEach(btn => btn.classList.remove('active'));
            runValidation();
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            activeSample = null;
            updateDropZoneUI(selectedFile.name);
            presetBtns.forEach(btn => btn.classList.remove('active'));
            runValidation();
        }
    });

    // Preset buttons
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            presetBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeSample = btn.dataset.sample;
            selectedFile = null;
            resetDropZoneUI();
            runValidation();
        });
    });

    btnRun.addEventListener('click', () => {
        runValidation();
    });

    function updateDropZoneUI(filename) {
        dropZone.querySelector('.primary-text').textContent = `File selected: ${filename}`;
        dropZone.querySelector('.secondary-text').innerHTML = `Click run validation below to verify quality gate`;
    }

    function resetDropZoneUI() {
        dropZone.querySelector('.primary-text').textContent = 'Drag & drop dataset here';
        dropZone.querySelector('.secondary-text').innerHTML = 'or <span class="browse-link">browse files</span> (CSV, JSON, XLSX, Parquet)';
    }

    async function runValidation() {
        btnRun.disabled = true;
        btnRun.innerText = 'Validating Quality Firewall...';

        try {
            let report;
            const expectedCols = schemaInput.value.trim();

            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('expected_cols', expectedCols);

                const res = await fetch('/api/validate', {
                    method: 'POST',
                    body: formData
                });
                report = await res.json();
            } else if (activeSample) {
                const res = await fetch(`/api/sample/${activeSample}`, {
                    method: 'POST'
                });
                report = await res.json();
            }

            renderReport(report);
        } catch (err) {
            console.error('Validation error:', err);
            alert('Failed to execute validation request. Ensure app server is running.');
        } finally {
            btnRun.disabled = false;
            btnRun.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Run Validation Firewall`;
        }
    }

    function renderReport(report) {
        document.getElementById('report-timestamp').textContent = report.timestamp ? new Date(report.timestamp).toLocaleString() : '--';
        document.getElementById('meta-filepath').textContent = report.filepath || '--';
        document.getElementById('json-viewer').textContent = JSON.stringify(report, null, 2);

        const banner = document.getElementById('overall-banner');
        const bannerTitle = document.getElementById('banner-title');
        const bannerMsg = document.getElementById('banner-msg');
        const bannerIcon = document.getElementById('banner-icon');

        if (report.status === 'PASSED') {
            banner.className = 'banner banner-passed';
            bannerTitle.textContent = 'GATE PASSED: Ingestion Approved';
            bannerMsg.textContent = 'Dataset satisfies all 5 quality firewall checks. Safe for downstream pipeline.';
            bannerIcon.textContent = '✓';
        } else {
            banner.className = 'banner banner-failed';
            bannerTitle.textContent = 'GATE FAILED: Ingestion Blocked';
            bannerMsg.textContent = 'Validation errors detected! Downstream pipeline stopped to protect pipeline.';
            bannerIcon.textContent = '✕';
        }

        // Render each gate check card
        const checks = report.checks || {};

        updateCheckCard('file_exists', checks.file_exists);
        updateCheckCard('format', checks.format);
        updateCheckCard('schema', checks.schema);
        updateCheckCard('encoding', checks.encoding);

        // Dimensions Check & Stats
        const dimCheck = checks.dimensions;
        updateCheckCard('dimensions', dimCheck);

        const statsRow = document.getElementById('stats-container');
        if (report.statistics) {
            statsRow.classList.remove('hidden');
            document.getElementById('stat-rows').textContent = report.statistics.rows ?? '0';
            document.getElementById('stat-cols').textContent = report.statistics.columns ?? '0';
            document.getElementById('stat-size').textContent = `${report.statistics.file_size_mb ?? 0} MB`;
        } else {
            statsRow.classList.add('hidden');
        }
    }

    function updateCheckCard(checkKey, checkObj) {
        const badge = document.getElementById(`badge-${checkKey}`);
        const msg = document.getElementById(`msg-${checkKey}`);

        if (!checkObj) {
            badge.className = 'check-badge badge-pending';
            badge.textContent = 'Skipped';
            msg.textContent = 'Gate skipped due to fail-fast policy on previous check.';
            return;
        }

        if (checkObj.passed) {
            badge.className = 'check-badge badge-passed';
            badge.textContent = 'Passed';
            msg.textContent = checkObj.message || 'Check passed successfully.';
        } else {
            badge.className = 'check-badge badge-failed';
            badge.textContent = 'Failed';
            msg.textContent = checkObj.message || 'Validation error detected.';
        }
    }

    // Run initial validation on page load
    runValidation();
});
