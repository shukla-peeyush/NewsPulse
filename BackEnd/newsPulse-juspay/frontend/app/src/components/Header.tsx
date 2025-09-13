import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-3xl font-bold text-gray-900">NewsPulse</h1>
        <p className="text-md text-gray-600 mt-1">
          APAC + MENA Merchant & Payments Intelligence
        </p>
      </div>
    </header>
  );
};

export default Header;