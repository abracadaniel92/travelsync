/**
 * Authentication handling
 */

const API_BASE = window.location.origin;

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        // Redirect to login if not on login page
        if (!window.location.pathname.includes('login.html')) {
            window.location.href = '/login';
        }
        return false;
    }
    return true;
}

// Login function
async function login(username, password) {
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        if (!response.ok) {
            let errorMessage = 'Login failed';
            try {
                const error = await response.json();
                errorMessage = error.detail || errorMessage;
            } catch (e) {
                // If response is not JSON, get text
                const text = await response.text();
                errorMessage = text || `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        localStorage.setItem('auth_token', data.access_token);
        return true;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// Logout function
function logout() {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
}

// Get auth token
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// Make authenticated request
async function authenticatedFetch(url, options = {}) {
    const token = getAuthToken();
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    return fetch(url, {
        ...options,
        headers
    });
}

// Login form handler
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.style.display = 'none';
        
        try {
            await login(username, password);
            window.location.href = '/';
        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        }
    });
}

// Logout button handler
if (document.getElementById('logoutBtn')) {
    document.getElementById('logoutBtn').addEventListener('click', () => {
        logout();
    });
}

// Check auth on page load (except login page)
if (!window.location.pathname.includes('login.html')) {
    checkAuth();
}

