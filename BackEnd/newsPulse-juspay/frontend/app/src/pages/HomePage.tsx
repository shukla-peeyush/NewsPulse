import React from 'react';
import FilterButtons from '../components/FilterButtons';
import NewsGrid from '../components/NewsGrid';
import Loading from '../components/Loading';
import type { Article } from '../types';

interface HomePageProps {
  loading: boolean;
  error: string | null;
  categories: string[];
  activeFilter: string;
  handleFilterChange: (category: string) => void;
  filteredArticles: Article[];
  categoryColors: { [key: string]: string };
}

const HomePage: React.FC<HomePageProps> = ({
  loading,
  error,
  categories,
  activeFilter,
  handleFilterChange,
  filteredArticles,
  categoryColors,
}) => {
  return (
    <main className="container mx-auto px-4 py-8">
      {!loading && !error && (
        <FilterButtons
          categories={categories}
          activeFilter={activeFilter}
          onFilterChange={handleFilterChange}
        />
      )}
      
      {loading && <Loading />}
      
      {error && <p className="text-center text-red-500">{error}</p>}
      
      {!loading && !error && <NewsGrid articles={filteredArticles} categoryColors={categoryColors} />}
    </main>
  );
};

export default HomePage;