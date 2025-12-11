/**
 * Main application logic
 */

// Use API_BASE from auth.js if available, otherwise use window.location.origin directly
let selectedFile = null;

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
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

    // Remove file
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', () => {
            selectedFile = null;
            fileInput.value = '';
            fileInfo.style.display = 'none';
            uploadBtn.style.display = 'none';
            uploadStatus.style.display = 'none';
            resultsSection.style.display = 'none';
        });
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
        showStatus('error', 'Invalid file type. Please upload JPG, PNG, or PDF.', uploadStatus);
        return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showStatus('error', 'File size exceeds 5MB limit.', uploadStatus);
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'flex';
    uploadBtn.style.display = 'block';
    console.log('Upload button should now be visible');
    uploadStatus.style.display = 'none';
    resultsSection.style.display = 'none';
}

// Upload and process document
async function uploadAndProcess(file, uploadBtn, uploadStatus, resultsSection, travelInfo, calendarStatus) {
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner"></span>Processing...';
    showStatus('processing', 'Processing document with AI...', uploadStatus);
    resultsSection.style.display = 'none';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await authenticatedFetch(`${window.location.origin}/api/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            let errorMessage = 'Upload failed';
            try {
                const error = await response.json();
                errorMessage = error.detail || errorMessage;
            } catch (e) {
                const text = await response.text();
                errorMessage = text || `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('success', 'Document processed successfully!', uploadStatus);
            displayTravelInfo(data.travel_info, travelInfo, resultsSection);
            
            if (data.calendar_event_id) {
                showCalendarStatus('success', 'Event added to calendar successfully!', calendarStatus);
            } else {
                showCalendarStatus('error', 'Could not add event to calendar. Please check your Google Calendar credentials.', calendarStatus);
            }
        } else {
            showStatus('error', data.message || 'Could not extract travel information from document.', uploadStatus);
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        if (error.message === 'Not authenticated') {
            window.location.href = '/login';
        } else {
            showStatus('error', error.message || 'An error occurred while processing the document.', uploadStatus);
        }
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Process Document';
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
    
    resultsSection.style.display = 'block';
}

// Show status message
function showStatus(type, message, uploadStatus) {
    uploadStatus.className = `upload-status ${type}`;
    uploadStatus.textContent = message;
    uploadStatus.style.display = 'block';
}

// Show calendar status
function showCalendarStatus(type, message, calendarStatus) {
    calendarStatus.className = `calendar-status ${type}`;
    calendarStatus.textContent = message;
}
