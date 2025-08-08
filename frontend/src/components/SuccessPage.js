import React from 'react';
import { FiCheck, FiHome, FiEdit3, FiDownload, FiShare2 } from 'react-icons/fi';

// Import logo
import logo from '../assets/logo.png';

const SuccessPage = ({ submissionId, onReset, onContinueEditing }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Success Card */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 sm:p-12 text-center">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="bg-white rounded-2xl p-3 shadow-lg">
              <img 
                src={logo} 
                alt="n8n Automation Logo" 
                className="h-12 w-auto object-contain"
              />
            </div>
          </div>
          
          {/* Success Icon */}
          <div className="mx-auto w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mb-6">
            <FiCheck className="text-emerald-600 text-3xl" />
          </div>
          
          {/* Success Message */}
          <h1 className="text-3xl sm:text-4xl font-light text-slate-800 mb-4">
            Feedback Submitted Successfully!
          </h1>
          <p className="text-slate-600 text-lg mb-8 max-w-md mx-auto">
            Your feedback has been saved and is now available for review. Thank you for your valuable input!
          </p>
          
          {/* Submission ID */}
          <div className="bg-slate-50 rounded-2xl p-4 mb-8">
            <div className="text-slate-500 text-sm mb-2">Submission ID</div>
            <div className="font-mono text-slate-800 text-lg font-medium">
              {submissionId}
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
            <button
              onClick={onReset}
              className="flex items-center justify-center gap-3 bg-emerald-600 text-white px-6 py-3 rounded-2xl hover:bg-emerald-700 transition-all duration-200 font-medium"
            >
              <FiHome />
              <span>Start New Feedback</span>
            </button>
            <button
              onClick={onContinueEditing}
              className="flex items-center justify-center gap-3 bg-slate-600 text-white px-6 py-3 rounded-2xl hover:bg-slate-700 transition-all duration-200 font-medium"
            >
              <FiEdit3 />
              <span>Continue Editing</span>
            </button>
          </div>
          
          {/* Additional Actions */}
          <div className="border-t border-slate-200 pt-6">
            <div className="text-slate-500 text-sm mb-4">What would you like to do next?</div>
            <div className="flex flex-wrap justify-center gap-3">
              <button className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-all duration-200 text-sm">
                <FiDownload />
                <span>Download Report</span>
              </button>
              <button className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-all duration-200 text-sm">
                <FiShare2 />
                <span>Share Results</span>
              </button>
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-slate-500 text-sm">
            Need help? Contact our support team
          </p>
        </div>
      </div>
    </div>
  );
};

export default SuccessPage; 