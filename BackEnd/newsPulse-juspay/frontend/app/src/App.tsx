import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import ArticleDetail from './pages/ArticleDetail';
import type { Article } from './types';

// Predefined colors for known categories
const PREDEFINED_CATEGORY_COLORS: { [key: string]: string } = {
  'Funding Round': 'bg-blue-100 text-blue-800',
  'Regulation': 'bg-indigo-100 text-indigo-800',
  'Product Launch': 'bg-green-100 text-green-800',
  'M&A': 'bg-purple-100 text-purple-800',
  'Expansion': 'bg-yellow-100 text-yellow-800',
  'Partnership': 'bg-pink-100 text-pink-800',
};

// Fallback colors for new, dynamic categories
const FALLBACK_COLORS = [
  'bg-teal-100 text-teal-800',
  'bg-cyan-100 text-cyan-800',
  'bg-rose-100 text-rose-800',
  'bg-orange-100 text-orange-800',
];

const App: React.FC = () => {
  const [allArticles, setAllArticles] = useState<Article[]>([]);
  const [filteredArticles, setFilteredArticles] = useState<Article[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [activeFilter, setActiveFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryColors, setCategoryColors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://127.0.0.1:5000/fetch-news');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        const data: Article[] = result.news;
        
        const sortedArticles = data.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
        
        setAllArticles(sortedArticles);
        setFilteredArticles(sortedArticles);
        
        const uniqueCategories = ['All', ...new Set(data.map(article => article.category))];
        setCategories(uniqueCategories);

        const newCategoryColors = { ...PREDEFINED_CATEGORY_COLORS };
        const newCategories = uniqueCategories.filter(cat => cat !== 'All' && !PREDEFINED_CATEGORY_COLORS[cat]);
        
        newCategories.forEach((category, index) => {
          newCategoryColors[category] = FALLBACK_COLORS[index % FALLBACK_COLORS.length];
        });
        setCategoryColors(newCategoryColors);
        
      } catch (e) {
        if (e instanceof Error) {
            setError(`Failed to fetch news. Please ensure the local API server is running at http://127.0.0.1:5000/fetch-news. Error: ${e.message}`);
        } else {
            setError('An unknown error occurred.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleFilterChange = (category: string) => {
    setActiveFilter(category);
    if (category === 'All') {
      setFilteredArticles(allArticles);
    } else {
      const filtered = allArticles.filter(article => article.category === category);
      setFilteredArticles(filtered);
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen font-sans">
      <Header />
      <Routes>
        <Route 
          path="/" 
          element={
            <HomePage 
              loading={loading}
              error={error}
              categories={categories}
              activeFilter={activeFilter}
              handleFilterChange={handleFilterChange}
              filteredArticles={filteredArticles}
              categoryColors={categoryColors}
            />
          } 
        />
        <Route path="/article/:id" element={<ArticleDetail />} />
      </Routes>
    </div>
  );
};

export default App;