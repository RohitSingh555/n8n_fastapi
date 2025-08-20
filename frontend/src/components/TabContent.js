import React from 'react';
import { FiLinkedin, FiTwitter, FiMessageCircle, FiEdit3, FiTrash2, FiImage } from 'react-icons/fi';
import ContentPreview from './ContentPreview';
import ImagePreview from './ImagePreview';
import RadioGroup from './RadioGroup';


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

const TabContent = ({ 
  activeTab, 
  formData, 
  handleInputChange, 
  tabValidation,
  isEditMode = false 
}) => {
  
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
    
    const hasFeedback = formData.linkedin_feedback?.trim() !== '';
    const hasLLM = formData.linkedin_chosen_llm?.trim() !== '';
    const hasCustomContent = formData.linkedin_custom_content?.trim() !== '';
    
    
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
            {formData.linkedin_grok_content?.trim() ? (
              <ContentPreview 
                title="Grok Content" 
                content={formData.linkedin_grok_content}
                icon={FiLinkedin}
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
                <div className="text-slate-400 text-sm">No Grok content generated yet</div>
              </div>
            )}
            {formData.linkedin_o3_content?.trim() ? (
              <ContentPreview 
                title="o3 Content" 
                content={formData.linkedin_o3_content}
                icon={FiLinkedin}
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
                <div className="text-slate-400 text-sm">No o3 content generated yet</div>
              </div>
            )}
            {formData.linkedin_gemini_content?.trim() ? (
              <ContentPreview 
                title="Gemini Content" 
                content={formData.linkedin_gemini_content}
                icon={FiLinkedin}
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
                <div className="text-slate-400 text-sm">No Gemini content generated yet</div>
              </div>
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
              value={convertEscapeSequences(formData.linkedin_feedback)}
              onChange={handleInputChange}
              disabled={isFeedbackDisabled}
              className={`w-full border rounded-xl px-3 sm:px-4 py-2 sm:py-3 transition-all duration-200 min-h-48 sm:min-h-64 resize-none text-sm sm:text-base ${
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
            value={convertEscapeSequences(formData.linkedin_custom_content)}
            onChange={handleInputChange}
            disabled={isCustomContentDisabled}
            className={`w-full border rounded-xl px-3 sm:px-4 py-2 sm:py-3 transition-all duration-200 min-h-48 sm:min-h-64 resize-none text-sm sm:text-base ${
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
    
    const hasFeedback = formData.x_feedback?.trim() !== '';
    const hasLLM = formData.x_chosen_llm?.trim() !== '';
    const hasCustomContent = formData.x_custom_content?.trim() !== '';
    
    
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
            {formData.x_grok_content?.trim() ? (
              <ContentPreview 
                title="Grok Content" 
                content={formData.x_grok_content}
                icon={FiTwitter}
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
                <div className="text-slate-400 text-sm">No Grok content generated yet</div>
              </div>
            )}
            {formData.x_o3_content?.trim() ? (
              <ContentPreview 
                title="o3 Content" 
                content={formData.x_o3_content}
                icon={FiTwitter}
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
                <div className="text-slate-400 text-sm">No o3 content generated yet</div>
              </div>
            )}
            {formData.x_gemini_content?.trim() ? (
              <ContentPreview 
                title="Gemini Content" 
                content={formData.x_gemini_content}
                icon={FiTwitter}
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
                <div className="text-slate-400 text-sm">No Gemini content generated yet</div>
              </div>
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
              value={convertEscapeSequences(formData.x_feedback)}
              onChange={handleInputChange}
              disabled={isFeedbackDisabled}
              className={`w-full border rounded-xl px-4 py-3 transition-all duration-200 min-h-64 resize-none ${
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
            value={convertEscapeSequences(formData.x_custom_content)}
            onChange={handleInputChange}
            disabled={isCustomContentDisabled}
            className={`w-full border rounded-xl px-4 py-3 transition-all duration-200 min-h-64 resize-none ${
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
    
    const hasFeedback = formData.image_feedback?.trim() !== '';
    const hasLinkedInLLM = formData.linkedin_image_llm?.trim() !== '';
    const hasTwitterLLM = formData.twitter_image_llm?.trim() !== '';
    const hasLLM = hasLinkedInLLM || hasTwitterLLM;
    
    
    const isFeedbackDisabled = hasLLM;
    const isLLMDisabled = hasFeedback;

    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {formData.stable_diffusion_image_url?.trim() ? (
            <ImagePreview 
              title="Stable Diffusion" 
              url={formData.stable_diffusion_image_url}
              icon={FiImage}
            />
          ) : (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
              <div className="text-slate-400 text-sm">No Stable Diffusion image yet</div>
            </div>
          )}
          {formData.pixabay_image_url?.trim() ? (
            <ImagePreview 
              title="Pixabay" 
              url={formData.pixabay_image_url}
              icon={FiImage}
            />
          ) : (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
              <div className="text-slate-400 text-sm">No Pixabay image yet</div>
            </div>
          )}
          {formData.gpt1_image_url?.trim() ? (
            <ImagePreview 
              title="GPT1" 
              url={formData.gpt1_image_url}
              icon={FiImage}
            />
          ) : (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center">
              <div className="text-slate-400 text-sm">No GPT1 image yet</div>
            </div>
          )}
        </div>

        {/* Additional Image Previews */}
        <div className="space-y-8">
          {formData.image_url?.trim() && (
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-100 rounded-xl">
                  <FiImage className="w-5 h-5 text-blue-600" />
                </div>
                <h4 className="text-lg font-semibold text-slate-800">Image Preview</h4>
              </div>
              <div className="relative w-full max-w-2xl mx-auto">
                <img 
                  src={formData.image_url} 
                  alt="Image Preview"
                  className="w-full h-auto max-h-96 object-contain rounded-xl shadow-lg border border-slate-200 hover:shadow-xl transition-shadow duration-300"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="hidden absolute inset-0 bg-slate-100 items-center justify-center rounded-xl">
                  <div className="flex flex-col items-center gap-2 text-slate-400">
                    <FiImage className="w-8 h-8" />
                    <p className="text-sm font-medium">Image not available</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {formData.uploaded_image_url?.trim() && (
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-green-100 rounded-xl">
                  <FiImage className="w-5 h-5 text-green-600" />
                </div>
                <h4 className="text-lg font-semibold text-slate-800">Uploaded Image Preview</h4>
              </div>
              <div className="relative w-full max-w-2xl mx-auto">
                <img 
                  src={formData.uploaded_image_url} 
                  alt="Uploaded Image Preview"
                  className="w-full h-auto max-h-96 object-contain rounded-xl shadow-lg border border-slate-200 hover:shadow-xl transition-shadow duration-300"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="hidden absolute inset-0 bg-slate-100 items-center justify-center rounded-xl">
                  <div className="flex flex-col items-center gap-2 text-slate-400">
                    <FiImage className="w-8 h-8" />
                    <p className="text-sm font-medium">Image not available</p>
                  </div>
                </div>
              </div>
            </div>
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
                    target: { name: 'linkedin_image_llm', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'twitter_image_llm', value: '' }
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
              value={convertEscapeSequences(formData.image_feedback)}
              onChange={handleInputChange}
              disabled={isFeedbackDisabled}
              className={`w-full border rounded-xl px-4 py-3 transition-all duration-200 min-h-64 resize-none ${
                isFeedbackDisabled
                  ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300'
              }`}
              placeholder={isFeedbackDisabled ? "Disabled - clear other fields to enable" : "Enter your feedback for images..."}
              required
            />
          </div>
          
          <div className="space-y-6">
            <div>
              <RadioGroup
                name="linkedin_image_llm"
                value={formData.linkedin_image_llm}
                onChange={handleInputChange}
                options={imageOptions}
                label="Choose LinkedIn Image LLM *"
                required
                disabled={isLLMDisabled}
              />
            </div>
            
            <div>
              <RadioGroup
                name="twitter_image_llm"
                value={formData.twitter_image_llm}
                onChange={handleInputChange}
                options={imageOptions}
                label="Choose Twitter Image LLM *"
                required
                disabled={isLLMDisabled}
              />
            </div>
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