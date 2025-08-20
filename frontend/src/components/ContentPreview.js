import React, { useState } from 'react';
import { FiCopy, FiCheck } from 'react-icons/fi';

const ContentPreview = ({ title, content, icon: Icon, isPrefilled = true }) => {
  const [copied, setCopied] = useState(false);

  
  const convertEscapeSequences = (text) => {
    if (!text || typeof text !== 'string') return text;
    
    return text
      .replace(/\\n/g, '\n')      
      .replace(/\\t/g, '\t')      
      .replace(/\\r/g, '\r')      
      .replace(/\\"/g, '"')       
      .replace(/\\'/g, "'")       
      .replace(/\\\\/g, '\\');    
  };

  
  const displayContent = convertEscapeSequences(content);

  const handleCopy = async (e) => {
    
    e.preventDefault();
    e.stopPropagation();
    
    try {
      
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(displayContent);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } else {
        
        const textArea = document.createElement('textarea');
        textArea.value = displayContent;
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
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 relative group overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 p-3 sm:p-4 lg:p-3 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white min-w-0">
        <div className="flex items-center gap-3 min-w-0 flex-1 overflow-hidden">
          <div className="p-1.5 bg-slate-100 rounded-xl shadow-sm flex-shrink-0">
            <Icon className="text-slate-600 text-base" />
          </div>
          <h4 className="text-base font-semibold text-slate-800 truncate min-w-0">{title}</h4>
        </div>
        
        {/* Copy Button - Always on the right side, never wraps */}
        <button
          type="button"
          onClick={handleCopy}
          className={`flex items-center justify-center w-8 h-8 rounded-xl transition-all duration-300 transform hover:scale-110 active:scale-95 shadow-sm hover:shadow-md border flex-shrink-0 ml-2 ${
            copied
              ? 'bg-emerald-50 text-emerald-600 border-emerald-200 shadow-emerald-100'
              : 'bg-slate-50 text-slate-600 hover:bg-slate-100 border-slate-200 hover:border-slate-300 hover:shadow-slate-200'
          }`}
          title="Copy content to clipboard"
          disabled={copied}
        >
          {copied ? (
            <FiCheck className="text-sm animate-pulse" />
          ) : (
            <FiCopy className="text-sm group-hover:rotate-12 transition-transform duration-300" />
          )}
        </button>
      </div>
      
      {/* Content Area */}
      <div className="p-3 sm:p-4 lg:p-3">
        <div className={`bg-slate-50 rounded-xl p-3 sm:p-4 lg:p-3 border-l-4 transition-all duration-300 relative ${
          copied ? 'border-emerald-400 shadow-lg shadow-emerald-100' : 'border-slate-300'
        }`}>
          <div className="relative">
            {/* Content with fixed height and scroll */}
            <div className="h-80 sm:h-96 overflow-y-auto">
              <p className="text-slate-700 text-sm sm:text-base leading-relaxed whitespace-pre-wrap font-medium">
                {displayContent}
              </p>
            </div>
            
            {/* Character count */}
            <div className="mt-2 text-xs text-slate-400 font-mono text-center">
              {displayContent.length} characters
            </div>
          </div>
          
          {/* Success indicator when copied */}
          {copied && (
            <div className="absolute top-2 right-2 animate-bounce">
              <div className="bg-emerald-500 text-white text-xs px-2 py-1 rounded-lg shadow-lg font-medium">
                ✓ Copied!
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Subtle hover effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
    </div>
  );
};

export default ContentPreview; 