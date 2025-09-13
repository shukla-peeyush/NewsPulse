// Authentication API Service
const API_BASE_URL = 'http://127.0.0.1:8002';

// API Response wrapper for consistent error handling
class AuthApiResponse {
  constructor(data, error = null, status = 200) {
    this.data = data;
    this.error = error;
    this.status = status;
    this.success = !error;
  }
}

// Authentication API client
class AuthApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      let data;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        return new AuthApiResponse(null, {
          message: data.detail || data.message || `HTTP ${response.status}: ${response.statusText}`,
          status: response.status,
          details: data
        }, response.status);
      }

      return new AuthApiResponse(data, null, response.status);
    } catch (error) {
      return new AuthApiResponse(null, {
        message: error.message || 'Network error occurred',
        status: 0,
        details: error
      }, 0);
    }
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async get(endpoint, headers = {}) {
    return this.request(endpoint, {
      method: 'GET',
      headers
    });
  }

  async put(endpoint, data = {}, headers = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    });
  }

  async delete(endpoint, headers = {}) {
    return this.request(endpoint, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    });
  }
}

// Create singleton instance
const authApiClient = new AuthApiClient();

// Helper function to get auth headers
export const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem('authToken');
};

// Get current user info from token (you might want to decode JWT or call user info endpoint)
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  }
  return null;
};

// Authentication APIs
export const authApi = {
  // POST /auth/register
  async register(userData) {
    const response = await authApiClient.post('/auth/register', {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      full_name: userData.fullName
    });

    if (response.success) {
      // Create enhanced user object for registration
      const enhancedUser = {
        ...response.data,
        id: userData.username,
        firstName: userData.fullName.split(' ')[0] || userData.username,
        lastName: userData.fullName.split(' ').slice(1).join(' ') || '',
        fullName: userData.fullName,
        username: userData.username,
        email: userData.email
      };
      
      // Store enhanced user data
      localStorage.setItem('user', JSON.stringify(enhancedUser));
      localStorage.setItem('isAuthenticated', 'true');
      
      // Return enhanced user data
      return new AuthApiResponse(enhancedUser, null, response.status);
    }

    return response;
  },

  // POST /auth/login
  async login(credentials) {
    const response = await authApiClient.post('/auth/login', {
      username: credentials.username,
      password: credentials.password
    });

    if (response.success) {
      const { access_token, token_type } = response.data;
      
      // Store token
      localStorage.setItem('authToken', access_token);
      localStorage.setItem('tokenType', token_type);
      localStorage.setItem('isAuthenticated', 'true');

      // Create user object with available data
      const user = {
        id: credentials.username, // Use username as ID for now
        username: credentials.username,
        email: credentials.email || '',
        firstName: credentials.username, // Use username as display name
        lastName: '',
        fullName: credentials.username,
        token: access_token
      };
      
      localStorage.setItem('user', JSON.stringify(user));
      
      return new AuthApiResponse(user, null, response.status);
    }

    return response;
  },

  // Logout
  async logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('tokenType');
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
    
    return new AuthApiResponse({ message: 'Logged out successfully' });
  },

  // Get user profile (if you have this endpoint)
  async getUserProfile() {
    const response = await authApiClient.get('/auth/me', getAuthHeaders());
    return response;
  }
};

// Saved Articles APIs
export const savedArticlesApi = {
  // POST /users/saved-articles
  async saveArticle(articleId, notes = '') {
    const headers = getAuthHeaders();
    const response = await authApiClient.request('/users/saved-articles', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        article_id: articleId,
        notes: notes
      })
    });

    return response;
  },

  // GET /users/saved-articles
  async getSavedArticles(skip = 0, limit = 20) {
    const headers = getAuthHeaders();
    const response = await authApiClient.request(
      `/users/saved-articles?skip=${skip}&limit=${limit}`,
      {
        method: 'GET',
        headers
      }
    );

    return response;
  },

  // PUT /users/saved-articles/{article_id}
  async updateArticleNotes(articleId, notes) {
    const headers = getAuthHeaders();
    const response = await authApiClient.request(
      `/users/saved-articles/${articleId}`,
      {
        method: 'PUT',
        headers,
        body: JSON.stringify({ notes: notes })
      }
    );

    return response;
  },

  // DELETE /users/saved-articles/{article_id}
  async removeSavedArticle(articleId) {
    const headers = getAuthHeaders();
    const response = await authApiClient.request(
      `/users/saved-articles/${articleId}`,
      {
        method: 'DELETE',
        headers
      }
    );

    return response;
  },

  // GET /users/saved-articles/count
  async getSavedArticlesCount() {
    const headers = getAuthHeaders();
    const response = await authApiClient.request(
      '/users/saved-articles/count',
      {
        method: 'GET',
        headers
      }
    );

    return response;
  }
};

// Export the API client for direct use if needed
export { authApiClient };

// Default export with all APIs
export default {
  auth: authApi,
  savedArticles: savedArticlesApi,
  utils: {
    getAuthHeaders,
    isAuthenticated,
    getCurrentUser
  }
};