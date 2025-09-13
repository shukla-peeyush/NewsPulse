import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import type { Article } from '../types';

const ArticleDetail: React.FC = () => {
  const location = useLocation();
  const article = location.state?.article as Article;

  if (!article) {
    return (
      <div className="text-center py-10">
        <h2 className="text-2xl font-bold text-gray-800">Article not found</h2>
        <p className="text-gray-600 mt-2">The article you are looking for does not exist or could not be loaded.</p>
        <Link to="/" className="text-blue-600 hover:underline mt-4 inline-block">&larr; Back to Home</Link>
      </div>
    );
  }

  const { heading, source, date, summary, image_url } = article;

  const formattedDate = new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <Link to="/" className="text-blue-600 hover:underline mb-6 inline-block">&larr; Back to Home</Link>
      
      <h1 className="text-4xl font-bold text-gray-900 mb-4 leading-tight">{heading}</h1>
      <div className="flex items-center text-sm text-gray-500 mb-6">
        <span>{source}</span>
        <span className="mx-2">&bull;</span>
        <span>{formattedDate}</span>
      </div>
      
      {image_url && (
        <img 
          src={image_url} 
          alt={heading} 
          className="w-full h-auto object-cover rounded-lg shadow-lg mb-8"
        />
      )}
      
      <div className="prose max-w-none text-gray-800 text-lg leading-relaxed">
        {/* Using summary as the full content for now, as per the current data structure */}
        <p>{summary}</p>
      </div>
    </div>
  );
};

export default ArticleDetail;