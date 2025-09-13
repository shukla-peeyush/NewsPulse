import React from 'react';
import ShareButton from './ShareButton';
import BookmarkButton from './BookmarkButton';

const Modal = ({ article, onClose, user }) => {
  const { 
    title, url, link, summary, detailedSummary, publishedDate, published_date, 
    source, sourceName, image_url, image, summaryLoaded, summaryError 
  } = article;
  
  // Use the mapped fields first, fallback to original API fields
  const dateToUse = publishedDate || published_date;
  const sourceToUse = sourceName || source?.name || source;
  const linkToUse = url || link; // url is the article link
  const imageToUse = image_url || image; // Don't use url for image
  
  const formattedDate = new Date(dateToUse).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
  
  return (
    <div 
      className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex justify-center items-center p-4" 
      onClick={onClose}
    >
      <div 
        className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full" 
        onClick={(e) => e.stopPropagation()}
      >
        {imageToUse && (
          <img 
            src={imageToUse} 
            alt={title} 
            className="w-full h-64 object-cover rounded-t-lg" 
            onError={(e) => {
              e.target.style.display = 'none'; // Hide image if it fails to load
            }}
          />
        )}
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h2>
            <button 
              onClick={onClose} 
              className="text-gray-500 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white text-2xl"
            >
              &times;
            </button>
          </div>
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-4">
            <span>{sourceToUse}</span>
            <span className="mx-2">&bull;</span>
            <span>{formattedDate}</span>
          </div>
          {/* Summary Content */}
          <div className="text-gray-700 dark:text-gray-300 text-base mb-6">
            {summaryError ? (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-red-800 dark:text-red-200 font-medium">Failed to load summary</p>
                <p className="text-red-600 dark:text-red-400 text-sm mt-1">{summaryError}</p>
                <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Showing original summary:</p>
                <p className="mt-2">{summary}</p>
              </div>
            ) : detailedSummary ? (
              <div 
                className="prose dark:prose-invert max-w-none"
                dangerouslySetInnerHTML={{ __html: detailedSummary }}
              />
            ) : summaryLoaded === false ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400"></div>
                <span className="ml-3 text-gray-600 dark:text-gray-400">Loading detailed summary...</span>
              </div>
            ) : (
              <p>{summary}</p>
            )}
          </div>
          <div className="flex justify-between items-center">
            <a 
              href={linkToUse} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              Read Full Story &rarr;
            </a>
            
            {/* Action Buttons */}
            <div className="flex items-center space-x-3">
              {/* Bookmark Button */}
              <BookmarkButton article={article} user={user} size="lg" />
              
              {/* Share Button */}
              <ShareButton 
                title={title}
                url={linkToUse}
                summary={summary}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;