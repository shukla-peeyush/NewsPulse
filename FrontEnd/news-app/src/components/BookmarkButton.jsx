import React, { useState, useEffect } from 'react';
import authApiService from '../services/authApi';

const BookmarkButton = ({ article, user, size = 'md' }) => {
  const [isSaved, setIsSaved] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Size variants
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  const buttonSizeClasses = {
    sm: 'p-1',
    md: 'p-2',
    lg: 'p-3'
  };

  useEffect(() => {
    // Reset state when user changes
    setIsSaved(false);
    setIsLoading(false);
    
    if (user && article) {
      checkIfSaved();
    }
  }, [user, article]);

  const checkIfSaved = async () => {
    try {
      // Check if user is authenticated
      if (!authApiService.utils.isAuthenticated()) {
        setIsSaved(false);
        return;
      }

      // Get saved articles from API
      const response = await authApiService.savedArticles.getSavedArticles();
      if (response.success) {
        const isArticleSaved = response.data.some(saved => saved.article_id === article.id);
        setIsSaved(isArticleSaved);
      }
    } catch (error) {
      console.error('Error checking saved status:', error);
      // Fallback to localStorage check
      const savedData = localStorage.getItem(`savedArticles_${user.id}`);
      if (savedData) {
        const savedArticles = JSON.parse(savedData);
        const isArticleSaved = savedArticles.some(saved => saved.id === article.id);
        setIsSaved(isArticleSaved);
      }
    }
  };

  const toggleSave = async () => {
    if (!user) {
      alert('Please sign in to save articles');
      return;
    }

    if (!authApiService.utils.isAuthenticated()) {
      alert('Please sign in to save articles');
      return;
    }

    setIsLoading(true);
    
    try {
      let response;
      
      if (isSaved) {
        // Remove from saved using API
        response = await authApiService.savedArticles.removeSavedArticle(article.id);
        if (response.success) {
          setIsSaved(false);
        } else {
          throw new Error(response.error?.message || 'Failed to remove article');
        }
      } else {
        // Add to saved using API
        response = await authApiService.savedArticles.saveArticle(article.id, '');
        if (response.success) {
          setIsSaved(true);
        } else {
          throw new Error(response.error?.message || 'Failed to save article');
        }
      }
      
    } catch (error) {
      console.error('Error toggling save status:', error);
      
      // Fallback to localStorage for offline functionality
      try {
        const savedData = localStorage.getItem(`savedArticles_${user.id}`);
        let savedArticles = savedData ? JSON.parse(savedData) : [];

        if (isSaved) {
          savedArticles = savedArticles.filter(saved => saved.id !== article.id);
          setIsSaved(false);
        } else {
          const articleToSave = {
            ...article,
            savedAt: new Date().toISOString(),
            savedBy: user.id
          };
          savedArticles.unshift(articleToSave);
          setIsSaved(true);
        }

        localStorage.setItem(`savedArticles_${user.id}`, JSON.stringify(savedArticles));
        console.log('Used localStorage fallback for saving article');
      } catch (fallbackError) {
        console.error('Fallback save also failed:', fallbackError);
        alert('Failed to save article. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Show login prompt if no user
  if (!user) {
    return (
      <button
        onClick={() => alert('Please sign in to save articles')}
        className={`${buttonSizeClasses[size]} rounded-full bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors`}
        title="Sign in to save articles"
      >
        <svg className={sizeClasses[size]} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
        </svg>
      </button>
    );
  }

  return (
    <button
      onClick={toggleSave}
      disabled={isLoading}
      className={`${buttonSizeClasses[size]} rounded-full transition-all duration-200 ${
        isSaved
          ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/40'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
      } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}`}
      title={isSaved ? 'Remove from saved articles' : 'Save article'}
    >
      {isLoading ? (
        <svg className={`${sizeClasses[size]} animate-spin`} fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : isSaved ? (
        <svg className={sizeClasses[size]} fill="currentColor" viewBox="0 0 24 24">
          <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
        </svg>
      ) : (
        <svg className={sizeClasses[size]} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
        </svg>
      )}
    </button>
  );
};

export default BookmarkButton;