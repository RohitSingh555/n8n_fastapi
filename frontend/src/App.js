import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import { FiSend, FiCheck, FiLinkedin, FiTwitter, FiImage, FiEdit3, FiEye } from 'react-icons/fi';

import Modal from './components/Modal';
import SuccessPage from './components/SuccessPage';
import TabContent from './components/TabContent';
import SocialMediaForm from './components/SocialMediaForm';
import logo from './assets/logo.png';
import API_BASE_URL from './config';



function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FeedbackForm />} />
        <Route path="/feedback/:submissionId" element={<FeedbackForm />} />
        <Route path="/feedback/:submissionId/:activeTab" element={<FeedbackForm />} />
        <Route path="/success/:submissionId" element={<SuccessPageWrapper />} />
        <Route path="/social-media" element={<SocialMediaForm />} />
      </Routes>
    </Router>
  );
}

function SuccessPageWrapper() {
  const { submissionId } = useParams();
  const navigate = useNavigate();
  
  const handleReset = () => {
    navigate('/');
  };
  
  const handleContinueEditing = () => {
    navigate(`/feedback/${submissionId}`);
  };
  
  return (
    <SuccessPage 
      submissionId={submissionId}
      onReset={handleReset}
      onContinueEditing={handleContinueEditing}
    />
  );
}

function FeedbackForm() {
  const { submissionId: urlSubmissionId, activeTab: urlActiveTab } = useParams();
  const navigate = useNavigate();
  
  const initialFormData = {
    n8n_execution_id: '',
    email: '',
    
    linkedin_grok_content: `What if AI could transform prenatal care into a lifeline for millions?

At Ultrasound AI, we're making that vision a reality. Our cutting-edge technology empowers healthcare providers with tools to predict and address critical maternal health challenges, ensuring better outcomes for women and families worldwide. By combining scientific expertise with compassionate innovation, we're breaking barriers to accessible care.

Our mission is clear: to advance women's health with solutions that are equitable, impactful, and inclusive. Every day, we strive to create a future where personalized care is not a luxury, but a standard—regardless of location or circumstance.

How do you see AI shaping the future of healthcare? Let's start a conversation in the comments. #WomensHealth #AIInnovation #PrenatalCare #UltrasoundAI #HealthcareTech`,
    
    linkedin_o3_content: `What if your next ultrasound could learn from millions of others—and put that knowledge to work for you?

At Ultrasound AI, we train our algorithms on diverse, global datasets so every expecting parent benefits from the most inclusive insights available. By detecting subtle patterns that traditional methods miss, our AI elevates prenatal care from reactive to proactive, helping clinicians personalize plans long before complications arise.

We believe equitable access starts with equitable data. That's why our team of scientists, physicians, and technologists collaborates across continents to ensure accuracy for every body, every background, every community. Personalized care isn't just the future—it's happening now, one ultrasound at a time.

How is data diversity shaping your approach to innovation? Share your thoughts below. #PrenatalCare #AIInnovation #HealthEquity #UltrasoundAI`,
    
    linkedin_gemini_content: `What if every clinician had a co-pilot in the exam room?

Our AI is designed to be just that. It analyzes complex data in real-time, flagging potential risks and offering data-driven insights that support clinical decisions. This frees our healthcare heroes to do what they do best: connect with patients and provide compassionate, expert care.

Technology should augment expertise, not replace it. At Ultrasound AI, we're building tools that empower providers, strengthen the doctor-patient relationship, and ultimately lead to safer pregnancies.

To all the healthcare providers out there: what's the biggest challenge AI could help you solve? #UltrasoundAI #AIinMedicine #ClinicalSupport #FutureOfHealth #DigitalHealth #PhysicianBurnout`,
    
    linkedin_feedback: null,
    linkedin_chosen_llm: null,
    linkedin_custom_content: null,
    
    // X Content
    x_grok_content: 'Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...',
    x_o3_content: 'Sample X/Twitter o3 content would appear here...',
    x_gemini_content: 'Sample X/Twitter Gemini content would appear here...',
    x_feedback: null,
    x_chosen_llm: null,
    x_custom_content: null,
    
    // Image URLs
    stable_diffusion_image_url: 'https://example.com/stable-diffusion-image.jpg',
    pixabay_image_url: 'https://example.com/pixabay-image.jpg',
    gpt1_image_url: 'https://example.com/gpt1-image.jpg',
    image_feedback: null,
    image_chosen_llm: null,
    
    // Additional image fields for feedback form
    image_url: '',
    uploaded_image_url: '',
    
    // Separate Image LLM selections for platforms
    linkedin_image_llm: null,
    twitter_image_llm: null
  };

  const [formData, setFormData] = useState(initialFormData);
  const [loading, setLoading] = useState(false);
  const [modal, setModal] = useState({ isOpen: false, title: '', message: '', type: 'info' });
  const [isEditMode, setIsEditMode] = useState(false);
  const [submissionId, setSubmissionId] = useState('');
  const [activeTab, setActiveTab] = useState('linkedin');
  const [visitedTabs, setVisitedTabs] = useState(new Set(['linkedin']));
  const [tabValidation, setTabValidation] = useState({
    linkedin: false,
    twitter: false,
    images: false
  });
  const [webhookLoading, setWebhookLoading] = useState(false);
  const [webhookStatus, setWebhookStatus] = useState(null);

  // Check if tabs have content
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
           formData.gpt1_image_url?.trim() ||
           formData.image_url?.trim() ||
           formData.uploaded_image_url?.trim();
  };

  // Get available tabs
  const getAvailableTabs = () => {
    const tabs = [];
    if (hasLinkedInContent()) tabs.push('linkedin');
    if (hasTwitterContent()) tabs.push('twitter');
    if (hasImageContent()) tabs.push('images');
    return tabs;
  };



  // Load feedback from URL if submissionId is provided
  useEffect(() => {
    if (urlSubmissionId && urlSubmissionId !== submissionId) {
      loadExistingFeedback(urlSubmissionId);
    }
    if (urlActiveTab && ['linkedin', 'twitter', 'images'].includes(urlActiveTab)) {
      setActiveTab(urlActiveTab);
      setVisitedTabs(prev => new Set([...prev, urlActiveTab]));
    }
  }, [urlSubmissionId, urlActiveTab]);

  // Auto-clear form fields on page load to show the mutual exclusion notice
  useEffect(() => {
    // Only auto-clear if we're not in edit mode and no submission ID
    if (!isEditMode && !submissionId) {
      // Simulate clicking the "Clear All" button for LinkedIn tab
      setFormData(prev => ({
        ...prev,
        linkedin_feedback: null,
        linkedin_chosen_llm: null,
        linkedin_custom_content: null,
        x_feedback: null,
        x_chosen_llm: null,
        x_custom_content: null,
        image_feedback: null,
        image_chosen_llm: null
      }));
    }
  }, []); // Empty dependency array means this runs once on mount

  useEffect(() => {
    console.log('URL update effect triggered:', { submissionId, activeTab });
    if (submissionId) {
      if (activeTab === 'linkedin') {
        navigate(`/feedback/${submissionId}`);
      } else {
        navigate(`/feedback/${submissionId}/${activeTab}`);
      }
    } else {
      navigate('/');
    }
  }, [submissionId, activeTab, navigate]);

  // Validate tab completion
  const validateTab = useCallback((tabName) => {
    switch (tabName) {
      case 'linkedin':
        // For LinkedIn, exactly one of the three fields should be filled (mutual exclusion)
        const linkedinFields = [
          formData.linkedin_feedback,
          formData.linkedin_chosen_llm,
          formData.linkedin_custom_content
        ];
        const filledLinkedInFields = linkedinFields.filter(field => field && field.trim() !== '');
        return filledLinkedInFields.length === 1;
      case 'twitter':
        // For Twitter, exactly one of the three fields should be filled (mutual exclusion)
        const twitterFields = [
          formData.x_feedback,
          formData.x_chosen_llm,
          formData.x_custom_content
        ];
        const filledTwitterFields = twitterFields.filter(field => field && field.trim() !== '');
        return filledTwitterFields.length === 1;
      case 'images':
        // For Images, exactly one of the three fields should be filled (mutual exclusion)
        const imageFields = [
          formData.image_feedback,
          formData.linkedin_image_llm,
          formData.twitter_image_llm
        ];
        const filledImageFields = imageFields.filter(field => field && field.trim() !== '');
        return filledImageFields.length === 1;
      default:
        return false;
    }
  }, [formData]);

  // Enhanced validation with detailed error messages
  const validateForm = useCallback(() => {
    const errors = [];
    
    // Required field validation
    if (!formData.n8n_execution_id?.trim()) {
      errors.push({ field: 'n8n_execution_id', message: 'N8N Execution ID is required' });
    }
    
    if (!formData.email?.trim()) {
      errors.push({ field: 'email', message: 'Email is required' });
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.push({ field: 'email', message: 'Please enter a valid email address' });
    }
    
    // Tab-specific validation
    const availableTabs = getAvailableTabs();
    
    if (availableTabs.includes('linkedin')) {
      const linkedinFields = [
        formData.linkedin_feedback,
        formData.linkedin_chosen_llm,
        formData.linkedin_custom_content
      ];
      const filledLinkedInFields = linkedinFields.filter(field => field && field.trim() !== '');
      
      if (filledLinkedInFields.length === 0) {
        errors.push({ field: 'linkedin', message: 'LinkedIn tab: Please provide feedback, select an LLM, or enter custom content' });
      } else if (filledLinkedInFields.length > 1) {
        errors.push({ field: 'linkedin', message: 'LinkedIn tab: Only one feedback method can be used at a time' });
      }
    }
    
    if (availableTabs.includes('twitter')) {
      const twitterFields = [
        formData.x_feedback,
        formData.x_chosen_llm,
        formData.x_custom_content
      ];
      const filledTwitterFields = twitterFields.filter(field => field && field.trim() !== '');
      
      if (filledTwitterFields.length === 0) {
        errors.push({ field: 'twitter', message: 'Twitter tab: Please provide feedback, select an LLM, or enter custom content' });
      } else if (filledTwitterFields.length > 1) {
        errors.push({ field: 'twitter', message: 'Twitter tab: Only one feedback method can be used at a time' });
      }
    }
    
    if (availableTabs.includes('images')) {
      const imageFields = [
        formData.image_feedback,
        formData.linkedin_image_llm,
        formData.twitter_image_llm
      ];
      const filledImageFields = imageFields.filter(field => field && field.trim() !== '');
      
      if (filledImageFields.length === 0) {
        errors.push({ field: 'images', message: 'Images tab: Please provide feedback or select image LLMs' });
      } else if (filledImageFields.length > 1) {
        errors.push({ field: 'images', message: 'Images tab: Only one feedback method can be used at a time' });
      }
    }
    
    return errors;
  }, [formData]);

  // Helper function to get user-friendly error messages
  const getErrorMessage = (error) => {
    if (typeof error === 'string') {
      return error;
    }
    
    if (error.message) {
      return error.message;
    }
    
    if (error.detail) {
      return error.detail;
    }
    
    return 'An unexpected error occurred. Please try again.';
  };

  // Field-level validation state
  const [fieldErrors, setFieldErrors] = useState({});
  const [formErrors, setFormErrors] = useState([]);

  // Clear field errors when user starts typing
  const clearFieldError = (fieldName) => {
    setFieldErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  };

  // Enhanced input change handler with validation
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Clear field error when user starts typing
    clearFieldError(name);
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Validate specific field
  const validateField = (fieldName, value) => {
    const errors = {};
    
    switch (fieldName) {
      case 'email':
        if (!value?.trim()) {
          errors[fieldName] = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors[fieldName] = 'Please enter a valid email address';
        }
        break;
      case 'n8n_execution_id':
        if (!value?.trim()) {
          errors[fieldName] = 'N8N Execution ID is required';
        }
        break;
      default:
        break;
    }
    
    return errors;
  };

  // Handle field blur for validation
  const handleFieldBlur = (e) => {
    const { name, value } = e.target;
    const fieldErrors = validateField(name, value);
    
    if (Object.keys(fieldErrors).length > 0) {
      setFieldErrors(prev => ({ ...prev, ...fieldErrors }));
    }
  };

  // Update tab validation when form data changes
  useEffect(() => {
    const linkedinValid = validateTab('linkedin');
    const twitterValid = validateTab('twitter');
    const imagesValid = validateTab('images');
    
    setTabValidation({
      linkedin: linkedinValid,
      twitter: twitterValid,
      images: imagesValid
    });
  }, [formData, validateTab]);

  const handleTabChange = useCallback((newTab) => {
    console.log('Tab change requested:', newTab, 'Current tab:', activeTab);
    if (!canAccessTab(newTab)) {
      console.log('Tab access denied for:', newTab);
      return;
    }
    
    // Mark current tab as visited
    setVisitedTabs(prev => new Set([...prev, activeTab, newTab]));
    setActiveTab(newTab);
    console.log('Tab changed to:', newTab);
  }, [activeTab]);

  const canSubmit = () => {
    // Check if form has validation errors
    if (formErrors.length > 0) {
      return false;
    }
    
    // Check if required fields are filled
    if (!formData.n8n_execution_id?.trim() || !formData.email?.trim()) {
      return false;
    }
    
    // Check if at least one tab has valid content
    const availableTabs = getAvailableTabs();
    if (availableTabs.length === 0) {
      return false;
    }
    
    // Check if each available tab has exactly one field filled
    for (const tab of availableTabs) {
      if (!validateTab(tab)) {
        return false;
      }
    }
    
    return true;
  };

  const canAccessTab = useCallback((tabName) => {
    // Always allow access to all tabs for new submissions and edit mode
    return true;
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous errors
    setFormErrors([]);
    setFieldErrors({});
    
    // Validate form before submission
    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setFormErrors(validationErrors);
      
      // Show first error in modal
      setModal({
        isOpen: true,
        title: 'Validation Error',
        message: validationErrors[0].message,
        type: 'error'
      });
      return;
    }
    
    setLoading(true);

    try {
      let response;
      let data;
      
      if (isEditMode && submissionId) {
        // Update existing feedback
        console.log('Sending PUT request to:', `${API_BASE_URL}/api/feedback/${submissionId}`);
        console.log('Form data being sent:', formData);
        
        // Filter out database-specific fields that shouldn't be in the update request
        const updateData = { ...formData };
        delete updateData.id;
        delete updateData.submission_id;
        delete updateData.created_at;
        delete updateData.updated_at;
        
        console.log('Filtered update data:', updateData);
        
        response = await fetch(`${API_BASE_URL}/api/feedback/${submissionId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updateData)
        });
        
        if (!response.ok) {
          console.error('PUT request failed:', response.status, response.statusText);
          const errorText = await response.text();
          console.error('Error response:', errorText);
          throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        data = await response.json();
        
        // Submit updated feedback to webhook
        try {
          setWebhookStatus({
            type: 'info',
            message: 'Feedback updated successfully!',
            details: 'Now sending to webhook...'
          });
          
          const webhookResponse = await fetch(`${API_BASE_URL}/api/submit-feedback-webhook`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ submission_id: submissionId })
          });
          
          if (webhookResponse.ok) {
            const result = await webhookResponse.json();
            setWebhookStatus({
              type: 'success',
              message: 'Webhook submitted successfully!',
              details: result.message
            });
          } else {
            const errorData = await webhookResponse.json();
            setWebhookStatus({
              type: 'error',
              message: 'Webhook submission failed',
              details: errorData.detail || 'Unknown error occurred'
            });
          }
        } catch (webhookError) {
          console.warn('Webhook submission failed:', webhookError);
          setWebhookStatus({
            type: 'error',
            message: 'Webhook submission failed',
            details: webhookError.message || 'Network error occurred'
          });
        }
        
        setModal({
          isOpen: true,
          title: 'Success!',
          message: `Feedback updated successfully! Submission ID: ${data.submission_id}`,
          type: 'success'
        });
      } else {
        // Create new feedback submission
        response = await fetch(`${API_BASE_URL}/api/feedback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
          let errorMessage = `HTTP error! status: ${response.status}`;
          try {
            const errorData = await response.json();
            if (errorData.detail) {
              errorMessage = errorData.detail;
            } else if (errorData.message) {
              errorMessage = errorData.message;
            }
          } catch (e) {
            // If we can't parse JSON, use the status text
            errorMessage = response.statusText || errorMessage;
          }
          throw new Error(errorMessage);
        }
        
        data = await response.json();
        
        // Submit new feedback to webhook
        try {
          setWebhookStatus({
            type: 'info',
            message: 'Feedback submitted successfully!',
            details: 'Now sending to webhook...'
          });
          
          const webhookResponse = await fetch(`${API_BASE_URL}/api/submit-feedback-webhook`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ submission_id: data.submission_id })
          });
          
          if (webhookResponse.ok) {
            const result = await webhookResponse.json();
            setWebhookStatus({
              type: 'success',
              message: 'Webhook submitted successfully!',
              details: result.message
            });
          } else {
            const errorData = await webhookResponse.json();
            setWebhookStatus({
              type: 'error',
              message: 'Webhook submission failed',
              details: errorData.detail || 'Unknown error occurred'
            });
          }
        } catch (webhookError) {
          console.warn('Webhook submission failed:', webhookError);
          setWebhookStatus({
            type: 'error',
            message: 'Webhook submission failed',
            details: webhookError.message || 'Network error occurred'
          });
        }
        
        setModal({
          isOpen: true,
          title: 'Success!',
          message: `Feedback submitted successfully! Submission ID: ${data.submission_id}`,
          type: 'success'
        });
      }
      
      // Navigate to success page after a short delay
      setTimeout(() => {
        navigate(`/success/${data.submission_id}`);
      }, 2000);
      
    } catch (error) {
      setModal({
        isOpen: true,
        title: 'Error',
        message: getErrorMessage(error),
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadExistingFeedback = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/feedback/${id}`);
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          }
        } catch (e) {
          // If we can't parse JSON, use the status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }
      const data = await response.json();
      setFormData(data);
      setSubmissionId(id);
      setIsEditMode(true);
      setVisitedTabs(new Set(['linkedin', 'twitter', 'images'])); // Mark all tabs as visited for existing feedback
      // Removed success modal - only show success when submitting feedback
    } catch (error) {
      setModal({
        isOpen: true,
        title: 'Error',
        message: getErrorMessage(error),
        type: 'error'
      });
    }
  };

  const handleWebhookSubmit = async () => {
    setWebhookLoading(true);
    setWebhookStatus(null);
    
    try {
      let currentSubmissionId = submissionId;
      
      // If no submission ID exists, we need to create a new submission first
      if (!currentSubmissionId) {
        setWebhookStatus({
          type: 'info',
          message: 'Saving feedback first...',
          details: 'Creating new feedback submission before sending to webhook.'
        });
        
        // Create new feedback submission
        const createResponse = await fetch(`${API_BASE_URL}/api/feedback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        });
        
        if (!createResponse.ok) {
          throw new Error(`Failed to create feedback: ${createResponse.status}`);
        }
        
        const createResult = await createResponse.json();
        currentSubmissionId = createResult.submission_id;
        setSubmissionId(currentSubmissionId);
        
        setWebhookStatus({
          type: 'info',
          message: 'Feedback saved successfully!',
          details: 'Now sending to webhook...'
        });
      } else {
        // Update existing feedback submission
        setWebhookStatus({
          type: 'info',
          message: 'Updating feedback first...',
          details: 'Saving changes before sending to webhook.'
        });
        
                 // Filter out database-specific fields for the update request
         const updateData = { ...formData };
         delete updateData.id;
         delete updateData.submission_id;
         delete updateData.created_at;
         delete updateData.updated_at;
         
         const updateResponse = await fetch(`${API_BASE_URL}/api/feedback/${currentSubmissionId}`, {
           method: 'PUT',
           headers: {
             'Content-Type': 'application/json',
           },
           body: JSON.stringify(updateData)
         });
        
        if (!updateResponse.ok) {
          throw new Error(`Failed to update feedback: ${updateResponse.status}`);
        }
        
        setWebhookStatus({
          type: 'info',
          message: 'Feedback updated successfully!',
          details: 'Now sending to webhook...'
        });
      }
      
      // Now send to webhook
      const webhookResponse = await fetch(`${API_BASE_URL}/api/submit-feedback-webhook`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ submission_id: currentSubmissionId })
      });
      
      if (webhookResponse.ok) {
        const result = await webhookResponse.json();
        setWebhookStatus({
          type: 'success',
          message: 'Webhook submitted successfully!',
          details: result.message
        });
      } else {
        const errorData = await webhookResponse.json();
        setWebhookStatus({
          type: 'error',
          message: 'Webhook submission failed',
          details: errorData.detail || 'Unknown error occurred'
        });
      }
    } catch (error) {
      setWebhookStatus({
        type: 'error',
        message: 'Webhook submission failed',
        details: error.message || 'Network error occurred'
      });
    } finally {
      setWebhookLoading(false);
    }
  };

  const TabButton = useCallback(({ id, label, icon: Icon, isActive, isCompleted, isVisited, isEditMode }) => {
    const canAccess = canAccessTab(id);
    
    console.log('TabButton render:', id, 'isActive:', isActive, 'canAccess:', canAccess);
    
    // Always show all tabs so users can access all form fields
    
    return (
      <button
        onClick={() => handleTabChange(id)}
        disabled={!canAccess}
        className={`flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 sm:py-3 rounded-xl font-medium transition-all duration-300 text-xs sm:text-sm whitespace-nowrap ${
          isActive 
            ? 'bg-[#5A67A5] text-white shadow-md' 
            : isCompleted
            ? 'bg-[#E8EBF5] text-[#5A67A5] border border-[#A8B3D4] hover:bg-[#D5D9E4]'
            : canAccess
            ? 'text-[#5A67A5] hover:text-[#3E3E3E] hover:bg-[#E8EBF5]'
            : 'text-[#A8B3D4] bg-[#E8EBF5] cursor-not-allowed'
        }`}
      >
        <Icon className="text-sm sm:text-lg" />
        <span className="hidden sm:inline">{label}</span>
        <span className="sm:hidden">{label.split(' ')[0]}</span>
        {isCompleted && <FiCheck className="text-[#5A67A5] text-xs sm:text-sm" />}
        {!canAccess && <FiEye className="text-[#A8B3D4] text-xs sm:text-sm" />}
      </button>
    );
  }, [canAccessTab, handleTabChange]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#E8EBF5] to-[#A8B3D4]">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div className="max-w-7xl mx-auto">
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
              n8n Execution Feedback
            </h1>
            <p className="text-[#5A67A5] text-sm sm:text-base lg:text-lg max-w-4xl mx-auto px-4 animate-fade-in-delay">
              Collect and manage feedback for n8n execution results
            </p>
            <div className="flex justify-center gap-4 mt-6">
              <button 
                onClick={() => navigate('/')}
                className="px-4 py-2 bg-[#5A67A5] text-white rounded-xl hover:bg-[#4A5A95] transition-all duration-200 text-sm shadow-md"
              >
                Feedback Form
              </button>
              <button 
                onClick={() => navigate('/social-media')}
                className="px-4 py-2 bg-[#A8B3D4] text-[#3E3E3E] rounded-xl hover:bg-[#9BA6C7] transition-all duration-200 text-sm"
              >
                Social Media Form
              </button>
            </div>
          </header>

          {/* Load Existing Feedback / Create New */}
          <div className="bg-[#FFFFFF] border border-[#D5D9E4] rounded-2xl p-4 sm:p-6 mb-6 sm:mb-8 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex items-center gap-3 sm:gap-4">
                <div className="p-2 bg-[#E8EBF5] rounded-xl">
                  {isEditMode ? <FiEdit3 className="text-[#5A67A5] text-lg" /> : <FiEye className="text-[#5A67A5] text-lg" />}
                </div>
                <div className="flex-1">
                  <h3 className="text-base sm:text-lg font-medium text-[#3E3E3E] mb-1 sm:mb-2">
                    {isEditMode ? 'Editing Existing Feedback' : 'Load Existing Feedback'}
                  </h3>
                  <p className="text-[#5A67A5] text-xs sm:text-sm">
                    {isEditMode 
                      ? `Currently editing feedback with ID: ${submissionId}` 
                      : 'Enter a submission ID to load and edit existing feedback'
                    }
                  </p>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                {!isEditMode ? (
                  <>
                    <input
                      type="text"
                      placeholder="Enter submission ID"
                      className="bg-[#E8EBF5] border border-[#D5D9E4] rounded-xl px-3 sm:px-4 py-2 text-[#3E3E3E] placeholder-[#5A67A5] focus:outline-none focus:ring-2 focus:ring-[#5A67A5] focus:border-[#5A67A5] transition-all duration-200 text-sm sm:text-base"
                      onChange={(e) => setSubmissionId(e.target.value)}
                    />
                    <button
                      onClick={() => loadExistingFeedback(submissionId)}
                      className="bg-[#5A67A5] text-white px-4 py-2 rounded-xl hover:bg-[#4A5A95] transition-all duration-200 text-sm sm:text-base"
                    >
                      Load
                    </button>
                  </>
                ) : (
                  <div className="text-emerald-600 text-sm font-medium">
                    ✓ Feedback loaded successfully
                  </div>
                )}
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8">
            {/* Basic Information */}
            <div className="bg-[#FFFFFF] border border-[#D5D9E4] rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
              <h2 className="text-xl sm:text-2xl font-medium text-[#3E3E3E] mb-4 sm:mb-6 flex items-center gap-3">
                <div className="p-2 bg-[#E8EBF5] rounded-xl">
                  <FiEdit3 className="text-[#5A67A5] text-lg" />
                </div>
                Basic Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                <div>
                  <label className="block text-[#3E3E3E] font-medium mb-2 text-sm sm:text-base">
                    n8n Execution ID <span className="text-[#5A67A5] text-xs sm:text-sm">(Read-only)</span>
                  </label>
                  <input
                    type="text"
                    name="n8n_execution_id"
                    value={formData.n8n_execution_id}
                    readOnly
                    className={`w-full bg-[#E8EBF5] border rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-[#5A67A5] cursor-not-allowed text-sm sm:text-base ${
                      fieldErrors.n8n_execution_id ? 'border-red-300' : 'border-[#D5D9E4]'
                    }`}
                    placeholder="Execution ID will be loaded automatically"
                  />
                  {fieldErrors.n8n_execution_id && (
                    <p className="mt-1 text-red-500 text-xs">{fieldErrors.n8n_execution_id}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-[#3E3E3E] font-medium mb-2 text-sm sm:text-base">
                    Email <span className="text-[#5A67A5] text-xs sm:text-sm">(Read-only)</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    readOnly
                    className={`w-full bg-[#E8EBF5] border rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-[#5A67A5] cursor-not-allowed text-sm sm:text-base ${
                      fieldErrors.email ? 'border-red-300' : 'border-[#D5D9E4]'
                    }`}
                    placeholder="Email will be loaded automatically"
                  />
                  {fieldErrors.email && (
                    <p className="mt-1 text-red-500 text-xs">{fieldErrors.email}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Form Validation Errors */}
            {formErrors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-2xl p-4 sm:p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-red-100 rounded-xl">
                    <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-red-800">Please fix the following issues:</h3>
                </div>
                <ul className="space-y-2">
                  {formErrors.map((error, index) => (
                    <li key={index} className="flex items-start gap-2 text-red-700">
                      <span className="text-red-500 mt-1">•</span>
                      <span>{error.message}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Content Tabs */}
            <div className="bg-[#FFFFFF] border border-[#D5D9E4] rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
              <div className="sticky top-0 z-10 bg-[#FFFFFF] border-b border-[#D5D9E4] -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-4 mb-6 sm:mb-8">
                <div className="flex gap-2 overflow-x-auto pb-2">
                  <TabButton 
                    id="linkedin" 
                    label="LinkedIn Content" 
                    icon={FiLinkedin} 
                    isActive={activeTab === 'linkedin'}
                    isCompleted={tabValidation.linkedin}
                    isVisited={visitedTabs.has('linkedin')}
                    isEditMode={isEditMode}
                  />
                  <TabButton 
                    id="twitter" 
                    label="X/Twitter Content" 
                    icon={FiTwitter} 
                    isActive={activeTab === 'twitter'}
                    isCompleted={tabValidation.twitter}
                    isVisited={visitedTabs.has('twitter')}
                    isEditMode={isEditMode}
                  />
                  <TabButton 
                    id="images" 
                    label="Generated Images" 
                    icon={FiImage} 
                    isActive={activeTab === 'images'}
                    isCompleted={tabValidation.images}
                    isVisited={visitedTabs.has('images')}
                    isEditMode={isEditMode}
                  />
                </div>
              </div>

              {/* Tab Content */}
              <TabContent
                activeTab={activeTab}
                formData={formData}
                handleInputChange={handleInputChange}
                handleFieldBlur={handleFieldBlur}
                fieldErrors={fieldErrors}
                tabValidation={tabValidation}
                isEditMode={isEditMode}
              />
            </div>

            {/* Submit Button - Now handles both saving and webhook submission */}
            <div className="text-center">
              {formErrors.length > 0 ? (
                <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-sm">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span className="font-medium">Please fix validation errors above before submitting</span>
                  </div>
                </div>
              ) : canSubmit() && !loading ? (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-xl text-green-800 text-sm">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="font-medium">Form is ready to submit!</span>
                  </div>
                </div>
              ) : null}
              
              <button
                type="submit"
                disabled={loading || !canSubmit()}
                className={`px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-medium transition-all duration-300 shadow-sm hover:shadow-md text-sm sm:text-base ${
                  canSubmit()
                    ? 'bg-[#5A67A5] text-white hover:bg-[#4A5A95]'
                    : 'bg-[#D5D9E4] text-[#A8B3D4] cursor-not-allowed'
                }`}
              >
                {loading ? (
                  <div className="flex items-center gap-3">
                    <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-b-2 border-white"></div>
                    <span>Submitting...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-3">
                    <FiSend />
                    <span>{isEditMode ? 'Update Feedback & Submit to Webhook' : 'Submit Feedback & Send to Webhook'}</span>
                  </div>
                )}
              </button>
              
              {/* Webhook Status - Show for both new submissions and updates */}
              {webhookStatus && (
                <div className={`mt-4 p-3 rounded-lg text-sm max-w-md mx-auto ${
                  webhookStatus.type === 'success' 
                    ? 'bg-green-100 text-green-800 border border-green-200' 
                    : webhookStatus.type === 'info'
                    ? 'bg-blue-100 text-blue-800 border border-blue-200'
                    : 'bg-red-100 text-red-800 border border-red-200'
                }`}>
                  <div className="font-medium">{webhookStatus.message}</div>
                  {webhookStatus.details && (
                    <div className="mt-1 opacity-80">{webhookStatus.details}</div>
                  )}
                </div>
              )}
            </div>
          </form>
        </div>
      </div>

      {/* Modal */}
      <Modal
        isOpen={modal.isOpen}
        onClose={() => setModal({ ...modal, isOpen: false })}
        title={modal.title}
        message={modal.message}
        type={modal.type}
      />
    </div>
  );
}

export default App; 