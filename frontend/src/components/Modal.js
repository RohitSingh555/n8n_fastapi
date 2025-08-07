import React from 'react';
import { FiX, FiCheck, FiAlertCircle } from 'react-icons/fi';

const Modal = ({ isOpen, onClose, title, message, type = 'info', children }) => {
  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <FiCheck className="text-emerald-600 text-xl" />;
      case 'error':
        return <FiAlertCircle className="text-red-600 text-xl" />;
      default:
        return <FiAlertCircle className="text-slate-600 text-xl" />;
    }
  };

  const getIconBg = () => {
    switch (type) {
      case 'success':
        return 'bg-emerald-100';
      case 'error':
        return 'bg-red-100';
      default:
        return 'bg-slate-100';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${getIconBg()}`}>
              {getIcon()}
            </div>
            <h3 className="text-lg font-medium text-slate-800">{title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-all duration-200"
          >
            <FiX className="text-lg" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6">
          {message && (
            <p className="text-slate-600 mb-4">{message}</p>
          )}
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal; 