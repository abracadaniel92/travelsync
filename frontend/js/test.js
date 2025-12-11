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
                
                resultDiv.style.display = 'block';
                
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
                    resultDiv.innerHTML = `
                        <strong>✗ Error:</strong><br>
                        ${data.error || 'Unknown error'}<br>
                        ${data.details ? `<small>${data.details}</small>` : ''}
                    `;
                }
            } catch (error) {
                console.error('Calendar test error:', error);
                resultDiv.style.display = 'block';
                resultDiv.className = 'upload-status error';
                
                if (error.message === 'Not authenticated') {
                    resultDiv.innerHTML = '<strong>Error:</strong> Not logged in. Please refresh and login again.';
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

