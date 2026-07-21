document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const presetBtns = document.querySelectorAll('.btn-preset');
    const btnRun = document.getElementById('btn-run-validation');
    const schemaInput = document.getElementById('schema-input');
    const delimiterSelect = document.getElementById('delimiter-select');
    const encodingSelect = document.getElementById('encoding-select');
    const flattenCheck = document.getElementById('flatten-json-check');
    
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

            // Preset specific overrides
            if (activeSample === 'semicolon') {
                delimiterSelect.value = ';';
            } else if (activeSample === 'latin1') {
                encodingSelect.value = 'latin-1';
            } else if (activeSample === 'nested_json') {
                flattenCheck.checked = true;
                schemaInput.value = 'id, transaction_date, amount, customer.id, customer.name, customer.location.city, customer.location.country';
            } else {
                schemaInput.value = 'transaction_id, customer_id, transaction_date, amount';
            }

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
        dropZone.querySelector('.secondary-text').innerHTML = 'or <span class="browse-link">browse files</span> (CSV, JSON, XLSX)';
    }

    async function runValidation() {
        btnRun.disabled = true;
        btnRun.innerText = 'Ingesting & Validating...';

        try {
            let resData;
            const expectedCols = schemaInput.value.trim();
            const delimiter = delimiterSelect.value;
            const encoding = encodingSelect.value;
            const isNested = flattenCheck.checked;

            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('expected_cols', expectedCols);
                formData.append('delimiter', delimiter);
                formData.append('encoding', encoding);
                formData.append('is_nested', isNested);

                const res = await fetch('/api/validate', {
                    method: 'POST',
                    body: formData
                });
                resData = await res.json();
            } else if (activeSample) {
                const res = await fetch(`/api/sample/${activeSample}`, {
                    method: 'POST'
                });
                resData = await res.json();
            }

            renderReport(resData);
        } catch (err) {
            console.error('Validation error:', err);
            alert('Failed to execute ingestion request. Ensure app server is running.');
        } finally {
            btnRun.disabled = false;
            btnRun.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Run Ingestion & Quality Gates`;
        }
    }

    function renderReport(resData) {
        const valReport = resData.validation || {};
        const ingReport = resData.ingestion || {};

        document.getElementById('report-timestamp').textContent = valReport.timestamp ? new Date(valReport.timestamp).toLocaleString() : '--';
        document.getElementById('meta-filepath').textContent = valReport.filepath || '--';
        document.getElementById('json-viewer').textContent = JSON.stringify(resData, null, 2);

        const banner = document.getElementById('overall-banner');
        const bannerTitle = document.getElementById('banner-title');
        const bannerMsg = document.getElementById('banner-msg');
        const bannerIcon = document.getElementById('banner-icon');

        if (valReport.status === 'PASSED') {
            banner.className = 'banner banner-passed';
            bannerTitle.textContent = 'INGESTION PASSED: Safe For Ingestion';
            bannerMsg.textContent = 'Dataset verified and successfully ingested into DataFrame.';
            bannerIcon.textContent = '✓';
        } else {
            banner.className = 'banner banner-failed';
            bannerTitle.textContent = 'INGESTION BLOCKED: Quality Gate Failed';
            bannerMsg.textContent = 'Validation error detected! Pipeline stopped to protect downstream steps.';
            bannerIcon.textContent = '✕';
        }

        // Render Ingestion Audit Report
        document.getElementById('audit-source').textContent = ingReport.source || valReport.filepath || '--';
        document.getElementById('audit-encoding').textContent = ingReport.used_encoding || '--';
        document.getElementById('audit-delimiter').textContent = ingReport.used_delimiter || '--';
        document.getElementById('audit-shape').textContent = (ingReport.rows !== undefined && ingReport.columns !== undefined) 
            ? `${ingReport.rows} Rows x ${ingReport.columns} Cols` 
            : '--';

        const tagsContainer = document.getElementById('dtypes-tags');
        tagsContainer.innerHTML = '';
        if (ingReport.column_types) {
            Object.entries(ingReport.column_types).forEach(([col, dtype]) => {
                const nulls = ingReport.null_counts ? ingReport.null_counts[col] : 0;
                const tag = document.createElement('span');
                tag.className = 'dtype-tag';
                tag.textContent = `${col}: ${dtype} (${nulls} nulls)`;
                tagsContainer.appendChild(tag);
            });
        }

        // Render each gate check card
        const checks = valReport.checks || {};
        updateCheckCard('file_exists', checks.file_exists);
        updateCheckCard('format', checks.format);
        updateCheckCard('schema', checks.schema);
        updateCheckCard('encoding', checks.encoding);
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
