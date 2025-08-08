import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUser, FiGlobe, FiEdit3, FiImage, FiX, FiSend } from 'react-icons/fi';

// Import logo
import logo from '../assets/logo.png';

function SocialMediaForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    contentCreator: '',
    email: '',
    socialPlatforms: '',
    customContent: '',
    aiPrompt: '',
    excludedLLMs: [],
    postImage: ''
  });

  const [loading, setLoading] = useState(false);

  const contentCreators = [
    { id: 'creator1', name: 'Bob - Ultrasound.AI', email: 'Bob@Ultrasound.AI' },
    { id: 'creator2', name: 'Leah Calahan - Ultrasound.AI', email: 'Leah.Calahan@@Ultrasound.AI' },
    { id: 'creator3', name: 'Matthew - Automation Consulting Services', email: 'Matthew@AutomationConsultingServices.org' }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        excludedLLMs: checked 
          ? [...prev.excludedLLMs, value]
          : prev.excludedLLMs.filter(llm => llm !== value)
      }));
    } else {
      setFormData(prev => {
        const newData = {
          ...prev,
          [name]: value
        };
        
        // Mutual exclusion validation for custom content and AI prompt
        if (name === 'customContent' && value.trim()) {
          // If custom content is filled, clear AI prompt
          newData.aiPrompt = '';
        } else if (name === 'aiPrompt' && value.trim()) {
          // If AI prompt is filled, clear custom content
          newData.customContent = '';
        }
        
        return newData;
      });
    }
  };

  const handleCreatorChange = (e) => {
    const creatorId = e.target.value;
    const creator = contentCreators.find(c => c.id === creatorId);
    
    setFormData(prev => ({
      ...prev,
      contentCreator: creatorId,
      email: creator ? creator.email : ''
    }));
  };

  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const resetForm = () => {
    setFormData({
      contentCreator: '',
      email: '',
      socialPlatforms: '',
      customContent: '',
      aiPrompt: '',
      excludedLLMs: [],
      postImage: '',
      imageUrl: '',
      imageFile: null,
      aiImageStyle: '',
      aiImageDescription: ''
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation: At least one content field must be filled
    if (!formData.customContent.trim() && !formData.aiPrompt.trim()) {
      setErrorMessage('Please provide either Custom Content or an AI Prompt. At least one is required.');
      setShowError(true);
      
      // Hide error message after 4 seconds
      setTimeout(() => {
        setShowError(false);
      }, 4000);
      return;
    }
    
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      setShowSuccess(true);
      resetForm();
      
      // Hide success message after 5 seconds
      setTimeout(() => {
        setShowSuccess(false);
      }, 5000);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f8fafc] to-[#e2e8f0] py-8 px-4 sm:px-6 lg:px-8">
      {/* Success Message */}
      {showSuccess && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-sm animate-fade-in">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div>
              <div className="font-semibold">Success!</div>
              <div className="text-sm opacity-90">Your social media post has been submitted successfully.</div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {showError && (
        <div className="fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-sm animate-fade-in">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <div className="font-semibold">Error</div>
              <div className="text-sm opacity-90">{errorMessage}</div>
            </div>
          </div>
        </div>
      )}
      
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8 sm:mb-12">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="bg-white rounded-2xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
              <img 
                src={logo} 
                alt="n8n Automation Logo" 
                className="h-16 w-auto sm:h-20 md:h-24 object-contain"
              />
            </div>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-light text-[#1e293b] mb-3 sm:mb-4 animate-fade-in">
            Social Media Posting Form
          </h1>
          <p className="text-[#64748b] text-sm sm:text-base lg:text-lg max-w-2xl mx-auto px-4 animate-fade-in-delay">
            Create and schedule your social media posts with AI-powered content generation
          </p>
          <div className="flex justify-center gap-4 mt-6">
            <button 
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-[#64748b] text-white rounded-xl hover:bg-[#475569] transition-all duration-200 text-sm"
            >
              Feedback Form
            </button>
            <button 
              onClick={() => navigate('/social-media')}
              className="px-4 py-2 bg-[#1e40af] text-white rounded-xl hover:bg-[#1d4ed8] transition-all duration-200 text-sm shadow-md"
            >
              Social Media Form
            </button>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8">
          {/* Content Creator Section */}
          <div className="bg-white border border-[#e2e8f0] rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
            <h2 className="text-xl sm:text-2xl font-medium text-[#1e293b] mb-4 sm:mb-6 flex items-center gap-3">
              <div className="p-2 bg-[#f1f5f9] rounded-xl">
                <FiUser className="text-[#1e40af] text-lg" />
              </div>
              Content Creator
            </h2>
            <p className="text-[#64748b] text-sm sm:text-base mb-4">
              Who is making this post? This is used to direct email notifications.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-[#1e293b] font-medium mb-2 text-sm sm:text-base">
                  Content Creator <span className="text-[#dc2626]">*</span>
                </label>
                <select 
                  name="contentCreator"
                  value={formData.contentCreator}
                  onChange={handleCreatorChange}
                  className="w-full bg-[#f8fafc] border border-[#e2e8f0] rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-[#1e293b] focus:outline-none focus:ring-2 focus:ring-[#1e40af] focus:border-[#1e40af] transition-all duration-200 text-sm sm:text-base"
                >
                  <option value="">Select a content creator</option>
                  {contentCreators.map(creator => (
                    <option key={creator.id} value={creator.id}>
                      {creator.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-[#1e293b] font-medium mb-2 text-sm sm:text-base">
                  Email <span className="text-[#64748b] text-xs sm:text-sm">(Auto-filled)</span>
                </label>
                <input 
                  type="email" 
                  name="email"
                  value={formData.email}
                  readOnly
                  className="w-full bg-[#f1f5f9] border border-[#e2e8f0] rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-[#64748b] cursor-not-allowed text-sm sm:text-base"
                  placeholder="Email will be auto-filled when creator is selected"
                />
              </div>
            </div>
          </div>

          {/* Social Platforms Section */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
            <h2 className="text-xl sm:text-2xl font-medium text-slate-800 mb-4 sm:mb-6 flex items-center gap-3">
              <div className="p-2 bg-slate-100 rounded-xl">
                <FiGlobe className="text-slate-600 text-lg" />
              </div>
              Social Platforms
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 ml-2">
                Required
              </span>
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mb-6">
              Which Social Media Platforms Would You Like to Post To?
            </p>
            
            {/* Required field indicator */}
            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl">
              <div className="flex items-center gap-2 text-amber-800 text-sm">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Please select one platform to continue</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <label className="relative cursor-pointer group transition-all duration-200">
                <input 
                  type="radio" 
                  name="socialPlatforms" 
                  className="sr-only" 
                  value="linkedin"
                  checked={formData.socialPlatforms === 'linkedin'}
                  onChange={handleInputChange}
                />
                <div className={`relative p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-24 sm:h-32 flex flex-col justify-center cursor-pointer ${
                  formData.socialPlatforms === 'linkedin'
                    ? 'border-blue-500 bg-blue-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-center gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.socialPlatforms === 'linkedin'
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="text-lg sm:text-xl" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                        <rect x="2" y="9" width="4" height="12"></rect>
                        <circle cx="4" cy="4" r="2"></circle>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.socialPlatforms === 'linkedin'
                          ? 'text-blue-800'
                          : 'text-slate-800'
                      }`}>
                        LinkedIn
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.socialPlatforms === 'linkedin'
                          ? 'text-blue-600'
                          : 'text-slate-500'
                      }`}>
                        Professional networking
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.socialPlatforms === 'linkedin' && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="absolute inset-0 rounded-xl sm:rounded-2xl transition-opacity duration-200 bg-slate-500/0 opacity-0 group-hover:opacity-100 group-hover:bg-slate-500/5"></div>
                </div>
              </label>
              
              <label className="relative cursor-pointer group transition-all duration-200">
                <input 
                  type="radio" 
                  name="socialPlatforms" 
                  className="sr-only" 
                  value="twitter"
                  checked={formData.socialPlatforms === 'twitter'}
                  onChange={handleInputChange}
                />
                <div className={`relative p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-24 sm:h-32 flex flex-col justify-center cursor-pointer ${
                  formData.socialPlatforms === 'twitter'
                    ? 'border-blue-500 bg-blue-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-center gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.socialPlatforms === 'twitter'
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="text-lg sm:text-xl" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                        <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.socialPlatforms === 'twitter'
                          ? 'text-blue-800'
                          : 'text-slate-800'
                      }`}>
                        X/Twitter
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.socialPlatforms === 'twitter'
                          ? 'text-blue-600'
                          : 'text-slate-500'
                        }`}>
                        Social media platform
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.socialPlatforms === 'twitter' && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="absolute inset-0 rounded-xl sm:rounded-2xl transition-opacity duration-200 bg-slate-500/0 opacity-0 group-hover:opacity-100 group-hover:bg-slate-500/5"></div>
                </div>
              </label>
            </div>
          </div>

          {/* Custom Content Section */}
          <div className={`bg-white border rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300 ${
            formData.customContent.trim() 
              ? 'border-green-200 bg-green-50/30' 
              : formData.aiPrompt.trim() 
                ? 'border-slate-200 opacity-60' 
                : 'border-slate-200'
          }`}>
            <h2 className="text-xl sm:text-2xl font-medium text-slate-800 mb-4 sm:mb-6 flex items-center gap-3">
              <div className={`p-2 rounded-xl ${
                formData.customContent.trim() 
                  ? 'bg-green-100' 
                  : 'bg-slate-100'
              }`}>
                <FiEdit3 className={`text-lg ${
                  formData.customContent.trim() 
                    ? 'text-green-600' 
                    : 'text-slate-600'
                }`} />
              </div>
              Custom Content?
              {formData.customContent.trim() && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 ml-2">
                  Active
                </span>
              )}
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mb-4">
              Do you have custom post text that you want to send directly to social media?
            </p>
            
            {/* Validation Message */}
            {formData.aiPrompt.trim() && (
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl">
                <div className="flex items-center gap-2 text-amber-700 text-sm">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span>AI Prompt is active - this field will be cleared when you start typing here</span>
                </div>
              </div>
            )}
            
            <textarea 
              name="customContent"
              value={formData.customContent}
              onChange={handleInputChange}
              className={`w-full border rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300 transition-all duration-200 min-h-32 resize-none text-sm sm:text-base ${
                formData.customContent.trim() 
                  ? 'bg-green-50 border-green-300' 
                  : formData.aiPrompt.trim() 
                    ? 'bg-slate-100 border-slate-300' 
                    : 'bg-slate-50 border-slate-200'
              }`}
              placeholder="Enter your custom post content here..."
            />
          </div>

          {/* AI Prompted Text Generation Section */}
          <div className={`bg-white border rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300 ${
            formData.aiPrompt.trim() 
              ? 'border-blue-200 bg-blue-50/30' 
              : formData.customContent.trim() 
                ? 'border-slate-200 opacity-60' 
                : 'border-slate-200'
          }`}>
            <h2 className="text-xl sm:text-2xl font-medium text-slate-800 mb-4 sm:mb-6 flex items-center gap-3">
              <div className={`p-2 rounded-xl ${
                formData.aiPrompt.trim() 
                  ? 'bg-blue-100' 
                  : 'bg-slate-100'
              }`}>
                <FiEdit3 className={`text-lg ${
                  formData.aiPrompt.trim() 
                    ? 'text-blue-600' 
                    : 'text-slate-600'
                }`} />
              </div>
              AI Prompted Text Generation
              {formData.aiPrompt.trim() && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 ml-2">
                  Active
                </span>
              )}
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mb-4">
              If you left Custom Content? blank, please prompt the AI, so it can produce post text for you.
            </p>
            
            {/* Validation Message */}
            {formData.customContent.trim() && (
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl">
                <div className="flex items-center gap-2 text-amber-700 text-sm">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span>Custom Content is active - this field will be cleared when you start typing here</span>
                </div>
              </div>
            )}
            
            <textarea 
              name="aiPrompt"
              value={formData.aiPrompt}
              onChange={handleInputChange}
              className={`w-full border rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300 transition-all duration-200 min-h-32 resize-none text-sm sm:text-base ${
                formData.aiPrompt.trim() 
                  ? 'bg-blue-50 border-blue-300' 
                  : formData.customContent.trim() 
                    ? 'bg-slate-100 border-slate-300' 
                    : 'bg-slate-50 border-slate-200'
              }`}
              placeholder="Describe what kind of post you want the AI to generate..."
            />
          </div>

          {/* Exclude LLMs Section */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
            <h2 className="text-xl sm:text-2xl font-medium text-slate-800 mb-4 sm:mb-6 flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-xl">
                <FiX className="text-orange-600 text-lg" />
              </div>
              Exclude LLMs
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 ml-2">
                Optional
              </span>
            </h2>
            
            <div className="mb-6 p-4 bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-xl">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-orange-800 mb-1">Speed Optimization</h3>
                  <p className="text-sm text-orange-700">
                    Excluding LLMs will generate content faster. Select any models you'd like to skip from the generation process.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
              <label className="relative cursor-pointer group transition-all duration-200">
                <input 
                  type="checkbox" 
                  name="excludedLLMs" 
                  className="sr-only" 
                  value="grok"
                  checked={formData.excludedLLMs.includes('grok')}
                  onChange={handleInputChange}
                />
                <div className={`relative p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-28 sm:h-36 flex flex-col justify-between cursor-pointer ${
                  formData.excludedLLMs.includes('grok')
                    ? 'border-orange-500 bg-orange-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-start gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.excludedLLMs.includes('grok')
                        ? 'bg-orange-100 text-orange-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.excludedLLMs.includes('grok')
                          ? 'text-orange-800'
                          : 'text-slate-800'
                      }`}>
                        Grok
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.excludedLLMs.includes('grok')
                          ? 'text-orange-600'
                          : 'text-slate-500'
                      }`}>
                        AI-powered content
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.excludedLLMs.includes('grok') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-orange-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 sm:mt-3">
                    <div className={`text-xs font-medium px-2 py-1 rounded-full inline-block ${
                      formData.excludedLLMs.includes('grok')
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {formData.excludedLLMs.includes('grok') ? 'Excluded' : 'Available'}
                    </div>
                  </div>
                  
                  <div className="absolute inset-0 rounded-xl sm:rounded-2xl transition-opacity duration-200 bg-slate-500/0 opacity-0 group-hover:opacity-100 group-hover:bg-slate-500/5"></div>
                </div>
              </label>
              
              <label className="relative cursor-pointer group transition-all duration-200">
                <input 
                  type="checkbox" 
                  name="excludedLLMs" 
                  className="sr-only" 
                  value="o3"
                  checked={formData.excludedLLMs.includes('o3')}
                  onChange={handleInputChange}
                />
                <div className={`relative p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-28 sm:h-36 flex flex-col justify-between cursor-pointer ${
                  formData.excludedLLMs.includes('o3')
                    ? 'border-orange-500 bg-orange-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-start gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.excludedLLMs.includes('o3')
                        ? 'bg-orange-100 text-orange-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.excludedLLMs.includes('o3')
                          ? 'text-orange-800'
                          : 'text-slate-800'
                      }`}>
                        o3
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.excludedLLMs.includes('o3')
                          ? 'text-orange-600'
                          : 'text-slate-500'
                      }`}>
                        Advanced language model
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.excludedLLMs.includes('o3') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-orange-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 sm:mt-3">
                    <div className={`text-xs font-medium px-2 py-1 rounded-full inline-block ${
                      formData.excludedLLMs.includes('o3')
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {formData.excludedLLMs.includes('o3') ? 'Excluded' : 'Available'}
                    </div>
                  </div>
                  
                  <div className="absolute inset-0 rounded-xl sm:rounded-2xl transition-opacity duration-200 bg-slate-500/0 opacity-0 group-hover:opacity-100 group-hover:bg-slate-500/5"></div>
                </div>
              </label>
              
              <label className="relative cursor-pointer group transition-all duration-200">
                <input 
                  type="checkbox" 
                  name="excludedLLMs" 
                  className="sr-only" 
                  value="gemini"
                  checked={formData.excludedLLMs.includes('gemini')}
                  onChange={handleInputChange}
                />
                <div className={`relative p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-28 sm:h-36 flex flex-col justify-between cursor-pointer ${
                  formData.excludedLLMs.includes('gemini')
                    ? 'border-orange-500 bg-orange-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-start gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.excludedLLMs.includes('gemini')
                        ? 'bg-orange-100 text-orange-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.excludedLLMs.includes('gemini')
                          ? 'text-orange-800'
                          : 'text-slate-800'
                      }`}>
                        Gemini
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.excludedLLMs.includes('gemini')
                          ? 'text-orange-600'
                          : 'text-slate-500'
                      }`}>
                        Google's latest AI model
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.excludedLLMs.includes('gemini') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-orange-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 sm:mt-3">
                    <div className={`text-xs font-medium px-2 py-1 rounded-full inline-block ${
                      formData.excludedLLMs.includes('gemini')
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {formData.excludedLLMs.includes('gemini') ? 'Excluded' : 'Available'}
                    </div>
                  </div>
                  
                  <div className="absolute inset-0 rounded-xl sm:rounded-2xl transition-opacity duration-200 bg-slate-500/0 opacity-0 group-hover:opacity-100 group-hover:bg-slate-500/5"></div>
                </div>
              </label>
            </div>
          </div>

          {/* Post Image Section */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
            <h2 className="text-xl sm:text-2xl font-medium text-slate-800 mb-4 sm:mb-6 flex items-center gap-3">
              <div className="p-2 bg-slate-100 rounded-xl">
                <FiImage className="text-slate-600 text-lg" />
              </div>
              Post Image
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 ml-2">
                Optional
              </span>
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mb-6">
              Would you like to add an image to your post?
            </p>

                    {/* Dynamic selection notice */}
        {formData.postImage && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-xl">
            <div className="flex items-center gap-2 text-blue-700 text-sm">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Selected:</span>
              <span className="capitalize">
                {formData.postImage === 'url' && 'Image URL'}
                {formData.postImage === 'upload' && 'Upload Image'}
                {formData.postImage === 'ai-generated' && 'AI Generated Image'}
                {formData.postImage === 'none' && 'No Image'}
              </span>
              <span className="text-blue-600">• Click another option to change</span>
            </div>
          </div>
        )}

            <div className="space-y-3 sm:space-y-4">
              {/* URL Option */}
              <div className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${
                formData.postImage === 'url' 
                  ? 'border-blue-500 bg-blue-50' 
                  : formData.postImage && formData.postImage !== 'url'
                    ? 'border-slate-200 bg-slate-50 opacity-60'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
              }`}>
                <label className="block cursor-pointer">
                  <input 
                    type="radio" 
                    name="postImage" 
                    className="sr-only" 
                    value="url"
                    checked={formData.postImage === 'url'}
                    onChange={handleInputChange}
                  />
                  <div className="p-3 sm:p-4">
                    <div className="flex items-center justify-between mb-2 sm:mb-3">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <div className={`w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 transition-all duration-200 flex items-center justify-center ${
                          formData.postImage === 'url' 
                            ? 'border-blue-500 bg-blue-500' 
                            : 'border-slate-300'
                        }`}>
                          {formData.postImage === 'url' && (
                            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white rounded-full"></div>
                          )}
                        </div>
                        <div>
                          <div className={`font-semibold text-sm sm:text-base transition-colors duration-200 ${
                            formData.postImage === 'url' ? 'text-blue-800' : 'text-slate-800'
                          }`}>
                            Image URL
                          </div>
                          <div className={`text-xs sm:text-sm transition-colors duration-200 ${
                            formData.postImage === 'url' ? 'text-blue-600' : 'text-slate-500'
                          }`}>
                            Provide image URL
                          </div>
                        </div>
                      </div>
                      <svg 
                        className={`w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-200 ${
                          formData.postImage === 'url' ? 'text-blue-500 rotate-180' : 'text-slate-400'
                        }`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <polyline points="6 9 12 15 18 9"></polyline>
                      </svg>
                    </div>
                    
                    {/* URL Input Field */}
                    {formData.postImage === 'url' && (
                      <div className="mt-2 sm:mt-3 pl-6 sm:pl-8">
                        <input 
                          type="url" 
                          name="imageUrl"
                          placeholder="https://example.com/image.jpg"
                          className="w-full px-2 sm:px-3 py-1.5 sm:py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-xs sm:text-sm"
                        />
                      </div>
                    )}
                  </div>
                </label>
              </div>

              {/* Upload Option */}
              <div className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${
                formData.postImage === 'upload' 
                  ? 'border-blue-500 bg-blue-50' 
                  : formData.postImage && formData.postImage !== 'upload'
                    ? 'border-slate-200 bg-slate-50 opacity-60'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
              }`}>
                <label className="block cursor-pointer">
                  <input 
                    type="radio" 
                    name="postImage" 
                    className="sr-only" 
                    value="upload"
                    checked={formData.postImage === 'upload'}
                    onChange={handleInputChange}
                  />
                  <div className="p-3 sm:p-4">
                    <div className="flex items-center justify-between mb-2 sm:mb-3">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <div className={`w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 transition-all duration-200 flex items-center justify-center ${
                          formData.postImage === 'upload' 
                            ? 'border-blue-500 bg-blue-500' 
                            : 'border-slate-300'
                        }`}>
                          {formData.postImage === 'upload' && (
                            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white rounded-full"></div>
                          )}
                        </div>
                        <div>
                          <div className={`font-semibold text-sm sm:text-base transition-colors duration-200 ${
                            formData.postImage === 'upload' ? 'text-blue-800' : 'text-slate-800'
                          }`}>
                            Upload Image
                          </div>
                          <div className={`text-xs sm:text-sm transition-colors duration-200 ${
                            formData.postImage === 'upload' ? 'text-blue-600' : 'text-slate-500'
                          }`}>
                            Upload image file
                          </div>
                        </div>
                      </div>
                      <svg 
                        className={`w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-200 ${
                          formData.postImage === 'upload' ? 'text-blue-500 rotate-180' : 'text-slate-400'
                        }`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <polyline points="6 9 12 15 18 9"></polyline>
                      </svg>
                    </div>
                    
                    {/* File Upload Field */}
                    {formData.postImage === 'upload' && (
                      <div className="mt-2 sm:mt-3 pl-6 sm:pl-8">
                        <div className="border-2 border-dashed border-slate-300 rounded-lg p-3 sm:p-4 text-center hover:border-blue-400 transition-colors duration-200">
                          <svg className="w-6 h-6 sm:w-8 sm:h-8 text-slate-400 mx-auto mb-1 sm:mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                          </svg>
                          <p className="text-xs sm:text-sm text-slate-600 mb-1 sm:mb-2">Click to upload or drag and drop</p>
                          <p className="text-xs text-slate-500">PNG, JPG, GIF up to 10MB</p>
                          <input 
                            type="file" 
                            name="imageFile"
                            accept="image/*"
                            className="hidden"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </label>
              </div>

              {/* AI Generated Option */}
              <div className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${
                formData.postImage === 'ai-generated' 
                  ? 'border-blue-500 bg-blue-50' 
                  : formData.postImage && formData.postImage !== 'ai-generated'
                    ? 'border-slate-200 bg-slate-50 opacity-60'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
              }`}>
                <label className="block cursor-pointer">
                  <input 
                    type="radio" 
                    name="postImage" 
                    className="sr-only" 
                    value="ai-generated"
                    checked={formData.postImage === 'ai-generated'}
                    onChange={handleInputChange}
                  />
                  <div className="p-3 sm:p-4">
                    <div className="flex items-center justify-between mb-2 sm:mb-3">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <div className={`w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 transition-all duration-200 flex items-center justify-center ${
                          formData.postImage === 'ai-generated' 
                            ? 'border-blue-500 bg-blue-500' 
                            : 'border-slate-300'
                        }`}>
                          {formData.postImage === 'ai-generated' && (
                            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white rounded-full"></div>
                          )}
                        </div>
                        <div>
                          <div className={`font-semibold text-sm sm:text-base transition-colors duration-200 ${
                            formData.postImage === 'ai-generated' ? 'text-blue-800' : 'text-slate-800'
                          }`}>
                            AI Generated
                          </div>
                          <div className={`text-xs sm:text-sm transition-colors duration-200 ${
                            formData.postImage === 'ai-generated' ? 'text-blue-600' : 'text-slate-500'
                          }`}>
                            AI-generated based on post text
                          </div>
                        </div>
                      </div>
                      <svg 
                        className={`w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-200 ${
                          formData.postImage === 'ai-generated' ? 'text-blue-500 rotate-180' : 'text-slate-400'
                        }`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <polyline points="6 9 12 15 18 9"></polyline>
                      </svg>
                    </div>
                    
                    {/* AI Generation Info */}
                    {formData.postImage === 'ai-generated' && (
                      <div className="mt-2 sm:mt-3 pl-6 sm:pl-8">
                        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                          <div className="flex items-center gap-2 text-blue-700 text-xs sm:text-sm">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                            </svg>
                            <span>AI will generate an image based on your post content automatically</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </label>
              </div>

              {/* No Image Option */}
              <div className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${
                formData.postImage === 'none' 
                  ? 'border-blue-500 bg-blue-50' 
                  : formData.postImage && formData.postImage !== 'none'
                    ? 'border-slate-200 bg-slate-50 opacity-60'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
              }`}>
                <label className="block cursor-pointer">
                  <input 
                    type="radio" 
                    name="postImage" 
                    className="sr-only" 
                    value="none"
                    checked={formData.postImage === 'none'}
                    onChange={handleInputChange}
                  />
                  <div className="p-3 sm:p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 sm:gap-3">
                        <div className={`w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 transition-all duration-200 flex items-center justify-center ${
                          formData.postImage === 'none' 
                            ? 'border-blue-500 bg-blue-500' 
                            : 'border-slate-300'
                        }`}>
                          {formData.postImage === 'none' && (
                            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white rounded-full"></div>
                          )}
                        </div>
                        <div>
                          <div className={`font-semibold text-sm sm:text-base transition-colors duration-200 ${
                            formData.postImage === 'none' ? 'text-blue-800' : 'text-slate-800'
                          }`}>
                            No Image
                          </div>
                          <div className={`text-xs sm:text-sm transition-colors duration-200 ${
                            formData.postImage === 'none' ? 'text-blue-600' : 'text-slate-500'
                          }`}>
                            Text-only post
                          </div>
                        </div>
                      </div>
                      <svg 
                        className={`w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-200 ${
                          formData.postImage === 'none' ? 'text-blue-500 rotate-180' : 'text-slate-400'
                        }`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <polyline points="6 9 12 15 18 9"></polyline>
                      </svg>
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="text-center">
            <button 
              type="submit" 
              disabled={loading}
              className="px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-medium transition-all duration-300 shadow-sm hover:shadow-md text-sm sm:text-base bg-slate-800 text-white hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Submitting...</span>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <FiSend />
                  <span>Submit Post Request</span>
                </div>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SocialMediaForm;
