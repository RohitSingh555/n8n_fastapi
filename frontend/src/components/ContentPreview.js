import React, { useState } from 'react';
import { FiCopy, FiCheck } from 'react-icons/fi';

const ContentPreview = ({ title, content, icon: Icon, isPrefilled = true }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e) => {
    // Prevent form submission
    e.preventDefault();
    e.stopPropagation();
    
    try {
      // Try modern clipboard API first
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } else {
        // Fallback for older browsers or non-secure contexts
        const textArea = document.createElement('textarea');
        textArea.value = content;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
          document.execCommand('copy');
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        } catch (err) {
          console.error('Fallback copy failed: ', err);
        }
        
        document.body.removeChild(textArea);
      }
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 sm:p-6 hover:bg-slate-100 transition-all duration-300 relative group">
      <div className="flex items-center justify-between mb-3 sm:mb-4">
        <div className="flex items-center gap-2 sm:gap-3">
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
        
        {/* Copy Button */}
        <button
          type="button"
          onClick={handleCopy}
          className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-sm hover:shadow-md ${
            copied
              ? 'bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-emerald-100'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200 hover:border-slate-300 hover:shadow-slate-200'
          }`}
          title="Copy content to clipboard"
          disabled={copied}
        >
          {copied ? (
            <>
              <FiCheck className="text-sm animate-pulse" />
              <span className="font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <FiCopy className="text-sm group-hover:rotate-12 transition-transform duration-300" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      
      <div className={`bg-white rounded-xl p-3 sm:p-4 border-l-4 transition-all duration-300 relative ${
        copied ? 'border-emerald-300 shadow-lg shadow-emerald-100' : 'border-slate-300'
      }`}>
        <p className="text-slate-600 text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">
          {content || 'No content available'}
        </p>
        
        {/* Success indicator when copied */}
        {copied && (
          <div className="absolute top-2 right-2 animate-bounce">
            <div className="bg-emerald-500 text-white text-xs px-2 py-1 rounded-lg shadow-lg">
              ✓ Copied!
            </div>
          </div>
        )}
        
        {/* Subtle copy indicator on hover */}
        {!copied && (
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <div className="bg-slate-800 text-white text-xs px-2 py-1 rounded-lg shadow-lg">
              Click copy button to copy content
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentPreview; 