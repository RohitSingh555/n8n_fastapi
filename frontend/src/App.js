import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import { FiSend, FiCheck, FiAlertCircle, FiLinkedin, FiTwitter, FiImage, FiEdit3, FiPlus, FiEye, FiLock, FiUnlock } from 'react-icons/fi';
import axios from 'axios';

// Import modular components
import Modal from './components/Modal';
import SuccessPage from './components/SuccessPage';
import TabContent from './components/TabContent';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FeedbackForm />} />
        <Route path="/feedback/:submissionId" element={<FeedbackForm />} />
        <Route path="/feedback/:submissionId/:activeTab" element={<FeedbackForm />} />
        <Route path="/success/:submissionId" element={<SuccessPageWrapper />} />
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
  
  // Initial prefilled state
  const initialFormData = {
    n8n_execution_id: '',
    email: '',
    
    // LinkedIn Content
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
    
    linkedin_feedback: '',
    linkedin_chosen_llm: '',
    linkedin_custom_content: '',
    
    // X Content
    x_grok_content: 'Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...Sample X/Twitter Grok content would appear here...',
    x_o3_content: 'Sample X/Twitter o3 content would appear here...',
    x_gemini_content: 'Sample X/Twitter Gemini content would appear here...',
    x_feedback: '',
    x_chosen_llm: '',
    x_custom_content: '',
    
    // Image URLs
    stable_diffusion_image_url: 'https://example.com/stable-diffusion-image.jpg',
    pixabay_image_url: 'https://example.com/pixabay-image.jpg',
    gpt1_image_url: 'https://example.com/gpt1-image.jpg',
    image_feedback: '',
    image_chosen_llm: ''
  };

  const [formData, setFormData] = useState(initialFormData);
  const [originalFormData, setOriginalFormData] = useState(initialFormData);
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
           formData.gpt1_image_url?.trim();
  };

  // Get available tabs
  const getAvailableTabs = () => {
    const tabs = [];
    if (hasLinkedInContent()) tabs.push('linkedin');
    if (hasTwitterContent()) tabs.push('twitter');
    if (hasImageContent()) tabs.push('images');
    return tabs;
  };

  // Check if any field has been modified from its original state
  const hasChanges = () => {
    const editableFields = [
      'email', 'linkedin_feedback', 'linkedin_chosen_llm', 'linkedin_custom_content',
      'x_feedback', 'x_chosen_llm', 'x_custom_content',
      'image_feedback', 'image_chosen_llm'
    ];
    
    return editableFields.some(field => {
      const currentValue = formData[field] || '';
      const originalValue = originalFormData[field] || '';
      return currentValue !== originalValue;
    });
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

  // Auto-select LLM based on available content
  useEffect(() => {
    const autoSelectLLM = () => {
      const updatedFormData = { ...formData };
      
      // LinkedIn auto-selection
      if (!formData.linkedin_chosen_llm) {
        if (formData.linkedin_grok_content?.trim()) {
          updatedFormData.linkedin_chosen_llm = 'Grok';
        } else if (formData.linkedin_o3_content?.trim()) {
          updatedFormData.linkedin_chosen_llm = 'o3';
        } else if (formData.linkedin_gemini_content?.trim()) {
          updatedFormData.linkedin_chosen_llm = 'Gemini';
        }
      }
      
      // Twitter auto-selection
      if (!formData.x_chosen_llm) {
        if (formData.x_grok_content?.trim()) {
          updatedFormData.x_chosen_llm = 'Grok';
        } else if (formData.x_o3_content?.trim()) {
          updatedFormData.x_chosen_llm = 'o3';
        } else if (formData.x_gemini_content?.trim()) {
          updatedFormData.x_chosen_llm = 'Gemini';
        }
      }
      
      // Image auto-selection
      if (!formData.image_chosen_llm) {
        if (formData.stable_diffusion_image_url?.trim()) {
          updatedFormData.image_chosen_llm = 'Stable';
        } else if (formData.pixabay_image_url?.trim()) {
          updatedFormData.image_chosen_llm = 'Pixabay';
        } else if (formData.gpt1_image_url?.trim()) {
          updatedFormData.image_chosen_llm = 'GPT1';
        }
      }
      
      // Only update if there are changes
      if (JSON.stringify(updatedFormData) !== JSON.stringify(formData)) {
        setFormData(updatedFormData);
      }
    };
    
    autoSelectLLM();
  }, [formData.linkedin_grok_content, formData.linkedin_o3_content, formData.linkedin_gemini_content, 
      formData.x_grok_content, formData.x_o3_content, formData.x_gemini_content,
      formData.stable_diffusion_image_url, formData.pixabay_image_url, formData.gpt1_image_url]);

  // Update URL when tab or submissionId changes
  useEffect(() => {
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
  const validateTab = (tabName) => {
    switch (tabName) {
      case 'linkedin':
        return formData.linkedin_feedback.trim() !== '' && formData.linkedin_chosen_llm !== '';
      case 'twitter':
        return formData.x_feedback.trim() !== '' && formData.x_chosen_llm !== '';
      case 'images':
        return formData.image_feedback.trim() !== '' && formData.image_chosen_llm !== '';
      default:
        return false;
    }
  };

  // Update tab validation when form data changes
  useEffect(() => {
    setTabValidation({
      linkedin: validateTab('linkedin'),
      twitter: validateTab('twitter'),
      images: validateTab('images')
    });
  }, [formData]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTabChange = (newTab) => {
    if (!canAccessTab(newTab)) return;
    
    // Mark current tab as visited
    setVisitedTabs(prev => new Set([...prev, activeTab, newTab]));
    setActiveTab(newTab);
  };

  const canSubmit = () => {
    // Always enable submit button
    return true;
  };

  const canAccessTab = (tabName) => {
    // If in edit mode, allow access to all tabs
    if (isEditMode) return true;
    
    // For new submissions, allow access to all tabs
    const availableTabs = getAvailableTabs();
    return availableTabs.includes(tabName);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);

    try {
      const response = await axios.put(`/api/feedback/${submissionId}`, formData);
      setModal({
        isOpen: true,
        title: 'Success!',
        message: `Feedback submitted successfully! Submission ID: ${response.data.submission_id}`,
        type: 'success'
      });
      
      // Navigate to success page after a short delay
      setTimeout(() => {
        navigate(`/success/${response.data.submission_id}`);
      }, 2000);
      
    } catch (error) {
      setModal({
        isOpen: true,
        title: 'Error',
        message: error.response?.data?.detail || 'Failed to submit feedback. Please try again.',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadExistingFeedback = async (id) => {
    try {
      const response = await axios.get(`/api/feedback/${id}`);
      setFormData(response.data);
      setOriginalFormData(response.data); // Store original state for comparison
      setSubmissionId(id);
      setIsEditMode(true);
      setVisitedTabs(new Set(['linkedin', 'twitter', 'images'])); // Mark all tabs as visited for existing feedback
      // Removed success modal - only show success when submitting feedback
    } catch (error) {
      setModal({
        isOpen: true,
        title: 'Error',
        message: error.response?.data?.detail || 'Failed to load feedback. Please check the ID.',
        type: 'error'
      });
    }
  };

  const TabButton = ({ id, label, icon: Icon, isActive, isCompleted, isVisited }) => {
    const canAccess = canAccessTab(id);
    const availableTabs = getAvailableTabs();
    
    // Don't render if tab has no content
    if (!availableTabs.includes(id)) return null;
    
    return (
      <button
        onClick={() => handleTabChange(id)}
        disabled={!canAccess}
        className={`flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 sm:py-3 rounded-xl font-medium transition-all duration-300 text-xs sm:text-sm whitespace-nowrap ${
          isActive 
            ? 'bg-slate-800 text-white shadow-md' 
            : isCompleted
            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200 hover:bg-emerald-200'
            : canAccess
            ? 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
            : 'text-slate-400 bg-slate-100 cursor-not-allowed'
        }`}
      >
        <Icon className="text-sm sm:text-lg" />
        <span className="hidden sm:inline">{label}</span>
        <span className="sm:hidden">{label.split(' ')[0]}</span>
        {isCompleted && <FiCheck className="text-emerald-600 text-xs sm:text-sm" />}
        {!canAccess && <FiLock className="text-slate-400 text-xs sm:text-sm" />}
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <header className="text-center mb-8 sm:mb-12">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-light text-slate-800 mb-3 sm:mb-4 animate-fade-in">
              n8n Execution Feedback
            </h1>
            <p className="text-slate-600 text-sm sm:text-base lg:text-lg max-w-2xl mx-auto px-4 animate-fade-in-delay">
              Collect and manage feedback for n8n execution results
            </p>
          </header>

          {/* Load Existing Feedback / Create New */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 mb-6 sm:mb-8 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex items-center gap-3 sm:gap-4">
                <div className="p-2 bg-slate-100 rounded-xl">
                  {isEditMode ? <FiEdit3 className="text-slate-600 text-lg" /> : <FiEye className="text-slate-600 text-lg" />}
                </div>
                <div className="flex-1">
                  <h3 className="text-base sm:text-lg font-medium text-slate-800 mb-1 sm:mb-2">
                    {isEditMode ? 'Editing Existing Feedback' : 'Load Existing Feedback'}
                  </h3>
                  <p className="text-slate-500 text-xs sm:text-sm">
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
                      className="bg-slate-50 border border-slate-200 rounded-xl px-3 sm:px-4 py-2 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-slate-300 transition-all duration-200 text-sm sm:text-base"
                      onChange={(e) => setSubmissionId(e.target.value)}
                    />
                    <button
                      onClick={() => loadExistingFeedback(submissionId)}
                      className="bg-slate-800 text-white px-4 py-2 rounded-xl hover:bg-slate-700 transition-all duration-200 text-sm sm:text-base"
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
            <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
              <h2 className="text-xl sm:text-2xl font-medium text-slate-800 mb-4 sm:mb-6 flex items-center gap-3">
                <div className="p-2 bg-slate-100 rounded-xl">
                  <FiEdit3 className="text-slate-600 text-lg" />
                </div>
                Basic Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                <div>
                  <label className="block text-slate-700 font-medium mb-2 text-sm sm:text-base">
                    n8n Execution ID <span className="text-slate-500 text-xs sm:text-sm">(Read-only)</span>
                  </label>
                  <input
                    type="text"
                    name="n8n_execution_id"
                    value={formData.n8n_execution_id}
                    readOnly
                    className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-slate-600 cursor-not-allowed text-sm sm:text-base"
                    placeholder="Execution ID will be loaded automatically"
                  />
                </div>
                
                <div>
                  <label className="block text-slate-700 font-medium mb-2 text-sm sm:text-base">
                    Email <span className="text-slate-500 text-xs sm:text-sm">(Read-only)</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    readOnly
                    className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3 sm:px-4 py-2 sm:py-3 text-slate-600 cursor-not-allowed text-sm sm:text-base"
                    placeholder="Email will be loaded automatically"
                  />
                </div>
              </div>
            </div>

            {/* Content Tabs */}
            <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 lg:p-8 shadow-sm hover:shadow-md transition-all duration-300">
              <div className="sticky top-0 z-10 bg-white border-b border-slate-200 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-4 mb-6 sm:mb-8">
                <div className="flex gap-2 overflow-x-auto pb-2">
                  <TabButton 
                    id="linkedin" 
                    label="LinkedIn Content" 
                    icon={FiLinkedin} 
                    isActive={activeTab === 'linkedin'}
                    isCompleted={tabValidation.linkedin}
                    isVisited={visitedTabs.has('linkedin')}
                  />
                  <TabButton 
                    id="twitter" 
                    label="X/Twitter Content" 
                    icon={FiTwitter} 
                    isActive={activeTab === 'twitter'}
                    isCompleted={tabValidation.twitter}
                    isVisited={visitedTabs.has('twitter')}
                  />
                  <TabButton 
                    id="images" 
                    label="Generated Images" 
                    icon={FiImage} 
                    isActive={activeTab === 'images'}
                    isCompleted={tabValidation.images}
                    isVisited={visitedTabs.has('images')}
                  />
                </div>
              </div>

              {/* Tab Content */}
              <TabContent
                activeTab={activeTab}
                formData={formData}
                handleInputChange={handleInputChange}
                tabValidation={tabValidation}
              />
            </div>

            {/* Submit Button */}
            <div className="text-center">
              <button
                type="submit"
                disabled={loading || !canSubmit()}
                className={`px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-medium transition-all duration-300 shadow-sm hover:shadow-md text-sm sm:text-base ${
                  canSubmit()
                    ? 'bg-slate-800 text-white hover:bg-slate-700'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
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
                    <span>Submit Feedback</span>
                  </div>
                )}
              </button>
              

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