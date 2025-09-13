import React from 'react';
import NewsCard from './NewsCard';
import type { Article } from '../types';

interface NewsGridProps {
  articles: Article[];
  categoryColors: { [key: string]: string };
}

const NewsGrid: React.FC<NewsGridProps> = ({ articles, categoryColors }) => {
  if (articles.length === 0) {
    return (
      <p className="text-center text-gray-500 col-span-full">
        No articles found for this category.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {articles.map((article, index) => (
        <NewsCard 
          key={index} 
          article={article} 
          categoryColor={categoryColors[article.category] || 'bg-gray-100 text-gray-800'}
        />
      ))}
    </div>
  );
};

export default NewsGrid;