/**
 * Main application logic
 */

// Use API_BASE from auth.js if available, otherwise use window.location.origin directly
let selectedFile = null;

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Bottom Sheet Modal
    const connectionsModal = document.getElementById('connectionsModal');
    const openConnectionsBtn = document.getElementById('openConnectionsBtn');
    const closeConnectionsBtn = document.getElementById('closeConnectionsBtn');
    const bottomSheetOverlay = document.querySelector('.bottom-sheet-overlay');
    
    function openConnectionsModal() {
        if (connectionsModal) {
            connectionsModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }
    
    function closeConnectionsModal() {
        if (connectionsModal) {
            connectionsModal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    if (openConnectionsBtn) {
        openConnectionsBtn.addEventListener('click', openConnectionsModal);
    }
    
    if (closeConnectionsBtn) {
        closeConnectionsBtn.addEventListener('click', closeConnectionsModal);
    }
    
    if (bottomSheetOverlay) {
        bottomSheetOverlay.addEventListener('click', closeConnectionsModal);
    }
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && connectionsModal && connectionsModal.classList.contains('active')) {
            closeConnectionsModal();
        }
        // Keyboard shortcut: Ctrl/Cmd + U to open file picker
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            if (fileInput && !uploadBtn.disabled) {
                fileInput.click();
            }
        }
    });
    
    // Swipe gesture for bottom sheet
    let touchStartY = 0;
    let touchEndY = 0;
    const bottomSheetContent = document.querySelector('.bottom-sheet-content');
    
    if (bottomSheetContent) {
        bottomSheetContent.addEventListener('touchstart', (e) => {
            touchStartY = e.changedTouches[0].screenY;
        }, { passive: true });
        
        bottomSheetContent.addEventListener('touchmove', (e) => {
            touchEndY = e.changedTouches[0].screenY;
        }, { passive: true });
        
        bottomSheetContent.addEventListener('touchend', () => {
            const swipeDistance = touchStartY - touchEndY;
            // If swiped down more than 100px, close modal
            if (swipeDistance < -100 && connectionsModal && connectionsModal.classList.contains('active')) {
                closeConnectionsModal();
            }
            touchStartY = 0;
            touchEndY = 0;
        }, { passive: true });
    }
    
    // DOM elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    const resultsSection = document.getElementById('resultsSection');
    const travelInfo = document.getElementById('travelInfo');
    const calendarStatus = document.getElementById('calendarStatus');
    
    if (!uploadArea || !fileInput || !uploadBtn) {
        console.error('Required DOM elements not found');
        return;
    }

    // Upload area click
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0], fileName, fileInfo, uploadBtn, uploadStatus, resultsSection);
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileSelect(file, fileName, fileInfo, uploadBtn, uploadStatus, resultsSection);
        }
    });

    // Remove file handler (will be re-attached after file selection)
    function removeFileHandler() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadBtn.style.display = 'none';
        uploadStatus.style.display = 'none';
        resultsSection.style.display = 'none';
    }
    
    // Remove file
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', removeFileHandler);
    }

    // Upload button
    console.log('Setting up upload button, element:', uploadBtn);
    if (uploadBtn) {
        uploadBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Upload button clicked!', 'selectedFile:', selectedFile);
            if (!selectedFile) {
                console.warn('No file selected');
                showStatus('error', 'Please select a file first.', uploadStatus);
                return;
            }
            
            console.log('Starting upload process...');
            await uploadAndProcess(selectedFile, uploadBtn, uploadStatus, resultsSection, travelInfo, calendarStatus);
        });
        console.log('Upload button event listener attached');
    } else {
        console.error('Upload button element not found!');
    }
});

// Handle file selection
function handleFileSelect(file, fileName, fileInfo, uploadBtn, uploadStatus, resultsSection) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        const errorMsg = `Invalid file type. Please upload JPG, PNG, or PDF. (Received: ${file.type || 'unknown'})`;
        showStatus('error', errorMsg, uploadStatus);
        if (typeof showToast !== 'undefined') {
            showToast('error', errorMsg);
        }
        return;
    }
    
    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        const errorMsg = `File too large (${fileSizeMB} MB). Maximum size is 5 MB.`;
        showStatus('error', errorMsg, uploadStatus);
        if (typeof showToast !== 'undefined') {
            showToast('error', errorMsg);
        }
        return;
    }
    
    selectedFile = file;
    
    // Create file preview
    const filePreview = createFilePreview(file);
    
    // Clear existing content
    fileInfo.innerHTML = '';
    
    // Add preview
    fileInfo.appendChild(filePreview);
    
    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.id = 'removeFile';
    removeBtn.className = 'btn-remove';
    removeBtn.textContent = 'Remove';
    fileInfo.appendChild(removeBtn);
    
    // Re-attach remove button handler
    removeBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadBtn.style.display = 'none';
        uploadStatus.style.display = 'none';
        resultsSection.style.display = 'none';
    });
    
    // Update the global removeFileBtn reference
    window.removeFileBtn = removeBtn;
    
    fileInfo.style.display = 'flex';
    uploadBtn.style.display = 'block';
    uploadStatus.style.display = 'none';
    resultsSection.style.display = 'none';
}

// Create file preview element
function createFilePreview(file) {
    const preview = document.createElement('div');
    preview.className = 'file-preview';
    
    const isImage = file.type.startsWith('image/');
    const isPDF = file.type === 'application/pdf';
    const fileSize = formatFileSize(file.size);
    
    if (isImage) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'file-preview-thumbnail';
            img.alt = file.name;
            preview.insertBefore(img, preview.firstChild);
        };
        reader.readAsDataURL(file);
    } else if (isPDF) {
        const iconWrapper = document.createElement('div');
        iconWrapper.className = 'file-preview-icon';
        iconWrapper.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                <polyline points="13 2 13 9 20 9"/>
            </svg>
        `;
        preview.insertBefore(iconWrapper, preview.firstChild);
    }
    
    const info = document.createElement('div');
    info.className = 'file-preview-info';
    info.innerHTML = `
        <div class="file-preview-name">${file.name}</div>
        <div class="file-preview-size">${fileSize}</div>
    `;
    preview.appendChild(info);
    
    return preview;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Upload and process document
async function uploadAndProcess(file, uploadBtn, uploadStatus, resultsSection, travelInfo, calendarStatus) {
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner"></span>Processing...';
    showStatus('processing', 'Processing document with AI...', uploadStatus);
    resultsSection.style.display = 'none';
    
    // Add progress indicator
    let progressBar = uploadStatus.parentElement.querySelector('.progress-bar');
    if (!progressBar) {
        progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.innerHTML = '<div class="progress-bar-fill" style="width: 0%"></div>';
        uploadStatus.parentElement.insertBefore(progressBar, uploadStatus);
    }
    const progressFill = progressBar.querySelector('.progress-bar-fill');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        // Simulate progress (since we can't track actual upload progress easily)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + 10, 90);
            if (progressFill) {
                progressFill.style.width = progress + '%';
            }
        }, 200);
        
        const response = await authenticatedFetch(`${window.location.origin}/api/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        if (progressFill) {
            progressFill.style.width = '100%';
        }
        
        if (!response.ok) {
            let errorMessage = 'Upload failed';
            try {
                const error = await response.json();
                errorMessage = error.detail || error.error || errorMessage;
            } catch (e) {
                const text = await response.text();
                errorMessage = text || `Server error (${response.status})`;
            }
            
            // More specific error messages
            if (response.status === 413) {
                errorMessage = 'File too large. Maximum size is 5 MB.';
            } else if (response.status === 415) {
                errorMessage = 'Unsupported file type. Please upload JPG, PNG, or PDF.';
            } else if (response.status === 401) {
                errorMessage = 'Authentication required. Please sign in again.';
            } else if (response.status >= 500) {
                errorMessage = 'Server error. Please try again later.';
            }
            
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('success', 'Document processed successfully!', uploadStatus);
            if (typeof showToast !== 'undefined') {
                showToast('success', 'Document processed successfully!');
            }
            displayTravelInfo(data.travel_info, travelInfo, resultsSection);
            
            if (data.calendar_event_id) {
                showCalendarStatus('success', 'Event added to calendar successfully!', calendarStatus);
                if (typeof showToast !== 'undefined') {
                    showToast('success', 'Event added to calendar!');
                }
            } else {
                showCalendarStatus('error', 'Could not add event to calendar. Please check your Google Calendar credentials.', calendarStatus);
            }
        } else {
            const errorMsg = data.message || 'Could not extract travel information from document. Please ensure the document contains clear travel details.';
            showStatus('error', errorMsg, uploadStatus);
            if (typeof showToast !== 'undefined') {
                showToast('error', errorMsg);
            }
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        if (error.message === 'Not authenticated') {
            window.location.href = '/login';
        } else {
            const errorMsg = error.message || 'An error occurred while processing the document. Please try again.';
            showStatus('error', errorMsg, uploadStatus);
            if (typeof showToast !== 'undefined') {
                showToast('error', errorMsg);
            }
        }
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Process Document';
        // Remove progress bar after a delay
        setTimeout(() => {
            if (progressBar && progressBar.parentElement) {
                progressBar.remove();
            }
        }, 1000);
    }
}

// Display travel information
function displayTravelInfo(info, travelInfo, resultsSection) {
    travelInfo.innerHTML = '';
    
    const fields = [
        { key: 'title', label: 'Title' },
        { key: 'start_date', label: 'Start Date' },
        { key: 'end_date', label: 'End Date' },
        { key: 'location', label: 'Location' },
        { key: 'description', label: 'Description' }
    ];
    
    const hasData = fields.some(field => info[field.key]);
    
    if (!hasData) {
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        emptyState.innerHTML = `
            <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <div class="empty-state-title">No information extracted</div>
            <div class="empty-state-description">The document was processed but no travel information could be extracted. Please ensure your document contains clear travel details.</div>
        `;
        travelInfo.appendChild(emptyState);
    } else {
        fields.forEach(field => {
            if (info[field.key]) {
                const item = document.createElement('div');
                item.className = 'info-item';
                item.innerHTML = `
                    <label>${field.label}</label>
                    <div class="value">${info[field.key]}</div>
                `;
                travelInfo.appendChild(item);
            }
        });
    }
    
    resultsSection.style.display = 'block';
}

// Show status message
function showStatus(type, message, uploadStatus) {
    // Support both new airportr style (status-message) and legacy (upload-status)
    const isStatusMessage = uploadStatus.classList.contains('status-message') || 
                           uploadStatus.id === 'uploadStatus' || 
                           uploadStatus.id === 'emailStatus' ||
                           uploadStatus.id === 'calendarTestResult' ||
                           uploadStatus.id === 'geminiTestResult';
    
    if (isStatusMessage) {
        uploadStatus.className = `status-message ${type}`;
    } else {
        uploadStatus.className = `upload-status ${type}`;
    }
    uploadStatus.textContent = message;
    uploadStatus.style.display = 'block';
}

// Show calendar status
function showCalendarStatus(type, message, calendarStatus) {
    // Support both new airportr style and legacy
    const isAirportr = calendarStatus.classList.contains('calendar-status-airportr');
    if (isAirportr) {
        calendarStatus.className = `calendar-status-airportr ${type}`;
    } else {
        calendarStatus.className = `calendar-status ${type}`;
    }
    calendarStatus.textContent = message;
}
