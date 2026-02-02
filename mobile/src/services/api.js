import AsyncStorage from '@react-native-async-storage/async-storage';

// Backend API URL
const API_BASE = 'https://tickets.gmojsoski.com';

export const apiService = {
  async getAuthToken() {
    return await AsyncStorage.getItem('auth_token');
  },

  async setAuthToken(token) {
    await AsyncStorage.setItem('auth_token', token);
  },

  async removeAuthToken() {
    await AsyncStorage.removeItem('auth_token');
  },

  async authenticatedFetch(url, options = {}) {
    const token = await this.getAuthToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      await this.removeAuthToken();
      throw new Error('Not authenticated');
    }

    return response;
  },

  async login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    await this.setAuthToken(data.access_token);
    return data;
  },

  async logout() {
    await this.removeAuthToken();
  },

  async uploadDocument(fileUri, fileName, fileType) {
    const token = await this.getAuthToken();
    
    const formData = new FormData();
    formData.append('file', {
      uri: fileUri,
      type: fileType || 'image/jpeg',
      name: fileName || 'document.jpg',
    } as any);

    const response = await fetch(`${API_BASE}/api/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Don't set Content-Type, let fetch set it with boundary
      },
      body: formData,
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

    return await response.json();
  },

  async testCalendar() {
    const response = await this.authenticatedFetch('/api/calendar/test');
    return await response.json();
  },

  async testGemini() {
    const response = await this.authenticatedFetch('/api/test/gemini');
    return await response.json();
  },

  async testEmail() {
    const response = await this.authenticatedFetch('/api/email/test', {
      method: 'POST',
    });
    return await response.json();
  },

  async checkEmails() {
    const response = await this.authenticatedFetch('/api/email/check', {
      method: 'POST',
    });
    return await response.json();
  },
};
