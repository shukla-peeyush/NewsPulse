import React from 'react';
import NewsCard from './NewsCard';

const NewsGrid = ({ articles, categoryColors, onSummaryClick, user }) => {
  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400 text-lg">No articles found for this category.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {articles.map((article) => (
        <NewsCard
          key={article.id}
          article={article}
          categoryColor={categoryColors[article.primary_category] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}
          onSummaryClick={onSummaryClick}
          user={user}
        />
      ))}
    </div>
  );
};

export default NewsGrid;