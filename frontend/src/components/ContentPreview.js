import React from 'react';

const ContentPreview = ({ title, content, icon: Icon, isPrefilled = true }) => (
  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 sm:p-6 hover:bg-slate-100 transition-all duration-300">
    <div className="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
      <div className="p-2 bg-slate-200 rounded-xl">
        <Icon className="text-slate-600 text-sm sm:text-lg" />
      </div>
      <h4 className="text-sm sm:text-lg font-medium text-slate-800">{title}</h4>
      {isPrefilled && (
        <span className="bg-emerald-100 text-emerald-700 text-xs px-2 sm:px-3 py-1 rounded-full border border-emerald-200">
          Pre-filled
        </span>
      )}
    </div>
    <div className="bg-white rounded-xl p-3 sm:p-4 border-l-4 border-slate-300">
      <p className="text-slate-600 text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">
        {content || 'No content available'}
      </p>
    </div>
  </div>
);

export default ContentPreview; 