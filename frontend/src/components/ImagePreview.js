import React, { useState } from 'react';
import { FiImage, FiFrown, FiX } from 'react-icons/fi';

const ImagePreview = ({ title, url, icon: Icon, isPrefilled = true }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = () => {
    if (url) {
      setIsModalOpen(true);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 sm:p-6 hover:bg-slate-100 transition-all duration-300">
        <div className="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
          <div className="p-2 bg-slate-200 rounded-xl">
            <Icon className="text-slate-600 text-sm sm:text-lg" />
          </div>
          <h4 className="text-sm sm:text-lg font-medium text-slate-800">{title}</h4>
        </div>
        
        {/* Image Container with Fixed Height */}
        <div className="h-32 sm:h-48 rounded-2xl border-2 border-slate-200 overflow-hidden">
          {url ? (
            <div className="relative w-full h-full">
              <img 
                src={url} 
                alt={title}
                className="w-full h-full object-cover cursor-pointer hover:opacity-90 transition-opacity duration-200"
                onClick={openModal}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
              <div className="hidden absolute inset-0 bg-slate-100 items-center justify-center">
                <div className="flex flex-col items-center gap-2 text-slate-400">
                  <FiFrown className="w-8 h-8" />
                  <p className="text-sm font-medium">Image not available</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="w-full h-full bg-slate-100 flex items-center justify-center">
              <div className="flex flex-col items-center gap-2 text-slate-400">
                <FiImage className="w-8 h-8" />
                <p className="text-sm font-medium">No image provided</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Image Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-4xl max-h-full">
            {/* Close Button */}
            <button
              onClick={closeModal}
              className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors duration-200 z-10"
            >
              <div className="flex items-center gap-2 bg-black bg-opacity-50 rounded-lg px-3 py-2">
                <FiX className="w-5 h-5" />
                <span className="text-sm">Close</span>
              </div>
            </button>
            
            {/* Image */}
            <img 
              src={url} 
              alt={title}
              className="max-w-full max-h-[80vh] object-contain rounded-lg shadow-2xl"
            />
            
            {/* Image Title */}
            <div className="absolute -bottom-12 left-0 text-white">
              <div className="bg-black bg-opacity-50 rounded-lg px-3 py-2">
                <p className="text-sm font-medium">{title}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ImagePreview; 