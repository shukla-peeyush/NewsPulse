import React from 'react';
import BookmarkButton from './BookmarkButton';

const NewsCard = ({ article, categoryColor, onSummaryClick, user }) => {
  const [isLoadingSummary, setIsLoadingSummary] = React.useState(false);
  
  const handleSummaryClick = async () => {
    setIsLoadingSummary(true);
    await onSummaryClick(article);
    setIsLoadingSummary(false);
  };
  const { title, url, link, summary, publishedDate, published_date, primaryCategory, primary_category, source, sourceName } = article;
  
  // Use the mapped fields first, fallback to original API fields
  const dateToUse = publishedDate || published_date;
  const categoryToUse = primaryCategory || primary_category;
  const sourceToUse = sourceName || source?.name || source;
  const linkToUse = url || link;
  
  const formattedDate = new Date(dateToUse).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
  
  const truncateSummary = (text, wordLimit) => 
    text.split(' ').slice(0, wordLimit).join(' ') + (text.split(' ').length > wordLimit ? '...' : '');
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden flex flex-col">
      <div className="p-6 flex flex-col flex-grow">
        <div className="flex justify-between items-start mb-4">
          <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${categoryColor}`}>
            {categoryToUse || 'Uncategorized'}
          </span>
          <div className="flex items-center space-x-2">
            <BookmarkButton article={article} user={user} size="sm" />
            <p className="text-xs text-gray-500 dark:text-gray-400">{formattedDate}</p>
          </div>
        </div>
        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{title}</h2>
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">{sourceToUse}</p>
        <p className="text-gray-700 dark:text-gray-400 text-base flex-grow">
          {truncateSummary(summary, 30)}
        </p>
        <div className="mt-6 flex justify-between items-center">
          <button 
            onClick={handleSummaryClick}
            disabled={isLoadingSummary}
            className="font-semibold text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isLoadingSummary ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Loading...
              </>
            ) : (
              'View Summary'
            )}
          </button>
          <a 
            href={linkToUse} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="group font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
          >
            Read Full Story <span className="group-hover:translate-x-1 transition-transform">&rarr;</span>
          </a>
        </div>
      </div>
    </div>
  );
};

export default NewsCard;