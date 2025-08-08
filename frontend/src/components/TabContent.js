import React from 'react';
import { FiLinkedin, FiTwitter, FiImage } from 'react-icons/fi';
import ContentPreview from './ContentPreview';
import ImagePreview from './ImagePreview';
import RadioGroup from './RadioGroup';

const TabContent = ({ 
  activeTab, 
  formData, 
  handleInputChange, 
  tabValidation 
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

  // If no content, don't render the tab
  if (activeTab === 'linkedin' && !hasLinkedInContent()) return null;
  if (activeTab === 'twitter' && !hasTwitterContent()) return null;
  if (activeTab === 'images' && !hasImageContent()) return null;

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
      <div className="space-y-6 sm:space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
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

        {/* Mutual exclusion notice */}
        {(hasFeedback || hasLLM || hasCustomContent) && (
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
                    target: { name: 'linkedin_feedback', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'linkedin_chosen_llm', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'linkedin_custom_content', value: '' }
                  });
                }}
                className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg text-xs font-medium transition-colors duration-200"
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
      <div className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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

        {/* Mutual exclusion notice */}
        {(hasFeedback || hasLLM || hasCustomContent) && (
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
                    target: { name: 'x_feedback', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'x_chosen_llm', value: '' }
                  });
                  handleInputChange({
                    target: { name: 'x_custom_content', value: '' }
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