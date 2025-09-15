import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import NewsGrid from './components/NewsGrid';
import Loading from './components/Loading';
import Modal from './components/Modal';
import CategoryPreferencePopup from './components/CategoryPreferencePopup';
import ErrorDisplay from './components/ErrorBoundary';
import SavedArticles from './components/SavedArticles';
import api from './services/api';

const PREDEFINED_COLORS = {
  'PAYMENTS': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  'FUNDING': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  'REGULATION': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
  'PRODUCT LAUNCH': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  'GENERAL FINTECH': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
  'CRYPTO': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  'MERGERS & ACQUISITIONS': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  'FINANCIAL CRIME': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
};

const FALLBACK_COLORS = [
  'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
  'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
  'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
  'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
  'bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200',
  'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
];

const App = () => {
  const [articles, setArticles] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [colors, setColors] = useState({});
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [savedCategories, setSavedCategories] = useState([]);
  const [showPreferencePopup, setShowPreferencePopup] = useState(false);
  const [pendingCategory, setPendingCategory] = useState(null);
  const [theme, setTheme] = useState(() => 
    localStorage.getItem('theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  );
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showSavedArticles, setShowSavedArticles] = useState(false);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Load saved preferences and check authentication on app start
  useEffect(() => {
    loadSavedPreferences();
    checkAuthStatus();
  }, []);

  // Check if user is already authenticated
  const checkAuthStatus = () => {
    const storedUser = localStorage.getItem('user');
    const isAuth = localStorage.getItem('isAuthenticated');
    
    if (storedUser && isAuth === 'true') {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('user');
        localStorage.removeItem('isAuthenticated');
      }
    }
  };

  // Handle successful authentication
  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  // Handle logout
  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    // Clear any user-specific data
    setSavedCategories([]);
    setShowSavedArticles(false);
    
    // Clear any cached article states
    setSelectedArticle(null);
    setShowPreferencePopup(false);
    setPendingCategory(null);
  };

  // Handle showing saved articles
  const handleShowSavedArticles = () => {
    if (user) {
      setShowSavedArticles(true);
    }
  };

  // Fetch data function (extracted for retry functionality)
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch articles directly from API
      const response = await fetch('http://127.0.0.1:8000/articles');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const articlesData = await response.json();
      
      // Map API response to frontend format (assuming articlesData is an array)
      const mappedArticles = articlesData.map(article => {
        // Fix date parsing - add timezone if missing
        let publishedDate = article.published_date;
        if (publishedDate && !publishedDate.includes('Z') && !publishedDate.includes('+')) {
          publishedDate = publishedDate + 'Z'; // Add UTC timezone
        }
        
        return {
          id: article.id,
          title: article.title,
          url: article.url || article.link,
          summary: article.summary,
          content: article.content,
          publishedDate: publishedDate,
          sourceName: article.source_name,
          relevanceScore: article.relevance_score,
          primaryCategory: article.primary_category?.toUpperCase(),
          confidenceLevel: article.confidence_level,
          // Compatibility fields
          source: { name: article.source_name },
          category: article.primary_category?.toUpperCase(),
          date: publishedDate
        };
      });
      
      // Sort by published date (newest first)
      const sorted = mappedArticles.sort((a, b) => 
        new Date(b.publishedDate || b.published_date).getTime() - 
        new Date(a.publishedDate || a.published_date).getTime()
      );
      
      setArticles(sorted);
      setFiltered(sorted);
      
      // Get categories from API or extract from articles
      let uniqueCats = ['All'];
      try {
        const categoriesResponse = await api.analytics.getCategories();
        if (categoriesResponse.success) {
          const apiCategories = api.mappers.mapCategories(categoriesResponse.data);
          uniqueCats = ['All', ...apiCategories.map(cat => cat.name.toUpperCase())];
        } else {
          // Fallback: extract categories from articles
          uniqueCats = ['All', ...new Set(sorted.map(a => a.primaryCategory || a.primary_category).filter(Boolean).map(c => c.toUpperCase()))];
        }
      } catch (catError) {
        console.warn('Failed to fetch categories, using fallback:', catError);
        uniqueCats = ['All', ...new Set(sorted.map(a => a.primaryCategory || a.primary_category).filter(Boolean).map(c => c.toUpperCase()))];
      }
      
      setCategories(uniqueCats);
      
      // Set up colors for categories
      const newColors = { ...PREDEFINED_COLORS };
      uniqueCats.filter(c => c !== 'All' && !(c in PREDEFINED_COLORS)).forEach((c, i) => {
        newColors[c] = FALLBACK_COLORS[i % FALLBACK_COLORS.length];
      });
      setColors(newColors);
      
      // Reset retry count on successful fetch
      setRetryCount(0);
      
    } catch (e) {
      console.error('Error fetching data:', e);
      setError({
        message: e.message || 'Failed to load articles. Please check if the API server is running.',
        status: e.status || 0,
        details: e.details || null
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [retryCount]);

  // Retry function
  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  // Original useEffect content moved to fetchData function above
  useEffect(() => {
    // This useEffect is now handled by the fetchData function above
  }, []);

  // Combined filter and search effect
  useEffect(() => {
    let result = articles;

    // Apply category filter
    if (activeFilter !== 'All') {
      result = result.filter(article => 
        (article.primaryCategory || article.primary_category)?.toUpperCase() === activeFilter
      );
    }

    // Apply search filter
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      result = result.filter(article => 
        article.title?.toLowerCase().includes(searchLower) ||
        article.summary?.toLowerCase().includes(searchLower) ||
        (article.sourceName || article.source?.name)?.toLowerCase().includes(searchLower) ||
        (article.author)?.toLowerCase().includes(searchLower) ||
        (article.primaryCategory || article.primary_category)?.toLowerCase().includes(searchLower)
      );
    }

    setFiltered(result);
  }, [articles, activeFilter, searchTerm]);

  // SIMPLIFIED: Check if search results suggest a category preference when user interacts with content
  const checkSearchBasedPreference = (clickedArticle) => {
    console.log('🔍 Checking search-based preference:', { 
      searchTerm: searchTerm.trim(), 
      showPreferencePopup, 
      clickedCategory: clickedArticle?.primary_category,
      savedCategories
    });
    
    if (!searchTerm.trim() || showPreferencePopup) {
      console.log('❌ Early return: no search term or popup already showing');
      return;
    }
    
    // SIMPLE LOGIC: If user searched and clicked an article, suggest that article's category
    const articleCategory = (clickedArticle.primaryCategory || clickedArticle.primary_category)?.toUpperCase();
    if (clickedArticle && articleCategory && !savedCategories.includes(articleCategory)) {
      console.log('✅ Suggesting category from clicked article:', articleCategory);
      setPendingCategory(articleCategory);
      setShowPreferencePopup(true);
      return;
    }
    
    if (clickedArticle && articleCategory && savedCategories.includes(articleCategory)) {
      console.log('⚠️ Category already saved:', articleCategory);
    }
    
    console.log('❌ No preference suggestion triggered');
  };

  // Load saved preferences from localStorage (API integration can be added later)
  const loadSavedPreferences = async () => {
    try {
      // Try to load from localStorage first
      const stored = localStorage.getItem('userPreferences');
      if (stored) {
        const data = JSON.parse(stored);
        setSavedCategories(data.savedCategories || []);
        return;
      }
      
      // Fallback: try to load from dummy file for backward compatibility
      const response = await fetch('/user-preferences.json');
      if (response.ok) {
        const data = await response.json();
        setSavedCategories(data.savedCategories || []);
      }
    } catch (error) {
      console.log('Could not load preferences:', error);
      setSavedCategories([]);
    }
  };

  // Save preferences (ready for API integration)
  const savePreferencesToFile = async (newSavedCategories) => {
    try {
      const preferences = {
        savedCategories: newSavedCategories,
        lastUpdated: new Date().toISOString(),
        userId: "dummy-user-001"
      };
      
      // Save to localStorage
      localStorage.setItem('userPreferences', JSON.stringify(preferences));
      console.log('Preferences saved to localStorage:', preferences);
      
      // TODO: Add API call when user preferences endpoint is available
      // await api.users.savePreferences(preferences);
      
    } catch (error) {
      console.error('Error saving preferences:', error);
    }
  };

  // Check if category should trigger save popup
  const checkCategoryPreference = (category) => {
    console.log('📂 Category preference check:', { category, showPreferencePopup, savedCategories });
    
    if (category === 'All' || showPreferencePopup) {
      console.log('❌ Early return: All category or popup already showing');
      return;
    }
    
    // Don't show popup if category is already saved
    if (savedCategories.includes(category)) {
      console.log('⚠️ Category already saved:', category);
      return;
    }
    
    console.log('✅ Showing popup for category:', category);
    // Show popup for category preference
    setPendingCategory(category);
    setShowPreferencePopup(true);
  };

  const handleFilter = (cat) => {
    setActiveFilter(cat);
    // Category saving logic removed - only works through search + article interaction
  };

  // Enhanced function to handle article interactions (View Summary or Read Full Story)
  const handleArticleInteraction = async (article) => {
    console.log('🎯 Article interaction:', { 
      searchTerm, 
      articleCategory: article.primary_category, 
      savedCategories,
      showPreferencePopup 
    });
    
    try {
      // Fetch detailed summary from API
      const response = await fetch(`http://127.0.0.1:8002/articles/${article.id}/summary`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch summary: ${response.status}`);
      }
      
      const articleWithSummary = await response.json();
      
      // Merge the summary data with the original article
      const enhancedArticle = {
        ...article,
        summary: articleWithSummary.summary, // This will be HTML content
        detailedSummary: articleWithSummary.summary,
        summaryLoaded: true
      };
      
      // Open the modal with enhanced article data
      setSelectedArticle(enhancedArticle);
      
    } catch (error) {
      console.error('Error fetching article summary:', error);
      
      // Fallback: show modal with original article data and error message
      const articleWithError = {
        ...article,
        summaryError: error.message,
        summaryLoaded: false
      };
      
      setSelectedArticle(articleWithError);
    }
  };

  const handleSearchChange = (term) => {
    setSearchTerm(term);
  };

  const handleSaveCategory = async (category) => {
    if (!savedCategories.includes(category)) {
      const newSavedCategories = [...savedCategories, category];
      setSavedCategories(newSavedCategories);
      await savePreferencesToFile(newSavedCategories);
    }
    setShowPreferencePopup(false);
    setPendingCategory(null);
  };

  const handleRemoveCategory = async (category) => {
    const newSavedCategories = savedCategories.filter(cat => cat !== category);
    setSavedCategories(newSavedCategories);
    await savePreferencesToFile(newSavedCategories);
    setShowPreferencePopup(false);
    setPendingCategory(null);
  };

  const handleCancelPreference = () => {
    setShowPreferencePopup(false);
    setPendingCategory(null);
  };

  // Handle modal close and check for preference suggestion
  const handleModalClose = (article) => {
    const articleCategory = (article.primaryCategory || article.primary_category)?.toUpperCase();
    console.log('📖 Modal closed after reading article:', {
      searchTerm,
      articleCategory,
      savedCategories
    });
    
    // Close the modal first
    setSelectedArticle(null);
    
    // Then check if we should suggest saving the category
    // (only if user had searched and read an article)
    if (searchTerm.trim()) {
      checkSearchBasedPreference(article);
    }
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen font-sans transition-colors duration-300">
      <Header 
        theme={theme} 
        onThemeSwitch={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        searchTerm={searchTerm}
        onSearchChange={handleSearchChange}
        onMobileMenuToggle={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
        user={user}
        onAuthSuccess={handleAuthSuccess}
        onLogout={handleLogout}
        onShowSavedArticles={handleShowSavedArticles}
      />
      <div className="flex min-h-[calc(100vh-80px)]">
        {/* Sidebar */}
        <Sidebar 
          categories={categories}
          savedCategories={savedCategories}
          activeFilter={activeFilter}
          onFilterChange={handleFilter}
          onRemoveCategory={handleRemoveCategory}
          isMobileOpen={isMobileSidebarOpen}
          onMobileClose={() => setIsMobileSidebarOpen(false)}
        />
        
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto lg:ml-0">
          <div className="container mx-auto px-4 lg:px-6 py-8">
            {/* Search Results Info */}
            {searchTerm && (
              <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-blue-800 dark:text-blue-200">
                  <span className="font-semibold">{filtered.length}</span> article{filtered.length !== 1 ? 's' : ''} found for "{searchTerm}"
                  {activeFilter !== 'All' && (
                    <span> in <span className="font-semibold">{activeFilter}</span> category</span>
                  )}
                </p>
                {filtered.length === 0 && (
                  <p className="text-blue-600 dark:text-blue-300 mt-2 text-sm">
                    Try adjusting your search terms or clearing the category filter.
                  </p>
                )}
              </div>
            )}
            
            {loading && <Loading />}
            {error && (
              <ErrorDisplay 
                error={error} 
                onRetry={handleRetry}
                showRetry={true}
              />
            )}
            {!loading && !error && (
              <NewsGrid 
                articles={filtered} 
                categoryColors={colors} 
                onSummaryClick={handleArticleInteraction}
                user={user}
              />
            )}
          </div>
        </main>
      </div>
      
      {selectedArticle && (
        <Modal 
          article={selectedArticle} 
          onClose={() => handleModalClose(selectedArticle)}
          user={user}
        />
      )}
      
      {showPreferencePopup && pendingCategory && (
        <CategoryPreferencePopup
          category={pendingCategory}
          isAlreadySaved={savedCategories.includes(pendingCategory)}
          onSave={handleSaveCategory}
          onRemove={handleRemoveCategory}
          onCancel={handleCancelPreference}
        />
      )}
      
      {/* Saved Articles Modal */}
      {showSavedArticles && user && (
        <SavedArticles
          user={user}
          onClose={() => setShowSavedArticles(false)}
          categoryColors={colors}
          onArticleClick={handleArticleInteraction}
        />
      )}
    </div>
  );
};

export default App;