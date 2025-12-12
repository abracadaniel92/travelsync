/**
 * Test functionality
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Test Calendar button
    const testCalendarBtn = document.getElementById('testCalendarBtn');
    if (testCalendarBtn) {
        testCalendarBtn.addEventListener('click', async () => {
            const btn = document.getElementById('testCalendarBtn');
            const resultDiv = document.getElementById('calendarTestResult');
            
            btn.disabled = true;
            btn.textContent = 'Testing...';
            resultDiv.style.display = 'none';
            
            try {
                if (typeof authenticatedFetch === 'undefined') {
                    throw new Error('authenticatedFetch function not found. Make sure auth.js is loaded.');
                }
                
                const response = await authenticatedFetch(`${window.location.origin}/api/calendar/test`);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Server error: ${response.status} - ${errorText}`);
                }
                
                const data = await response.json();
                
                console.log('Calendar test response:', data); // Debug log
                
                resultDiv.style.display = 'block';
                
                // Check if authentication is needed (before checking success)
                // Check for needs_auth flag OR error message containing authentication
                const needsAuth = data.needs_auth === true || 
                                (data.error && typeof data.error === 'string' && data.error.toLowerCase().includes('authentication')) ||
                                (data.details && typeof data.details === 'string' && data.details.toLowerCase().includes('authentication'));
                
                if (!data.success && needsAuth) {
                    resultDiv.className = 'upload-status error';
                    resultDiv.innerHTML = `
                        <strong>⚠ Google Calendar authentication required</strong><br>
                        ${data.details ? `<small>${data.details}</small><br>` : ''}
                        <button id="startAuthBtn" class="btn btn-secondary" style="margin-top: 0.5rem;">Start Authentication</button>
                        <div id="authFlowDiv" style="margin-top: 1rem; display: none;">
                            <p><strong>Step 1:</strong> Visit the URL below to authorize:</p>
                            <a id="authUrlLink" href="#" target="_blank" style="word-break: break-all; color: #3b82f6; display: block; margin: 0.5rem 0;">Loading...</a>
                            <p style="margin-top: 1rem;"><strong>Step 2:</strong> After authorizing, paste the code here:</p>
                            <input type="text" id="authCodeInput" placeholder="Paste authorization code here" style="width: 100%; padding: 0.5rem; margin-top: 0.5rem; border: 1px solid #ccc; border-radius: 4px;">
                            <button id="completeAuthBtn" class="btn btn-primary" style="margin-top: 0.5rem;">Complete Authentication</button>
                        </div>
                    `;
                    
                    // Add event listeners for OAuth flow
                    const startAuthBtn = document.getElementById('startAuthBtn');
                    if (startAuthBtn) {
                        startAuthBtn.addEventListener('click', async () => {
                            try {
                                startAuthBtn.disabled = true;
                                startAuthBtn.textContent = 'Loading...';
                                const authResponse = await authenticatedFetch(`${window.location.origin}/api/calendar/auth/start`);
                                if (!authResponse.ok) {
                                    throw new Error(`Server error: ${authResponse.status}`);
                                }
                                const authData = await authResponse.json();
                                
                                document.getElementById('authUrlLink').href = authData.authorization_url;
                                document.getElementById('authUrlLink').textContent = authData.authorization_url;
                                document.getElementById('authFlowDiv').style.display = 'block';
                                startAuthBtn.textContent = 'Start Authentication';
                                startAuthBtn.disabled = false;
                            } catch (err) {
                                alert('Failed to start authentication: ' + err.message);
                                startAuthBtn.textContent = 'Start Authentication';
                                startAuthBtn.disabled = false;
                            }
                        });
                    }
                    
                    const completeAuthBtn = document.getElementById('completeAuthBtn');
                    if (completeAuthBtn) {
                        completeAuthBtn.addEventListener('click', async () => {
                            const code = document.getElementById('authCodeInput').value.trim();
                            if (!code) {
                                alert('Please enter the authorization code');
                                return;
                            }
                            
                            try {
                                completeAuthBtn.disabled = true;
                                completeAuthBtn.textContent = 'Completing...';
                                const formData = new FormData();
                                formData.append('code', code);
                                
                                const completeResponse = await authenticatedFetch(`${window.location.origin}/api/calendar/auth/complete`, {
                                    method: 'POST',
                                    body: formData
                                });
                                
                                if (!completeResponse.ok) {
                                    const errorText = await completeResponse.text();
                                    throw new Error(errorText);
                                }
                                
                                const completeData = await completeResponse.json();
                                
                                if (completeData.success) {
                                    resultDiv.className = 'upload-status success';
                                    resultDiv.innerHTML = '<strong>✓ Authentication completed! Testing connection...</strong>';
                                    // Auto-test after successful auth
                                    setTimeout(() => testCalendarBtn.click(), 1000);
                                } else {
                                    alert('Authentication failed: ' + (completeData.error || 'Unknown error'));
                                    completeAuthBtn.textContent = 'Complete Authentication';
                                    completeAuthBtn.disabled = false;
                                }
                            } catch (err) {
                                alert('Failed to complete authentication: ' + err.message);
                                completeAuthBtn.textContent = 'Complete Authentication';
                                completeAuthBtn.disabled = false;
                            }
                        });
                    }
                    return; // Exit early, don't process success case
                }
                
                if (data.success) {
                    resultDiv.className = 'upload-status success';
                    resultDiv.innerHTML = `
                        <strong>✓ Google Calendar is connected!</strong><br>
                        Calendar: ${data.calendar_name || 'Primary'}<br>
                        Timezone: ${data.timezone || 'Unknown'}<br>
                        Total calendars: ${data.total_calendars || 0}
                    `;
                } else {
                    resultDiv.className = 'upload-status error';
                    // Check again if this is an authentication error (fallback)
                    const errorText = (data.error || '') + ' ' + (data.details || '');
                    if (errorText.toLowerCase().includes('authentication') || errorText.toLowerCase().includes('auth/start')) {
                        // Show authentication button
                        resultDiv.innerHTML = `
                            <strong>⚠ Google Calendar authentication required</strong><br>
                            ${data.details ? `<small>${data.details}</small><br>` : ''}
                            <button id="startAuthBtn" class="btn btn-secondary" style="margin-top: 0.5rem;">Start Authentication</button>
                            <div id="authFlowDiv" style="margin-top: 1rem; display: none;">
                                <p><strong>Step 1:</strong> Visit the URL below to authorize:</p>
                                <a id="authUrlLink" href="#" target="_blank" style="word-break: break-all; color: #3b82f6; display: block; margin: 0.5rem 0;">Loading...</a>
                                <p style="margin-top: 1rem;"><strong>Step 2:</strong> After authorizing, paste the code here:</p>
                                <input type="text" id="authCodeInput" placeholder="Paste authorization code here" style="width: 100%; padding: 0.5rem; margin-top: 0.5rem; border: 1px solid #ccc; border-radius: 4px;">
                                <button id="completeAuthBtn" class="btn btn-primary" style="margin-top: 0.5rem;">Complete Authentication</button>
                            </div>
                        `;
                        
                        // Add event listeners for OAuth flow
                        const startAuthBtn = document.getElementById('startAuthBtn');
                        if (startAuthBtn) {
                            startAuthBtn.addEventListener('click', async () => {
                                try {
                                    startAuthBtn.disabled = true;
                                    startAuthBtn.textContent = 'Loading...';
                                    const authResponse = await authenticatedFetch(`${window.location.origin}/api/calendar/auth/start`);
                                    if (!authResponse.ok) {
                                        throw new Error(`Server error: ${authResponse.status}`);
                                    }
                                    const authData = await authResponse.json();
                                    
                                    document.getElementById('authUrlLink').href = authData.authorization_url;
                                    document.getElementById('authUrlLink').textContent = authData.authorization_url;
                                    document.getElementById('authFlowDiv').style.display = 'block';
                                    startAuthBtn.textContent = 'Start Authentication';
                                    startAuthBtn.disabled = false;
                                } catch (err) {
                                    alert('Failed to start authentication: ' + err.message);
                                    startAuthBtn.textContent = 'Start Authentication';
                                    startAuthBtn.disabled = false;
                                }
                            });
                        }
                        
                        const completeAuthBtn = document.getElementById('completeAuthBtn');
                        if (completeAuthBtn) {
                            completeAuthBtn.addEventListener('click', async () => {
                                const code = document.getElementById('authCodeInput').value.trim();
                                if (!code) {
                                    alert('Please enter the authorization code');
                                    return;
                                }
                                
                                try {
                                    completeAuthBtn.disabled = true;
                                    completeAuthBtn.textContent = 'Completing...';
                                    const formData = new FormData();
                                    formData.append('code', code);
                                    
                                    const completeResponse = await authenticatedFetch(`${window.location.origin}/api/calendar/auth/complete`, {
                                        method: 'POST',
                                        body: formData
                                    });
                                    
                                    if (!completeResponse.ok) {
                                        const errorText = await completeResponse.text();
                                        throw new Error(errorText);
                                    }
                                    
                                    const completeData = await completeResponse.json();
                                    
                                    if (completeData.success) {
                                        resultDiv.className = 'upload-status success';
                                        resultDiv.innerHTML = '<strong>✓ Authentication completed! Testing connection...</strong>';
                                        // Auto-test after successful auth
                                        setTimeout(() => testCalendarBtn.click(), 1000);
                                    } else {
                                        alert('Authentication failed: ' + (completeData.error || 'Unknown error'));
                                        completeAuthBtn.textContent = 'Complete Authentication';
                                        completeAuthBtn.disabled = false;
                                    }
                                } catch (err) {
                                    alert('Failed to complete authentication: ' + err.message);
                                    completeAuthBtn.textContent = 'Complete Authentication';
                                    completeAuthBtn.disabled = false;
                                }
                            });
                        }
                    } else {
                        resultDiv.innerHTML = `
                            <strong>✗ Error:</strong><br>
                            ${data.error || 'Unknown error'}<br>
                            ${data.details ? `<small>${data.details}</small>` : ''}
                        `;
                    }
                }
            } catch (error) {
                console.error('Calendar test error:', error);
                resultDiv.style.display = 'block';
                resultDiv.className = 'upload-status error';
                
                // Check if error message contains authentication-related text
                const errorMsg = error.message || '';
                const isAuthError = errorMsg.toLowerCase().includes('authentication') || 
                                  errorMsg.toLowerCase().includes('auth/start') ||
                                  errorMsg.toLowerCase().includes('token.pickle');
                
                if (error.message === 'Not authenticated') {
                    resultDiv.innerHTML = '<strong>Error:</strong> Not logged in. Please refresh and login again.';
                } else if (isAuthError) {
                    // Show OAuth authentication option
                    resultDiv.innerHTML = `
                        <strong>⚠ Google Calendar authentication required</strong><br>
                        <button id="startAuthBtn" class="btn btn-secondary" style="margin-top: 0.5rem;">Start Authentication</button>
                        <div id="authFlowDiv" style="margin-top: 1rem; display: none;">
                            <p><strong>Step 1:</strong> Visit the URL below to authorize:</p>
                            <a id="authUrlLink" href="#" target="_blank" style="word-break: break-all; color: #3b82f6;">Loading...</a>
                            <p style="margin-top: 1rem;"><strong>Step 2:</strong> After authorizing, paste the code here:</p>
                            <input type="text" id="authCodeInput" placeholder="Paste authorization code here" style="width: 100%; padding: 0.5rem; margin-top: 0.5rem; border: 1px solid #ccc; border-radius: 4px;">
                            <button id="completeAuthBtn" class="btn btn-primary" style="margin-top: 0.5rem;">Complete Authentication</button>
                        </div>
                    `;
                    
                    // Add event listeners for OAuth flow
                    const startAuthBtn = document.getElementById('startAuthBtn');
                    if (startAuthBtn) {
                        startAuthBtn.addEventListener('click', async () => {
                            try {
                                const authResponse = await authenticatedFetch(`${window.location.origin}/api/calendar/auth/start`);
                                const authData = await authResponse.json();
                                
                                document.getElementById('authUrlLink').href = authData.authorization_url;
                                document.getElementById('authUrlLink').textContent = authData.authorization_url;
                                document.getElementById('authFlowDiv').style.display = 'block';
                            } catch (err) {
                                alert('Failed to start authentication: ' + err.message);
                            }
                        });
                    }
                    
                    const completeAuthBtn = document.getElementById('completeAuthBtn');
                    if (completeAuthBtn) {
                        completeAuthBtn.addEventListener('click', async () => {
                            const code = document.getElementById('authCodeInput').value.trim();
                            if (!code) {
                                alert('Please enter the authorization code');
                                return;
                            }
                            
                            try {
                                const formData = new FormData();
                                formData.append('code', code);
                                
                                const completeResponse = await authenticatedFetch(`${window.location.origin}/api/calendar/auth/complete`, {
                                    method: 'POST',
                                    body: formData
                                });
                                
                                const completeData = await completeResponse.json();
                                
                                if (completeData.success) {
                                    resultDiv.className = 'upload-status success';
                                    resultDiv.innerHTML = '<strong>✓ Authentication completed! Please test the connection again.</strong>';
                                    // Auto-test after successful auth
                                    setTimeout(() => testCalendarBtn.click(), 1000);
                                } else {
                                    alert('Authentication failed: ' + (completeData.error || 'Unknown error'));
                                }
                            } catch (err) {
                                alert('Failed to complete authentication: ' + err.message);
                            }
                        });
                    }
                } else {
                    resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
                }
            } finally {
                btn.disabled = false;
                btn.textContent = 'Test Calendar Connection';
            }
        });
    }
    
    // Test Gemini button
    const testBtn = document.getElementById('testGeminiBtn');
    if (testBtn) {
        console.log('Test button found, adding event listener');
        testBtn.addEventListener('click', async () => {
            console.log('Test button clicked');
            const btn = document.getElementById('testGeminiBtn');
            const resultDiv = document.getElementById('geminiTestResult');
            
            btn.disabled = true;
            btn.textContent = 'Testing...';
            resultDiv.style.display = 'none';
            
            try {
                console.log('Calling authenticatedFetch...');
                
                // Check if authenticatedFetch is available
                if (typeof authenticatedFetch === 'undefined') {
                    throw new Error('authenticatedFetch function not found. Make sure auth.js is loaded.');
                }
                
                const response = await authenticatedFetch(`${window.location.origin}/api/test/gemini`);
                console.log('Response received:', response.status);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Server error: ${response.status} - ${errorText}`);
                }
                
                const data = await response.json();
                console.log('Data received:', data);
                
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    resultDiv.className = 'upload-status success';
                    resultDiv.innerHTML = `
                        <strong>✓ Gemini API is working!</strong><br>
                        Response: ${data.response}
                    `;
                } else {
                    resultDiv.className = 'upload-status error';
                    resultDiv.innerHTML = `
                        <strong>✗ Error:</strong><br>
                        ${data.error || 'Unknown error'}
                    `;
                }
            } catch (error) {
                console.error('Test error:', error);
                resultDiv.style.display = 'block';
                resultDiv.className = 'upload-status error';
                
                if (error.message === 'Not authenticated') {
                    resultDiv.innerHTML = '<strong>Error:</strong> Not logged in. Please refresh and login again.';
                } else {
                    resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
                }
            } finally {
                btn.disabled = false;
                btn.textContent = 'Test Gemini Connection';
            }
        });
    } else {
        console.error('Test button not found!');
    }
});

