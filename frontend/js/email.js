/**
 * Email forwarding functionality
 */

// Extract error message from API response (FastAPI returns detail, we use error)
function getEmailErrorMsg(data) {
    if (data?.error) return data.error;
    if (data?.detail) {
        if (typeof data.detail === 'string') return data.detail;
        if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
    }
    return 'Unknown error';
}

document.addEventListener('DOMContentLoaded', async function() {
    // Check if email is configured and show hint (only when logged in)
    const emailCard = document.querySelector('.connection-card');
    const emailStatusEl = document.getElementById('emailStatus');
    if (emailCard && emailStatusEl && typeof authenticatedFetch !== 'undefined' && localStorage.getItem('auth_token')) {
        try {
            const statusRes = await authenticatedFetch(`${window.location.origin}/api/email/status`);
            if (statusRes.ok) {
                const status = await statusRes.json();
                if (!status.configured && emailStatusEl) {
                    emailStatusEl.style.display = 'block';
                    emailStatusEl.className = 'connection-status';
                    emailStatusEl.style.background = 'var(--color-bg)';
                    emailStatusEl.style.border = '1px solid var(--color-border)';
                    emailStatusEl.innerHTML = '<strong>Email not configured</strong><br>Set EMAIL_ADDRESS and EMAIL_PASSWORD in your .env file to enable email forwarding. See docs/EMAIL_SETUP.md for details.';
                }
            }
        } catch (e) {
            // Ignore - user may not be logged in yet
        }
    }

    // Update connection status on load
    const emailStatus = localStorage.getItem('connection_email_status');
    if (emailStatus) {
        const button = document.getElementById('testEmailBtn');
        if (button) {
            const existingDot = button.querySelector('.status-dot');
            if (existingDot) {
                existingDot.remove();
            }
            const dot = document.createElement('span');
            dot.className = `status-dot ${emailStatus}`;
            button.insertBefore(dot, button.firstChild);
        }
    }
    const testEmailBtn = document.getElementById('testEmailBtn');
    const checkEmailBtn = document.getElementById('checkEmailBtn');
    const emailStatus = document.getElementById('emailStatus');
    const emailResults = document.getElementById('emailResults');
    
    // Test email connection
    if (testEmailBtn) {
        testEmailBtn.addEventListener('click', async () => {
            testEmailBtn.disabled = true;
            testEmailBtn.textContent = 'Testing...';
            emailStatus.style.display = 'none';
            emailResults.style.display = 'none';
            
            try {
                const response = await authenticatedFetch(`${window.location.origin}/api/email/test`, {
                    method: 'POST'
                });
                
                const data = await response.json().catch(() => ({}));
                
                emailStatus.style.display = 'block';
                
                if (response.ok && data.success) {
                    emailStatus.className = 'connection-status success';
                    emailStatus.innerHTML = `
                        <strong>✓ Email connection successful!</strong><br>
                        Email: ${data.email_address}<br>
                        Server: ${data.imap_server}<br>
                        Total emails in inbox: ${data.total_emails_in_inbox}
                        <div class="connection-timestamp">Last checked: ${new Date().toLocaleTimeString()}</div>
                    `;
                    if (typeof showToast !== 'undefined') {
                        showToast('success', 'Email connection successful!');
                    }
                    localStorage.setItem('connection_email_status', 'connected');
                    localStorage.setItem('connection_email_timestamp', new Date().toLocaleTimeString());
                    // Update status dot
                    const button = document.getElementById('testEmailBtn');
                    if (button) {
                        const existingDot = button.querySelector('.status-dot');
                        if (existingDot) {
                            existingDot.remove();
                        }
                        const dot = document.createElement('span');
                        dot.className = 'status-dot connected';
                        button.insertBefore(dot, button.firstChild);
                    }
                } else {
                    emailStatus.className = 'connection-status error';
                    const errorMsg = getEmailErrorMsg(data);
                    emailStatus.innerHTML = `<strong>✗ Connection failed:</strong><br>${errorMsg}`;
                    if (typeof showToast !== 'undefined') {
                        showToast('error', `Email connection failed: ${errorMsg}`);
                    }
                    localStorage.setItem('connection_email_status', 'error');
                    // Update status dot
                    const button = document.getElementById('testEmailBtn');
                    if (button) {
                        const existingDot = button.querySelector('.status-dot');
                        if (existingDot) {
                            existingDot.remove();
                        }
                        const dot = document.createElement('span');
                        dot.className = 'status-dot error';
                        button.insertBefore(dot, button.firstChild);
                    }
                }
            } catch (error) {
                console.error('Email test error:', error);
                emailStatus.style.display = 'block';
                emailStatus.className = 'connection-status error';
                
                if (error.message === 'Not authenticated') {
                    emailStatus.innerHTML = '<strong>Error:</strong> Not logged in. Please refresh and login again.';
                } else {
                    emailStatus.innerHTML = `<strong>Error:</strong> ${error.message}`;
                }
            } finally {
                testEmailBtn.disabled = false;
                testEmailBtn.textContent = 'Test Connection';
            }
        });
    }
    
    // Check and process emails
    if (checkEmailBtn) {
        checkEmailBtn.addEventListener('click', async () => {
            checkEmailBtn.disabled = true;
            checkEmailBtn.textContent = 'Checking...';
            emailStatus.style.display = 'none';
            emailResults.style.display = 'none';
            
            try {
                const response = await authenticatedFetch(`${window.location.origin}/api/email/check`, {
                    method: 'POST'
                });
                
                const data = await response.json().catch(() => ({}));
                
                emailStatus.style.display = 'block';
                
                if (response.ok && data.success) {
                    emailStatus.className = 'connection-status success';
                    emailStatus.innerHTML = `
                        <strong>✓ ${data.message}</strong><br>
                        Emails processed: ${data.emails_processed}<br>
                        Attachments processed: ${data.attachments_processed}<br>
                        Calendar events created: ${data.events_created}
                        <div class="connection-timestamp">Last checked: ${new Date().toLocaleTimeString()}</div>
                    `;
                    if (typeof showToast !== 'undefined') {
                        showToast('success', `${data.message} - ${data.events_created} event(s) created`);
                    }
                    
                    // Show detailed results if available
                    if (data.results && data.results.length > 0) {
                        emailResults.style.display = 'block';
                        emailResults.innerHTML = '<h3 style="margin-top: 1rem; font-size: 1rem;">Processing Details:</h3>';
                        
                        data.results.forEach((result, index) => {
                            const resultDiv = document.createElement('div');
                            resultDiv.style.cssText = 'margin-top: 0.75rem; padding: 1rem; background: var(--color-bg); border-radius: var(--radius-md); border: 1px solid var(--color-border);';
                            
                            const statusClass = result.errors && result.errors.length > 0 ? 'error' : 'success';
                            const statusIcon = result.errors && result.errors.length > 0 ? '✗' : '✓';
                            
                            resultDiv.innerHTML = `
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                    <div>
                                        <strong>${statusIcon} ${result.subject || 'No Subject'}</strong><br>
                                        <small style="color: var(--color-text-secondary);">From: ${result.sender}</small>
                                    </div>
                                    <span class="connection-status ${statusClass}" style="padding: 0.25rem 0.5rem; font-size: 0.85rem;">
                                        ${result.attachments_processed} processed
                                    </span>
                                </div>
                                ${result.errors && result.errors.length > 0 ? `
                                    <div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(239, 68, 68, 0.1); border-radius: var(--radius-sm);">
                                        <strong style="color: #ef4444;">Errors:</strong>
                                        <ul style="margin: 0.25rem 0 0 1.5rem; padding: 0;">
                                            ${result.errors.map(e => `<li style="color: #ef4444; font-size: 0.9rem;">${e}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                                ${result.events_created > 0 ? `
                                    <div style="margin-top: 0.5rem; color: #10b981; font-size: 0.9rem;">
                                        ✓ ${result.events_created} calendar event(s) created
                                    </div>
                                ` : ''}
                            `;
                            
                            emailResults.appendChild(resultDiv);
                        });
                    }
                } else {
                    emailStatus.className = 'connection-status error';
                    const errorMsg = getEmailErrorMsg(data);
                    emailStatus.innerHTML = `<strong>✗ Error:</strong><br>${errorMsg}`;
                    if (typeof showToast !== 'undefined') {
                        showToast('error', `Email processing failed: ${errorMsg}`);
                    }
                }
            } catch (error) {
                console.error('Email check error:', error);
                emailStatus.style.display = 'block';
                emailStatus.className = 'connection-status error';
                
                if (error.message === 'Not authenticated') {
                    emailStatus.innerHTML = '<strong>Error:</strong> Not logged in. Please refresh and login again.';
                } else {
                    emailStatus.innerHTML = `<strong>Error:</strong> ${error.message}`;
                }
            } finally {
                checkEmailBtn.disabled = false;
                checkEmailBtn.textContent = 'Check & Process Emails';
            }
        });
    }
});











