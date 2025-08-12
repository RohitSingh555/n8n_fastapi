import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUser, FiGlobe, FiEdit3, FiImage, FiX, FiSend } from 'react-icons/fi';

// Import logo
import logo from '../assets/logo.png';

function SocialMediaForm() {
  const navigate = useNavigate();
  const dropdownRef = useRef(null);
  
  const [formData, setFormData] = useState({
    contentCreator: '',
    email: '',
    isCustomEmail: false,
    dropdownOpen: false,
    socialPlatforms: [],
    customContent: '',
    aiPrompt: '',
    excludedLLMs: [],
    postImage: '',
    imageUrl: '',
    imageFile: null
  });

  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');

  const contentCreators = [
    { id: 'creator1', name: 'Bob - Ultrasound.AI', email: 'Bob@Ultrasound.AI' },
    { id: 'creator2', name: 'Leah Calahan - Ultrasound.AI', email: 'Leah.Calahan@Ultrasound.AI' },
    { id: 'creator3', name: 'Matthew - Automation Consulting Services', email: 'Matthew@AutomationConsultingServices.org' }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    if (type === 'checkbox') {
      if (name === 'socialPlatforms') {
        setFormData(prev => ({
          ...prev,
          socialPlatforms: checked 
            ? [...prev.socialPlatforms, value]
            : prev.socialPlatforms.filter(platform => platform !== value)
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          excludedLLMs: checked 
            ? [...prev.excludedLLMs, value]
            : prev.excludedLLMs.filter(llm => llm !== value)
        }));
      }
    } else if (type === 'file') {
      const file = files[0];
      if (file) {
        setFormData(prev => ({
          ...prev,
          imageFile: file
        }));
        
        // Automatically upload the file
        handleFileUpload(file);
      }
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

  const handleFileUpload = async (file) => {
    setUploadLoading(true);
    setUploadProgress('Preparing file for upload...');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      setUploadProgress('Uploading file to server...');
      
      const response = await fetch('/api/upload-image', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        setUploadProgress('Upload successful! Processing response...');
        
        // Extract the file URL from the response
        let fileUrl;
        if (result.files && result.files.length > 0) {
          fileUrl = result.files[0];
        } else if (result.url) {
          fileUrl = result.url;
        } else if (result.public_url) {
          fileUrl = result.public_url;
        } else {
          fileUrl = result;
        }
        
        // Ensure fileUrl is a string
        const fileUrlString = typeof fileUrl === 'string' ? fileUrl : JSON.stringify(fileUrl);
        
        setFormData(prev => ({
          ...prev,
          imageUrl: fileUrlString,
          imageFile: null // Clear the file since we now have the URL
        }));
        
        setUploadProgress('File uploaded successfully! URL: ' + fileUrlString);
        
        // Clear progress after 3 seconds
        setTimeout(() => {
          setUploadProgress('');
          setUploadLoading(false);
        }, 3000);
        
      } else {
        throw new Error(`Upload failed: ${response.status}`);
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadProgress('Upload failed. Please try again.');
      
      // Clear error after 3 seconds
      setTimeout(() => {
        setUploadProgress('');
        setUploadLoading(false);
      }, 3000);
    }
  };

  const handleCreatorChange = (e) => {
    const creatorId = e.target.value;
    const creator = contentCreators.find(c => c.id === creatorId);
    
    setFormData(prev => ({
      ...prev,
      contentCreator: creatorId,
      email: creator ? creator.email : '',
      isCustomEmail: false
    }));
  };

  const handleEmailChange = (e) => {
    setFormData(prev => ({
      ...prev,
      email: e.target.value,
      isCustomEmail: true,
      contentCreator: ''
    }));
  };



  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setFormData(prev => ({ ...prev, dropdownOpen: false }));
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const [showSuccess, setShowSuccess] = useState(false);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [feedbackFormLink, setFeedbackFormLink] = useState('');
  const [feedbackSubmissionId, setFeedbackSubmissionId] = useState('');
  const [socialMediaPostId, setSocialMediaPostId] = useState('');

  const resetForm = () => {
    setFormData({
      contentCreator: '',
      email: '',
      isCustomEmail: false,
      dropdownOpen: false,
      socialPlatforms: [],
      customContent: '',
      aiPrompt: '',
      excludedLLMs: [],
      postImage: '',
      imageUrl: '',
      imageFile: null
    });
    setFeedbackFormLink('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation: Content creator or email must be provided
    if (!formData.contentCreator && !formData.email.trim()) {
      setErrorMessage('Please select a content creator or enter a custom email address.');
      setShowError(true);
      
      // Hide error message after 4 seconds
      setTimeout(() => {
        setShowError(false);
      }, 4000);
      return;
    }
    
    // Validation: At least one platform must be selected
    if (formData.socialPlatforms.length === 0) {
      setErrorMessage('Please select at least one social media platform.');
      setShowError(true);
      
      // Hide error message after 4 seconds
      setTimeout(() => {
        setShowError(false);
      }, 4000);
      return;
    }
    
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
    
    try {
      // Get current timestamp in the required format
      const now = new Date();
      const timestamp = `${now.getMonth() + 1}/${now.getDate()}/${now.getFullYear()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
      
      // Get content creator email
      const contentCreatorEmail = formData.contentCreator 
        ? contentCreators.find(c => c.id === formData.contentCreator)?.email 
        : formData.email;
      
      // Get social platforms as comma-separated string
      const socialPlatforms = formData.socialPlatforms.map(platform => {
        if (platform === 'linkedin') return 'LinkedIn';
        if (platform === 'twitter') return 'X/Twitter';
        return platform;
      }).join(', ');
      
      // Get excluded LLMs as comma-separated string
      const excludedLLMs = formData.excludedLLMs.join(', ');
      
      // Determine post image type and value
      let postImageType = '';
      let uploadImageValue = '';
      let imageUrlValue = '';
      
      if (formData.postImage === 'url') {
        postImageType = 'Yes, I have an image URL';
        uploadImageValue = '';
        imageUrlValue = formData.imageUrl || '';
      } else if (formData.postImage === 'upload') {
        postImageType = 'Yes, I have an image upload';
        uploadImageValue = formData.imageUrl || '';
        imageUrlValue = '';
      } else if (formData.postImage === 'ai-generated') {
        postImageType = 'Yes, AI generated image';
        uploadImageValue = '';
        imageUrlValue = '';
      } else {
        postImageType = 'No image';
        uploadImageValue = '';
        imageUrlValue = '';
      }
      
      // Prepare the payload in the exact format required
      const payload = [{
        "Timestamp": timestamp,
        "Social Platforms": socialPlatforms,
        "Custom Content?": formData.customContent || "",
        "AI Prompted Text Generation": formData.aiPrompt || "",
        "Exclude LLMs": excludedLLMs,
        "Post Image?": postImageType,
        "Upload an Image": uploadImageValue,
        "Image URL": imageUrlValue,
        "Content Creator": contentCreatorEmail
      }];
      
      // Send to webhook through our backend proxy
      const response = await fetch('/api/webhook-proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const result = await response.json();
        setLoading(false);
        
        // Extract feedback form link and IDs if available
        if (result.feedback_form_link) {
          setFeedbackFormLink(result.feedback_form_link);
        } else {
          console.warn('No feedback form link received from backend');
          setFeedbackFormLink('');
        }
        
        // Store the IDs in state
        if (result.feedback_submission_id) {
          setFeedbackSubmissionId(result.feedback_submission_id);
          console.log('Feedback Submission ID:', result.feedback_submission_id);
        }
        if (result.social_media_post_id) {
          setSocialMediaPostId(result.social_media_post_id);
          console.log('Social Media Post ID:', result.social_media_post_id);
        }
        
        setShowSuccess(true);
        resetForm();
        
        // Hide success message after 8 seconds (longer to allow copying the link)
        setTimeout(() => {
          setShowSuccess(false);
        }, 8000);
      } else {
        throw new Error(`Failed to submit to webhook: ${response.status}`);
      }
      
    } catch (error) {
      console.error('Error submitting form:', error);
      setLoading(false);
      setErrorMessage('Failed to submit the form. Please try again.');
      setShowError(true);
      
      // Hide error message after 4 seconds
      setTimeout(() => {
        setShowError(false);
      }, 4000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#E8EBF5] to-[#A8B3D4] py-8 px-4 sm:px-6 lg:px-8">
      {/* Success Message */}
      {showSuccess && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-md animate-fade-in">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div className="flex-1 min-w-0">
              <div className="font-semibold mb-2">Success!</div>
              <div className="text-sm opacity-90 mb-3">Your social media post has been submitted successfully.</div>
              
              {feedbackFormLink && (
                <div className="bg-green-600 rounded-lg p-3">
                  <div className="text-xs font-medium mb-2 opacity-90">Feedback Form Link:</div>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={feedbackFormLink}
                      readOnly
                      className="flex-1 bg-green-700 text-white text-xs px-2 py-1 rounded border-0 focus:outline-none focus:ring-2 focus:ring-green-300"
                      onClick={(e) => e.target.select()}
                    />
                    <button
                      type="button"
                      onClick={(e) => {
                        navigator.clipboard.writeText(feedbackFormLink);
                        // Show a brief "Copied!" message
                        const button = e.target;
                        const originalText = button.textContent;
                        button.textContent = 'Copied!';
                        button.className = 'bg-green-400 text-green-900 text-xs px-2 py-1 rounded hover:bg-green-300 transition-colors';
                        setTimeout(() => {
                          button.textContent = originalText;
                          button.className = 'bg-green-400 text-green-900 text-xs px-2 py-1 rounded hover:bg-green-300 transition-colors';
                        }, 1000);
                      }}
                      className="bg-green-400 text-green-900 text-xs px-2 py-1 rounded hover:bg-green-300 transition-colors"
                    >
                      Copy
                    </button>
                  </div>
                  <div className="text-xs opacity-75 mt-1">Use this link to provide feedback on your post</div>
                </div>
              )}
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

      {/* File Upload Loading Overlay */}
      {uploadLoading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 shadow-2xl">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#5A67A5] mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold text-[#3E3E3E] mb-2">Uploading Image</h3>
              <p className="text-[#5A67A5] text-sm mb-4">{uploadProgress}</p>
              <div className="w-full bg-[#E8EBF5] rounded-full h-2">
                <div className="bg-[#5A67A5] h-2 rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8 sm:mb-12">
                      {/* Logo */}
            <div className="flex justify-center mb-8">
              <div className="relative bg-[#FFFFFF] rounded-2xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 overflow-hidden group">
                <img 
                  src={logo} 
                  alt="n8n Automation Logo" 
                  className="h-20 w-auto sm:h-28 md:h-32 lg:h-36 object-contain relative z-10"
                />
                {/* Violet Line Animation */}
                <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out">
                  <div className="w-full h-0.5 bg-gradient-to-r from-transparent via-[#5A67A5]/60 to-transparent"></div>
                </div>
              </div>
            </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-light text-[#3E3E3E] mb-3 sm:mb-4 animate-fade-in">
            Social Media Posting Form
          </h1>
          <p className="text-[#5A67A5] text-sm sm:text-base lg:text-lg max-w-2xl mx-auto px-4 animate-fade-in-delay">
            Create and schedule your social media posts with AI-powered content generation
          </p>
          <div className="flex justify-center gap-4 mt-6">
            <button 
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-[#A8B3D4] text-[#3E3E3E] rounded-xl hover:bg-[#9BA6C7] transition-all duration-200 text-sm"
            >
              Feedback Form
            </button>
            <button 
              onClick={() => navigate('/social-media')}
              className="px-4 py-2 bg-[#5A67A5] text-white rounded-xl hover:bg-[#4A5A95] transition-all duration-200 text-sm shadow-md"
            >
              Social Media Form
            </button>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8">
          {/* Content Creator Section */}
          <div className="bg-[#FFFFFF] border border-[#D5D9E4] rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
            <h2 className="text-xl sm:text-2xl font-medium text-[#3E3E3E] mb-4 sm:mb-6 flex items-center gap-3">
              <div className="p-2 bg-[#E8EBF5] rounded-xl">
                <FiUser className="text-[#5A67A5] text-lg" />
              </div>
              Content Creator
            </h2>
            <p className="text-[#5A67A5] text-sm sm:text-base mb-4">
              Who is making this post? This is used to direct email notifications.
            </p>
                                      <div className="space-y-4">
              {/* Mode Selection */}
              <div className="mb-4">
                <label className="block text-[#3E3E3E] font-medium mb-3 text-sm sm:text-base">
                  Choose Email Method <span className="text-[#dc2626]">*</span>
                </label>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, isCustomEmail: false, contentCreator: '', email: '' }))}
                    className={`flex-1 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 border-2 ${
                      !formData.isCustomEmail
                        ? 'bg-[#5A67A5] text-white border-[#5A67A5] shadow-md'
                        : 'bg-[#FFFFFF] text-[#5A67A5] border-[#D5D9E4] hover:border-[#A8B3D4]'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                      Select from List
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, isCustomEmail: true, contentCreator: '', email: '' }))}
                    className={`flex-1 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 border-2 ${
                      formData.isCustomEmail
                        ? 'bg-[#5A67A5] text-white border-[#5A67A5] shadow-md'
                        : 'bg-[#FFFFFF] text-[#5A67A5] border-[#D5D9E4] hover:border-[#A8B3D4]'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                      Enter Custom Email
                    </div>
                  </button>
                </div>
              </div>



              {/* Content Creator Dropdown */}
              {!formData.isCustomEmail && (
                <div>
                  <label className="block text-[#3E3E3E] font-medium mb-2 text-sm sm:text-base">
                    Content Creator <span className="text-[#dc2626]">*</span>
                  </label>
                  <div className="relative" ref={dropdownRef}>
                    <button
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, dropdownOpen: !prev.dropdownOpen }))}
                      className="w-full bg-[#E8EBF5] border border-[#D5D9E4] rounded-xl px-4 py-3 text-left text-[#3E3E3E] focus:outline-none focus:ring-2 focus:ring-[#5A67A5] focus:border-[#5A67A5] transition-all duration-200 text-sm sm:text-base flex items-center justify-between"
                    >
                      <span className={formData.contentCreator ? 'text-[#3E3E3E]' : 'text-[#5A67A5]'}>
                        {formData.contentCreator 
                          ? contentCreators.find(c => c.id === formData.contentCreator)?.name
                          : 'Select a content creator'
                        }
                      </span>
                      <svg 
                        className={`w-5 h-5 text-[#5A67A5] transition-transform duration-200 ${formData.dropdownOpen ? 'rotate-180' : ''}`}
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                      </svg>
                    </button>
                    
                    {/* Dropdown Options */}
                    {formData.dropdownOpen && (
                      <div className="absolute z-50 w-full mt-2 bg-[#FFFFFF] border border-[#D5D9E4] rounded-xl shadow-lg overflow-hidden">
                        {contentCreators.map(creator => (
                          <button
                            key={creator.id}
                            type="button"
                            onClick={() => {
                              handleCreatorChange({ target: { value: creator.id } });
                              setFormData(prev => ({ ...prev, dropdownOpen: false }));
                            }}
                            className={`w-full px-4 py-3 text-left hover:bg-[#E8EBF5] transition-colors duration-200 border-b border-[#E8EBF5] last:border-b-0 ${
                              formData.contentCreator === creator.id 
                                ? 'bg-[#E8EBF5] text-[#5A67A5]' 
                                : 'text-[#3E3E3E]'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-[#A8B3D4] rounded-full flex items-center justify-center flex-shrink-0">
                                <span className="text-[#5A67A5] font-semibold text-sm">
                                  {creator.name.split(' ')[0][0]}
                                </span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm">{creator.name}</div>
                                <div className="text-xs text-[#5A67A5] truncate">{creator.email}</div>
                              </div>
                              {formData.contentCreator === creator.id && (
                                <svg className="w-4 h-4 text-[#5A67A5] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Custom Email Input */}
              {formData.isCustomEmail && (
                <div>
                  <label className="block text-[#3E3E3E] font-medium mb-2 text-sm sm:text-base">
                    Email Address <span className="text-[#dc2626]">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleEmailChange}
                    placeholder="Enter your email address"
                    className="w-full bg-[#E8EBF5] border border-[#D5D9E4] rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-[#3E3E3E] placeholder-[#5A67A5] focus:outline-none focus:ring-2 focus:ring-[#5A67A5] focus:border-[#5A67A5] transition-all duration-200 text-sm sm:text-base"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Social Platforms Section */}
          <div className="bg-[#FFFFFF] border border-[#D5D9E4] rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
            <h2 className="text-xl sm:text-2xl font-medium text-[#3E3E3E] mb-4 sm:mb-6 flex items-center gap-3">
              <div className="p-2 bg-[#E8EBF5] rounded-xl">
                <FiGlobe className="text-[#5A67A5] text-lg" />
              </div>
              Social Platforms
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 ml-2">
                Required
              </span>
            </h2>
            <p className="text-[#5A67A5] text-sm sm:text-base mb-6">
              Which Social Media Platforms Would You Like to Post To?
            </p>
            
            {/* Required field indicator */}
            <div className="mb-4 p-3 bg-[#E8EBF5] border border-[#A8B3D4] rounded-xl">
              <div className="flex items-center gap-2 text-[#5A67A5] text-sm">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Please select at least one platform to continue</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <label className="relative cursor-pointer group transition-all duration-200">
                <input 
                  type="checkbox" 
                  name="socialPlatforms" 
                  className="sr-only" 
                  value="linkedin"
                  checked={formData.socialPlatforms.includes('linkedin')}
                  onChange={handleInputChange}
                />
                <div className={`relative p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-24 sm:h-32 flex flex-col justify-center cursor-pointer ${
                  formData.socialPlatforms.includes('linkedin')
                    ? 'border-[#5A67A5] bg-[#E8EBF5] shadow-lg'
                    : 'border-[#D5D9E4] bg-[#FFFFFF] hover:border-[#A8B3D4] hover:bg-[#E8EBF5] hover:shadow-md'
                }`}>
                  <div className="flex items-center gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.socialPlatforms.includes('linkedin')
                        ? 'bg-[#A8B3D4] text-[#5A67A5]'
                        : 'bg-[#E8EBF5] text-[#5A67A5]'
                    }`}>
                      <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="text-lg sm:text-xl" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                        <rect x="2" y="9" width="4" height="12"></rect>
                        <circle cx="4" cy="4" r="2"></circle>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.socialPlatforms.includes('linkedin')
                          ? 'text-[#3E3E3E]'
                          : 'text-[#3E3E3E]'
                      }`}>
                        LinkedIn
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.socialPlatforms.includes('linkedin')
                          ? 'text-[#5A67A5]'
                          : 'text-[#5A67A5]'
                      }`}>
                        Professional networking
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.socialPlatforms.includes('linkedin') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-[#5A67A5] rounded-full flex items-center justify-center">
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
                  type="checkbox" 
                  name="socialPlatforms" 
                  className="sr-only" 
                  value="twitter"
                  checked={formData.socialPlatforms.includes('twitter')}
                  onChange={handleInputChange}
                />
                <div className={`relative p-4 sm:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-300 transform hover:scale-[1.02] h-24 sm:h-32 flex flex-col justify-center cursor-pointer ${
                  formData.socialPlatforms.includes('twitter')
                    ? 'border-[#5A67A5] bg-[#E8EBF5] shadow-lg'
                    : 'border-[#D5D9E4] bg-[#FFFFFF] hover:border-[#A8B3D4] hover:bg-[#E8EBF5] hover:shadow-md'
                }`}>
                  <div className="flex items-center gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.socialPlatforms.includes('twitter')
                        ? 'bg-[#A8B3D4] text-[#5A67A5]'
                        : 'bg-[#E8EBF5] text-[#5A67A5]'
                    }`}>
                      <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="text-lg sm:text-xl" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                        <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.socialPlatforms.includes('twitter')
                          ? 'text-[#3E3E3E]'
                          : 'text-[#3E3E3E]'
                      }`}>
                        X/Twitter
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.socialPlatforms.includes('twitter')
                          ? 'text-[#5A67A5]'
                          : 'text-[#5A67A5]'
                        }`}>
                        Social media platform
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.socialPlatforms.includes('twitter') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-[#5A67A5] rounded-full flex items-center justify-center">
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
              <div className="p-2 bg-slate-100 rounded-xl">
                <FiX className="text-slate-600 text-lg" />
              </div>
              Exclude LLMs
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 ml-2">
                Optional
              </span>
            </h2>
            
            <div className="mb-6 p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-1">Speed Optimization</h3>
                  <p className="text-sm text-slate-600">
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
                    ? 'border-slate-400 bg-slate-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-start gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.excludedLLMs.includes('grok')
                        ? 'bg-slate-200 text-slate-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.excludedLLMs.includes('grok')
                          ? 'text-slate-700'
                          : 'text-slate-800'
                      }`}>
                        Grok
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.excludedLLMs.includes('grok')
                          ? 'text-slate-600'
                          : 'text-slate-500'
                      }`}>
                        AI-powered content
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.excludedLLMs.includes('grok') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-slate-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 sm:mt-3">
                    <div className={`text-xs font-medium px-2 py-1 rounded-full inline-block ${
                      formData.excludedLLMs.includes('grok')
                        ? 'bg-slate-200 text-slate-700'
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
                    ? 'border-slate-400 bg-slate-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-start gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.excludedLLMs.includes('o3')
                        ? 'bg-slate-200 text-slate-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.excludedLLMs.includes('o3')
                          ? 'text-slate-700'
                          : 'text-slate-800'
                      }`}>
                        o3
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.excludedLLMs.includes('o3')
                          ? 'text-slate-600'
                          : 'text-slate-500'
                      }`}>
                        Advanced language model
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.excludedLLMs.includes('o3') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-slate-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 sm:mt-3">
                    <div className={`text-xs font-medium px-2 py-1 rounded-full inline-block ${
                      formData.excludedLLMs.includes('o3')
                        ? 'bg-slate-200 text-slate-700'
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
                    ? 'border-slate-400 bg-slate-50 shadow-lg'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-md'
                }`}>
                  <div className="flex items-start gap-3 sm:gap-4">
                    <div className={`p-2 sm:p-3 rounded-lg sm:rounded-xl transition-colors duration-200 flex-shrink-0 ${
                      formData.excludedLLMs.includes('gemini')
                        ? 'bg-slate-200 text-slate-600'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold text-base sm:text-lg transition-colors duration-200 ${
                        formData.excludedLLMs.includes('gemini')
                          ? 'text-slate-700'
                          : 'text-slate-800'
                      }`}>
                        Gemini
                      </div>
                      <div className={`text-xs sm:text-sm mt-0.5 sm:mt-1 transition-colors duration-200 ${
                        formData.excludedLLMs.includes('gemini')
                          ? 'text-slate-600'
                          : 'text-slate-500'
                      }`}>
                        Google's latest AI model
                      </div>
                    </div>
                  </div>
                  
                  {/* Selection indicator */}
                  {formData.excludedLLMs.includes('gemini') && (
                    <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                      <div className="w-5 h-5 sm:w-6 sm:h-6 bg-slate-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 sm:mt-3">
                    <div className={`text-xs font-medium px-2 py-1 rounded-full inline-block ${
                      formData.excludedLLMs.includes('gemini')
                        ? 'bg-slate-200 text-slate-700'
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
                          value={formData.imageUrl}
                          onChange={handleInputChange}
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
                        {formData.imageUrl ? (
                          <div className="border-2 border-[#5A67A5] bg-[#E8EBF5] rounded-lg p-3 sm:p-4">
                            <div className="flex items-center gap-3">
                              <svg className="w-5 h-5 text-[#5A67A5]" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-[#3E3E3E]">Image uploaded successfully!</p>
                                <p className="text-xs text-[#5A67A5] truncate">{formData.imageUrl}</p>
                              </div>
                              <button
                                type="button"
                                onClick={() => setFormData(prev => ({ ...prev, imageUrl: '', imageFile: null }))}
                                className="text-[#5A67A5] hover:text-[#3E3E3E] transition-colors"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div 
                            className="border-2 border-dashed border-slate-300 rounded-lg p-3 sm:p-4 text-center hover:border-blue-400 transition-colors duration-200 cursor-pointer"
                            onClick={() => document.getElementById('fileInput').click()}
                          >
                            <svg className="w-6 h-6 sm:w-8 sm:h-8 text-slate-400 mx-auto mb-1 sm:mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                            </svg>
                            <p className="text-xs sm:text-sm text-slate-600 mb-1 sm:mb-2">Click to upload or drag and drop</p>
                            <p className="text-xs text-slate-500">PNG, JPG, GIF up to 10MB</p>
                            <input 
                              id="fileInput"
                              type="file" 
                              name="imageFile"
                              accept="image/*"
                              onChange={handleInputChange}
                              className="hidden"
                            />
                          </div>
                        )}
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
              className="px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-medium transition-all duration-300 shadow-sm hover:shadow-md text-sm sm:text-base bg-[#5A67A5] text-white hover:bg-[#4A5A95] disabled:opacity-50 disabled:cursor-not-allowed"
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
