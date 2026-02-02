/**
 * Authentication handling
 */

const API_BASE = window.location.origin;

// Check if user is logged in
function checkAuth() {
    // Double-check we're not on login page before redirecting
    const pathname = window.location.pathname;
    const isLoginPage = pathname === '/login' || 
                       pathname === '/login/' || 
                       pathname.startsWith('/login?') ||
                       pathname.includes('login.html') ||
                       pathname.includes('/login.html');
    
    // Safety check: if somehow we're on login page, don't redirect
    if (isLoginPage) {
        return false;
    }
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
        // Only redirect if we're definitely NOT on login page
        window.location.href = '/login';
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
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // If token expired (401), clear it and redirect to login
    if (response.status === 401) {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
        throw new Error('Session expired. Please log in again.');
    }
    
    return response;
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
// Only run checkAuth if we're NOT on the login page
(function() {
    // Get current pathname
    const pathname = window.location.pathname;
    // Check if we're on login page - be very explicit
    const isLoginPage = pathname === '/login' || 
                       pathname === '/login/' || 
                       pathname.startsWith('/login?') ||
                       pathname.includes('login.html') ||
                       pathname.includes('/login.html');
    
    // NEVER run checkAuth on login page
    if (isLoginPage) {
        console.log('On login page, skipping auth check');
        return; // Exit early, don't run checkAuth
    }
    
    // Only run checkAuth if NOT on login page
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAuth);
    } else {
        checkAuth();
    }
})();

