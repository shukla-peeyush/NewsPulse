import React from 'react';

interface FilterButtonsProps {
  categories: string[];
  activeFilter: string;
  onFilterChange: (category: string) => void;
}

const FilterButtons: React.FC<FilterButtonsProps> = ({ categories, activeFilter, onFilterChange }) => {
  return (
    <div className="flex items-center overflow-x-auto space-x-3 pb-4 mb-8">
      {categories.map(category => {
        const isActive = category === activeFilter;
        const buttonClasses = isActive
          ? 'bg-gray-900 text-white'
          : 'bg-white text-gray-800 hover:bg-gray-100 border border-gray-300';
        
        return (
          <button
            key={category}
            onClick={() => onFilterChange(category)}
            className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 ${buttonClasses}`}
          >
            {category}
          </button>
        );
      })}
    </div>
  );
};

export default FilterButtons;