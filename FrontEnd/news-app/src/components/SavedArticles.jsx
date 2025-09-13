import React, { useState, useEffect } from 'react';
import NewsCard from './NewsCard';
import authApiService from '../services/authApi';

const SavedArticles = ({ user, onClose, categoryColors, onArticleClick }) => {
  const [savedArticles, setSavedArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredArticles, setFilteredArticles] = useState([]);

  useEffect(() => {
    // Clear previous user's data and load new user's data
    setSavedArticles([]);
    setFilteredArticles([]);
    setSearchTerm('');
    
    if (user) {
      loadSavedArticles();
    }
  }, [user]);

  useEffect(() => {
    // Filter saved articles based on search
    if (searchTerm.trim()) {
      const filtered = savedArticles.filter(article =>
        article.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.sourceName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.primaryCategory?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredArticles(filtered);
    } else {
      setFilteredArticles(savedArticles);
    }
  }, [savedArticles, searchTerm]);

  const loadSavedArticles = async () => {
    setLoading(true);
    try {
      // Check if user is authenticated
      if (!authApiService.utils.isAuthenticated()) {
        setSavedArticles([]);
        setFilteredArticles([]);
        return;
      }

      // Get saved articles from API
      const response = await authApiService.savedArticles.getSavedArticles(0, 100);
      
      if (response.success) {
        // Handle different possible response formats
        let articles;
        if (Array.isArray(response.data)) {
          // If response.data is directly an array of articles
          articles = response.data.map(item => {
            // Check if item has article property or is the article itself
            if (item.article) {
              return {
                ...item.article,
                savedAt: item.saved_at,
                notes: item.notes
              };
            } else {
              // Item is the article itself
              return {
                ...item,
                savedAt: item.saved_at,
                notes: item.notes
              };
            }
          });
        } else {
          articles = [];
        }
        
        setSavedArticles(articles);
        setFilteredArticles(articles);
      } else {
        throw new Error(response.error?.message || 'Failed to load saved articles');
      }
    } catch (error) {
      console.error('Error loading saved articles:', error);
      
      // Fallback to localStorage
      try {
        const savedData = localStorage.getItem(`savedArticles_${user.id}`);
        if (savedData) {
          const articles = JSON.parse(savedData);
          setSavedArticles(articles);
          setFilteredArticles(articles);
        }
      } catch (fallbackError) {
        console.error('Fallback load also failed:', fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveArticle = async (articleId) => {
    try {
      // Remove from API
      const response = await authApiService.savedArticles.removeSavedArticle(articleId);
      
      if (response.success) {
        // Update local state
        const updatedArticles = savedArticles.filter(article => article.id !== articleId);
        setSavedArticles(updatedArticles);
        setFilteredArticles(updatedArticles.filter(article =>
          !searchTerm.trim() || 
          article.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          article.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          article.sourceName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          article.primaryCategory?.toLowerCase().includes(searchTerm.toLowerCase())
        ));
        
        console.log('Article removed from saved articles');
      } else {
        throw new Error(response.error?.message || 'Failed to remove article');
      }
    } catch (error) {
      console.error('Error removing saved article:', error);
      
      // Fallback to localStorage
      const updatedArticles = savedArticles.filter(article => article.id !== articleId);
      setSavedArticles(updatedArticles);
      setFilteredArticles(updatedArticles.filter(article =>
        !searchTerm.trim() || 
        article.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.sourceName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        article.primaryCategory?.toLowerCase().includes(searchTerm.toLowerCase())
      ));
      
      try {
        localStorage.setItem(`savedArticles_${user.id}`, JSON.stringify(updatedArticles));
      } catch (storageError) {
        console.error('Error updating localStorage:', storageError);
      }
      
      alert('Failed to remove article from server, but removed locally.');
    }
  };

  const clearAllSaved = async () => {
    if (window.confirm('Are you sure you want to remove all saved articles?')) {
      try {
        // Remove all articles from API (we'll need to remove them one by one)
        const removePromises = savedArticles.map(article => 
          authApiService.savedArticles.removeSavedArticle(article.id)
        );
        
        await Promise.all(removePromises);
        
        // Clear local state
        setSavedArticles([]);
        setFilteredArticles([]);
        
        console.log('All saved articles removed successfully');
      } catch (error) {
        console.error('Error clearing all saved articles:', error);
        
        // Fallback: clear locally
        setSavedArticles([]);
        setFilteredArticles([]);
        localStorage.removeItem(`savedArticles_${user.id}`);
        
        alert('Failed to clear all articles from server, but cleared locally.');
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex justify-center items-start p-4 overflow-y-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-6xl w-full my-8">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Saved Articles
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {savedArticles.length} article{savedArticles.length !== 1 ? 's' : ''} saved
              </p>
            </div>
            <button 
              onClick={onClose}
              className="text-gray-500 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white text-2xl"
            >
              &times;
            </button>
          </div>

          {/* Search and Actions */}
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search saved articles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Clear All Button */}
            {savedArticles.length > 0 && (
              <button
                onClick={clearAllSaved}
                className="px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-sm font-medium"
              >
                Clear All
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600 dark:text-gray-400">Loading saved articles...</span>
            </div>
          ) : filteredArticles.length === 0 ? (
            <div className="text-center py-12">
              {savedArticles.length === 0 ? (
                <div>
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No saved articles yet
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    Start saving articles by clicking the bookmark icon on any article.
                  </p>
                </div>
              ) : (
                <div>
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No articles found
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    No saved articles match your search "{searchTerm}".
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredArticles.map((article) => (
                <div key={article.id} className="relative">
                  {/* Remove Button */}
                  <button
                    onClick={() => handleRemoveArticle(article.id)}
                    className="absolute top-2 right-2 z-10 p-1 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-full hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors"
                    title="Remove from saved"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  
                  {/* Article Card */}
                  <NewsCard
                    article={article}
                    categoryColor={categoryColors[article.primaryCategory || article.primary_category] || 'bg-gray-100 text-gray-800'}
                    onSummaryClick={onArticleClick}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SavedArticles;