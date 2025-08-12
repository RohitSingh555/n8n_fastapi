import React from 'react';
import { FiLinkedin, FiTwitter, FiImage } from 'react-icons/fi';
import ContentPreview from './ContentPreview';
import ImagePreview from './ImagePreview';
import RadioGroup from './RadioGroup';

const TabContent = ({ 
  activeTab, 
  formData, 
  handleInputChange, 
  tabValidation,
  isEditMode = false // Add isEditMode prop
}) => {
  // Check if tab has content
  const hasLinkedInContent = () => {
    return formData.linkedin_grok_content?.trim() || 
           formData.linkedin_o3_content?.trim() || 
           formData.linkedin_gemini_content?.trim();
  };

  const hasTwitterContent = () => {
    return formData.x_grok_content?.trim() || 
           formData.x_o3_content?.trim() || 
           formData.x_gemini_content?.trim();
  };

  const hasImageContent = () => {
    return formData.stable_diffusion_image_url?.trim() || 
           formData.pixabay_image_url?.trim() || 
           formData.gpt1_image_url?.trim();
  };

  // If no content and not in edit mode, don't render the tab
  // In edit mode, always render so users can see and edit all fields
  if (!isEditMode) {
    if (activeTab === 'linkedin' && !hasLinkedInContent()) return null;
    if (activeTab === 'twitter' && !hasTwitterContent()) return null;
    if (activeTab === 'images' && !hasImageContent()) return null;
  }

  const linkedinOptions = [
    { value: 'Grok', label: 'Grok', description: 'AI-powered content generation' },
    { value: 'o3', label: 'o3', description: 'Advanced language model' },
    { value: 'Gemini', label: 'Gemini', description: 'Google\'s latest AI model' }
  ];

  const twitterOptions = [
    { value: 'Grok', label: 'Grok', description: 'AI-powered content generation' },
    { value: 'o3', label: 'o3', description: 'Advanced language model' },
    { value: 'Gemini', label: 'Gemini', description: 'Google\'s latest AI model' }
  ];

  const imageOptions = [
    { value: 'Stable', label: 'Stable Diffusion', description: 'AI image generation' },
    { value: 'Pixabay', label: 'Pixabay', description: 'Stock photo library' },
    { value: 'GPT1', label: 'GPT1', description: 'AI image creation' }
  ];

  const renderLinkedInContent = () => {
    // Check which fields are filled to determine which ones should be disabled
    const hasFeedback = formData.linkedin_feedback?.trim() !== '';
    const hasLLM = formData.linkedin_chosen_llm?.trim() !== '';
    const hasCustomContent = formData.linkedin_custom_content?.trim() !== '';
    
    // If any field is filled, disable the others
    const isFeedbackDisabled = hasLLM || hasCustomContent;
    const isLLMDisabled = hasFeedback || hasCustomContent;
    const isCustomContentDisabled = hasFeedback || hasLLM;

    return (
      <div className="space-y-8 sm:space-y-10">
        {/* Content Preview Section */}
        <div className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-slate-300 rounded-full"></div>
            <div className="flex items-center gap-3 group relative">
              <div className="p-2 bg-slate-100 rounded-xl shadow-sm">
                <svg className="w-5 h-5 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl sm:text-2xl font-semibold text-slate-800">Generated Content</h3>
              
              {/* Hover/Click Tooltip */}
              <div className="absolute top-full left-0 mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-10">
                <div className="bg-slate-800 text-white text-xs px-3 py-2 rounded-lg shadow-lg whitespace-nowrap">
                  <div className="flex flex-col gap-1">
                    <span className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full"></div>
                      Ready to use
                    </span>
                    <span className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                      AI-generated
                    </span>
                    <span className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
                      Click copy to use
                    </span>
                  </div>
                  <div className="absolute top-0 left-4 transform -translate-y-1 w-2 h-2 bg-slate-800 rotate-45"></div>
                </div>
              </div>
            </div>
            <div className="flex-1 h-px bg-gradient-to-r from-slate-300 to-transparent"></div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
            {formData.linkedin_grok_content?.trim() && (
              <ContentPreview 
                title="Grok Content" 
                content={formData.linkedin_grok_content}
                icon={FiLinkedin}
              />
            )}
            {formData.linkedin_o3_content?.trim() && (
              <ContentPreview 
                title="o3 Content" 
                content={formData.linkedin_o3_content}
                icon={FiLinkedin}
              />
            )}
            {formData.linkedin_gemini_content?.trim() && (
              <ContentPreview 
                title="Gemini Content" 
                content={formData.linkedin_gemini_content}
                icon={FiLinkedin}
              />
            )}
          </div>
        </div>

        {/* Mutual exclusion notice */}
        {(hasFeedback || hasLLM || hasCustomContent) && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-4 sm:p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3 text-blue-700">
                <div className="p-2 bg-blue-100 rounded-xl">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 text-sm">
                  <span className="font-semibold">Choose One Approach:</span>
                  <span className="text-blue-600">Only one feedback method can be used at a time.</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  handleInputChange({
                    target: { name: 'linkedin_feedback', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'linkedin_chosen_llm', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'linkedin_custom_content', value: '' }
                  });
                }}
                className="px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-xl text-sm font-medium transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105 active:scale-95"
              >
                Clear All
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <div>
            <label className={`block font-medium mb-2 text-sm sm:text-base ${
              isFeedbackDisabled ? 'text-slate-400' : 'text-slate-700'
            }`}>
              LinkedIn Feedback <span className="text-red-500">*</span>
              {isFeedbackDisabled && <span className="text-slate-400 text-xs ml-2">(Disabled)</span>}
            </label>
            <textarea
              name="linkedin_feedback"
              value={formData.linkedin_feedback}
              onChange={handleInputChange}
              disabled={isFeedbackDisabled}
              className={`w-full border rounded-xl px-3 sm:px-4 py-2 sm:py-3 transition-all duration-200 min-h-24 sm:min-h-32 resize-none text-sm sm:text-base ${
                isFeedbackDisabled
                  ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300'
              }`}
              placeholder={isFeedbackDisabled ? "Disabled - clear other fields to enable" : "Enter your feedback for LinkedIn content..."}
              required
            />
          </div>
          
          <div>
            <RadioGroup
              name="linkedin_chosen_llm"
              value={formData.linkedin_chosen_llm}
              onChange={handleInputChange}
              options={linkedinOptions}
              label={`Choose LinkedIn LLM ${isLLMDisabled ? ' (Disabled)' : ''}`}
              required
              disabled={isLLMDisabled}
            />
          </div>
        </div>

        <div>
          <label className={`block font-medium mb-2 text-sm sm:text-base ${
            isCustomContentDisabled ? 'text-slate-400' : 'text-slate-700'
          }`}>
            LinkedIn Custom Content
            {isCustomContentDisabled && <span className="text-slate-400 text-xs ml-2">(Disabled)</span>}
          </label>
          <textarea
            name="linkedin_custom_content"
            value={formData.linkedin_custom_content}
            onChange={handleInputChange}
            disabled={isCustomContentDisabled}
            className={`w-full border rounded-xl px-3 sm:px-4 py-2 sm:py-3 transition-all duration-200 min-h-24 sm:min-h-32 resize-none text-sm sm:text-base ${
              isCustomContentDisabled
                ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300'
            }`}
            placeholder={isCustomContentDisabled ? "Disabled - clear other fields to enable" : "Enter custom LinkedIn content..."}
          />
        </div>
      </div>
    );
  };

  const renderTwitterContent = () => {
    // Check which fields are filled to determine which ones should be disabled
    const hasFeedback = formData.x_feedback?.trim() !== '';
    const hasLLM = formData.x_chosen_llm?.trim() !== '';
    const hasCustomContent = formData.x_custom_content?.trim() !== '';
    
    // If any field is filled, disable the others
    const isFeedbackDisabled = hasLLM || hasCustomContent;
    const isLLMDisabled = hasFeedback || hasCustomContent;
    const isCustomContentDisabled = hasFeedback || hasLLM;

    return (
      <div className="space-y-8 sm:space-y-10">
        {/* Content Preview Section */}
        <div className="space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-8 bg-slate-300 rounded-full"></div>
            <div className="flex items-center gap-3 group relative">
              <div className="p-2 bg-slate-100 rounded-xl shadow-sm">
                <svg className="w-5 h-5 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl sm:text-2xl font-semibold text-slate-800">Generated Content</h3>
              
              {/* Hover/Click Tooltip */}
              <div className="absolute top-full left-0 mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-10">
                <div className="bg-slate-800 text-white text-xs px-3 py-2 rounded-lg shadow-lg whitespace-nowrap">
                  <div className="flex flex-col gap-1">
                    <span className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full"></div>
                      Ready to use
                    </span>
                    <span className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                      AI-generated
                    </span>
                    <span className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
                      Click copy to use
                    </span>
                  </div>
                  <div className="absolute top-0 left-4 transform -translate-y-1 w-2 h-2 bg-slate-800 rotate-45"></div>
                </div>
              </div>
            </div>
            <div className="flex-1 h-px bg-gradient-to-r from-slate-300 to-transparent"></div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
            {formData.x_grok_content?.trim() && (
              <ContentPreview 
                title="Grok Content" 
                content={formData.x_grok_content}
                icon={FiTwitter}
              />
            )}
            {formData.x_o3_content?.trim() && (
              <ContentPreview 
                title="o3 Content" 
                content={formData.x_o3_content}
                icon={FiTwitter}
              />
            )}
            {formData.x_gemini_content?.trim() && (
              <ContentPreview 
                title="Gemini Content" 
                content={formData.x_gemini_content}
                icon={FiTwitter}
              />
            )}
          </div>
        </div>

        {/* Mutual exclusion notice */}
        {(hasFeedback || hasLLM || hasCustomContent) && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-4 sm:p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3 text-blue-700">
                <div className="p-2 bg-blue-100 rounded-xl">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 text-sm">
                  <span className="font-semibold">Choose One Approach:</span>
                  <span className="text-blue-600">Only one feedback method can be used at a time.</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  handleInputChange({
                    target: { name: 'x_feedback', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'x_chosen_llm', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'x_custom_content', value: '' }
                  });
                }}
                className="px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-xl text-sm font-medium transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105 active:scale-95"
              >
                Clear All
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className={`block font-medium mb-2 ${
              isFeedbackDisabled ? 'text-slate-400' : 'text-slate-700'
            }`}>
              X Feedback <span className="text-red-500">*</span>
              {isFeedbackDisabled && <span className="text-slate-400 text-xs ml-2">(Disabled)</span>}
            </label>
            <textarea
              name="x_feedback"
              value={formData.x_feedback}
              onChange={handleInputChange}
              disabled={isFeedbackDisabled}
              className={`w-full border rounded-xl px-4 py-3 transition-all duration-200 min-h-32 resize-none ${
                isFeedbackDisabled
                  ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300'
              }`}
              placeholder={isFeedbackDisabled ? "Disabled - clear other fields to enable" : "Enter your feedback for X content..."}
              required
            />
          </div>
          
          <div>
            <RadioGroup
              name="x_chosen_llm"
              value={formData.x_chosen_llm}
              onChange={handleInputChange}
              options={twitterOptions}
              label={`Choose X LLM${isLLMDisabled ? ' (Disabled)' : ''}`}
              required
              disabled={isLLMDisabled}
            />
          </div>
        </div>

        <div>
          <label className={`block font-medium mb-2 ${
            isCustomContentDisabled ? 'text-slate-400' : 'text-slate-700'
          }`}>
            X Custom Content
            {isCustomContentDisabled && <span className="text-slate-400 text-xs ml-2">(Disabled)</span>}
          </label>
          <textarea
            name="x_custom_content"
            value={formData.x_custom_content}
            onChange={handleInputChange}
            disabled={isCustomContentDisabled}
            className={`w-full border rounded-xl px-4 py-3 transition-all duration-200 min-h-32 resize-none ${
              isCustomContentDisabled
                ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300'
            }`}
            placeholder={isCustomContentDisabled ? "Disabled - clear other fields to enable" : "Enter custom X content..."}
          />
        </div>
      </div>
    );
  };

  const renderImageContent = () => {
    // Check which fields are filled to determine which ones should be disabled
    const hasFeedback = formData.image_feedback?.trim() !== '';
    const hasLLM = formData.image_chosen_llm?.trim() !== '';
    
    // If any field is filled, disable the other
    const isFeedbackDisabled = hasLLM;
    const isLLMDisabled = hasFeedback;

    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {formData.stable_diffusion_image_url?.trim() && (
            <ImagePreview 
              title="Stable Diffusion" 
              url={formData.stable_diffusion_image_url}
              icon={FiImage}
            />
          )}
          {formData.pixabay_image_url?.trim() && (
            <ImagePreview 
              title="Pixabay" 
              url={formData.pixabay_image_url}
              icon={FiImage}
            />
          )}
          {formData.gpt1_image_url?.trim() && (
            <ImagePreview 
              title="GPT1" 
              url={formData.gpt1_image_url}
              icon={FiImage}
            />
          )}
        </div>

        {/* Mutual exclusion notice */}
        {(hasFeedback || hasLLM) && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-blue-700 text-sm">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="font-medium">Choose One Approach:</span>
                <span>Only one feedback method can be used at a time.</span>
              </div>
              <button
                type="button"
                onClick={() => {
                  handleInputChange({
                    target: { name: 'image_feedback', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'image_chosen_llm', value: '' }
                  });
                }}
                className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg text-xs font-medium transition-colors duration-200"
              >
                Clear All
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className={`block font-medium mb-2 ${
              isFeedbackDisabled ? 'text-slate-400' : 'text-slate-700'
            }`}>
              Image Feedback <span className="text-red-500">*</span>
              {isFeedbackDisabled && <span className="text-slate-400 text-xs ml-2">(Disabled)</span>}
            </label>
            <textarea
              name="image_feedback"
              value={formData.image_feedback}
              onChange={handleInputChange}
              disabled={isFeedbackDisabled}
              className={`w-full border rounded-xl px-4 py-3 transition-all duration-200 min-h-32 resize-none ${
                isFeedbackDisabled
                  ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300'
              }`}
              placeholder={isFeedbackDisabled ? "Disabled - clear other fields to enable" : "Enter your feedback for images..."}
              required
            />
          </div>
          
          <div>
            <RadioGroup
              name="image_chosen_llm"
              value={formData.image_chosen_llm}
              onChange={handleInputChange}
              options={imageOptions}
              label={`Choose Image LLM${isLLMDisabled ? ' (Disabled)' : ''}`}
              required
              disabled={isLLMDisabled}
            />
          </div>
        </div>
      </div>
    );
  };

  switch (activeTab) {
    case 'linkedin':
      return renderLinkedInContent();
    case 'twitter':
      return renderTwitterContent();
    case 'images':
      return renderImageContent();
    default:
      return null;
  }
};

export default TabContent; 