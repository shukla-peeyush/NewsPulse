// API Service Layer for NewsPulse
// Base configuration and utility functions for API calls

const API_BASE_URL = 'http://localhost:8000';

// API Response wrapper for consistent error handling
class ApiResponse {
  constructor(data, error = null, status = 200) {
    this.data = data;
    this.error = error;
    this.status = status;
    this.success = !error;
  }
}

// Base API client with error handling
class ApiClient {
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
      
      // Handle different response types
      let data;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        return new ApiResponse(null, {
          message: data.detail || data.message || `HTTP ${response.status}: ${response.statusText}`,
          status: response.status,
          details: data
        }, response.status);
      }

      return new ApiResponse(data, null, response.status);
    } catch (error) {
      return new ApiResponse(null, {
        message: error.message || 'Network error occurred',
        status: 0,
        details: error
      }, 0);
    }
  }

  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Create singleton instance
const apiClient = new ApiClient();

// General Information APIs
export const generalApi = {
  // GET / - API welcome and basic information
  async getInfo() {
    return apiClient.get('/');
  },

  // GET /health - System health check and database statistics
  async getHealth() {
    return apiClient.get('/health');
  }
};

// Articles Management APIs
export const articlesApi = {
  // GET /articles - Get paginated list of articles with filtering
  async getArticles(params = {}) {
    const {
      skip = 0,
      limit = 100,
      min_relevance_score,
      category,
      source_id,
      processed_only
    } = params;

    const queryParams = { skip, limit };
    
    if (min_relevance_score !== undefined) queryParams.min_relevance_score = min_relevance_score;
    if (category) queryParams.category = category;
    if (source_id) queryParams.source_id = source_id;
    if (processed_only !== undefined) queryParams.processed_only = processed_only;

    return apiClient.get('/articles', queryParams);
  },

  // GET /articles/{article_id} - Get specific article by UUID
  async getArticleById(articleId) {
    return apiClient.get(`/articles/${articleId}`);
  }
};

// News Sources APIs
export const sourcesApi = {
  // GET /sources - List all configured news sources
  async getSources() {
    return apiClient.get('/sources');
  },

  // GET /sources/{source_id}/articles - Get articles from specific news source
  async getSourceArticles(sourceId, params = {}) {
    const { skip = 0, limit = 100 } = params;
    return apiClient.get(`/sources/${sourceId}/articles`, { skip, limit });
  }
};

// Analytics & Statistics APIs
export const analyticsApi = {
  // GET /categories - Get article categories with article counts
  async getCategories() {
    return apiClient.get('/categories');
  },

  // GET /stats - Platform statistics and metrics
  async getStats() {
    return apiClient.get('/stats');
  }
};

// Manual Operations APIs
export const operationsApi = {
  // POST /scrape - Manually trigger RSS feed scraping
  async triggerScraping() {
    return apiClient.post('/scrape');
  },

  // GET /scraping-sessions - Get recent scraping session history
  async getScrapingSessions() {
    return apiClient.get('/scraping-sessions');
  }
};

// Data transformation utilities to map API responses to frontend format
export const dataMappers = {
  // Map API article to frontend article format
  mapArticle(apiArticle) {
    return {
      id: apiArticle.id,
      title: apiArticle.title,
      url: apiArticle.url || apiArticle.link, // Handle both field names
      summary: apiArticle.summary,
      content: apiArticle.content,
      publishedDate: apiArticle.published_date,
      sourceName: apiArticle.source_name,
      relevanceScore: apiArticle.relevance_score,
      primaryCategory: apiArticle.primary_category,
      confidenceLevel: apiArticle.confidence_level,
      // Map to existing frontend fields for compatibility
      source: apiArticle.source_name,
      category: apiArticle.primary_category,
      date: apiArticle.published_date
    };
  },

  // Map API source to frontend format
  mapSource(apiSource) {
    return {
      id: apiSource.id,
      name: apiSource.name,
      rssUrl: apiSource.rss_url,
      region: apiSource.region,
      enabled: apiSource.enabled
    };
  },

  // Map API categories to frontend format
  mapCategories(apiCategories) {
    if (apiCategories.categories) {
      return apiCategories.categories.map(cat => ({
        name: cat.name,
        count: cat.count
      }));
    }
    return [];
  }
};

// Utility functions for common operations
export const apiUtils = {

  // Get all articles with client-side search and filtering
  async searchArticles(searchTerm = '', category = '', limit = 100) {
    const params = { limit };
    if (category && category !== 'ALL') {
      params.category = category.toLowerCase();
    }

    const response = await articlesApi.getArticles(params);
    
    if (!response.success) {
      return response;
    }

    let articles = response.data.map(dataMappers.mapArticle);

    // Client-side search if search term provided
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      articles = articles.filter(article => 
        article.title?.toLowerCase().includes(searchLower) ||
        article.summary?.toLowerCase().includes(searchLower) ||
        article.sourceName?.toLowerCase().includes(searchLower) ||
        article.primaryCategory?.toLowerCase().includes(searchLower)
      );
    }

    return new ApiResponse(articles);
  },

  // Get unique categories from articles
  async getAvailableCategories() {
    const response = await analyticsApi.getCategories();
    if (response.success) {
      return new ApiResponse(dataMappers.mapCategories(response.data));
    }
    
    // Fallback: get categories from articles if analytics endpoint fails
    const articlesResponse = await articlesApi.getArticles({ limit: 1000 });
    if (articlesResponse.success) {
      const categories = [...new Set(
        articlesResponse.data
          .map(article => article.primary_category)
          .filter(Boolean)
      )].map(name => ({ name, count: 0 }));
      
      return new ApiResponse(categories);
    }
    
    return response;
  }
};

// Export the API client for direct use if needed
export { apiClient };

// Default export with all APIs
export default {
  general: generalApi,
  articles: articlesApi,
  sources: sourcesApi,
  analytics: analyticsApi,
  operations: operationsApi,
  utils: apiUtils,
  mappers: dataMappers
};