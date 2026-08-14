import React from 'react';

const Footer = () => {
  return (
    <footer className="border-t border-gray-200 bg-white py-6 mt-16 text-center text-xs text-gray-500">
      <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
        <p>© {new Date().getFullYear()} Universal Converter. Fast & Secure File Transformations.</p>
        <p className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full bg-green-500"></span>
          All engines online
        </p>
      </div>
    </footer>
  );
};

export default Footer;
