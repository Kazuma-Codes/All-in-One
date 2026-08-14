import React from 'react';

const FormatSelector = ({ value, onChange, options = [] }) => {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full border border-gray-300 rounded-xl px-4 py-3 bg-white font-medium text-gray-900 shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
    >
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
};

export default FormatSelector;
