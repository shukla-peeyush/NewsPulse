import React from 'react';
import { Link } from 'react-router-dom';
import type { Article } from '../types';

interface NewsCardProps {
  article: Article;
  categoryColor: string;
}

const NewsCard: React.FC<NewsCardProps> = ({ article, categoryColor }) => {
  const { category, heading, source, date, summary } = article;

  const formattedDate = new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  // Create a URL-friendly slug from the heading
  const articleId = heading.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden transform hover:-translate-y-1 hover:shadow-lg transition-all duration-300 flex flex-col">
      <div className="p-6 flex flex-col flex-grow">
        <div className="flex justify-between items-start mb-4">
          <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${categoryColor}`}>
            {category}
          </span>
          <p className="text-xs text-gray-500">{formattedDate}</p>
        </div>
        <h2 className="text-lg font-bold text-gray-900 mb-2 leading-tight">{heading}</h2>
        <p className="text-sm text-gray-600 mb-4">{source}</p>
        <p className="text-gray-700 text-base leading-relaxed flex-grow">{summary}</p>
        <div className="mt-6">
            <Link 
              to={`/article/${articleId}`}
              state={{ article }}
              className="group font-medium text-blue-600 hover:text-blue-800 transition-colors duration-300"
            >
              Read Full Story <span className="inline-block transform group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
            </Link>
        </div>
      </div>
    </div>
  );
};

export default NewsCard;