import React, { useState } from 'react';
import { FiSend, FiCheck, FiAlertCircle, FiLinkedin, FiTwitter, FiImage } from 'react-icons/fi';
import axios from 'axios';

function App() {
  const [formData, setFormData] = useState({
    n8n_execution_id: '',
    
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
    x_grok_content: 'Sample X/Twitter Grok content would appear here...',
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
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await axios.post('/api/feedback', formData);
      setMessage({
        type: 'success',
        text: `Feedback submitted successfully! Submission ID: ${response.data.submission_id}`
      });
      // Reset form
      setFormData(prev => ({
        ...prev,
        n8n_execution_id: '',
        linkedin_feedback: '',
        linkedin_chosen_llm: '',
        linkedin_custom_content: '',
        x_feedback: '',
        x_chosen_llm: '',
        x_custom_content: '',
        image_feedback: '',
        image_chosen_llm: ''
      }));
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to submit feedback. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const ContentPreview = ({ title, content, icon: Icon, isPrefilled = true }) => (
    <div className="card mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="text-primary text-lg" />
        <h4 className="text-lg font-semibold text-text-primary">{title}</h4>
        {isPrefilled && (
          <span className="bg-green-600 text-white text-xs px-2 py-1 rounded-full">
            Pre-filled
          </span>
        )}
      </div>
      <div className="bg-black bg-opacity-30 rounded-lg p-4 border-l-4 border-primary">
        <p className="text-text-secondary text-sm leading-relaxed whitespace-pre-wrap">
          {content || 'No content available'}
        </p>
      </div>
    </div>
  );

  const ImagePreview = ({ title, url, icon: Icon, isPrefilled = true }) => (
    <div className="card mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="text-primary text-lg" />
        <h4 className="text-lg font-semibold text-text-primary">{title}</h4>
        {isPrefilled && (
          <span className="bg-green-600 text-white text-xs px-2 py-1 rounded-full">
            Pre-filled
          </span>
        )}
      </div>
      {url ? (
        <img 
          src={url} 
          alt={title}
          className="max-w-xs max-h-48 rounded-lg border-2 border-border"
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'block';
          }}
        />
      ) : (
        <div className="bg-black bg-opacity-30 rounded-lg p-4 border-l-4 border-primary">
          <p className="text-text-muted text-sm">No image URL provided</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-text-primary mb-2">
              n8n Execution Feedback System
            </h1>
            <p className="text-text-secondary">
              Collect and store feedback for n8n execution results
            </p>
          </header>

          {message.text && (
            <div className={`card mb-6 ${
              message.type === 'success' 
                ? 'bg-green-900 bg-opacity-20 border-green-500' 
                : 'bg-red-900 bg-opacity-20 border-red-500'
            }`}>
              <div className="flex items-center gap-2">
                {message.type === 'success' ? (
                  <FiCheck className="text-green-400" />
                ) : (
                  <FiAlertCircle className="text-red-400" />
                )}
                <span className={message.type === 'success' ? 'text-green-400' : 'text-red-400'}>
                  {message.text}
                </span>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* n8n Execution ID */}
            <div className="card">
              <h2 className="section-title">n8n Execution ID</h2>
              <div className="mb-4">
                <label className="block text-text-secondary font-semibold mb-2">
                  Execution ID * <span className="text-blue-400 text-sm">(User Input)</span>
                </label>
                <input
                  type="text"
                  name="n8n_execution_id"
                  value={formData.n8n_execution_id}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter n8n execution ID"
                  required
                />
              </div>
            </div>

            {/* LinkedIn Content Section */}
            <div className="card">
              <h2 className="section-title flex items-center gap-2">
                <FiLinkedin className="text-primary" />
                LinkedIn Content
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <ContentPreview 
                  title="Grok Content" 
                  content={formData.linkedin_grok_content}
                  icon={FiLinkedin}
                />
                <ContentPreview 
                  title="o3 Content" 
                  content={formData.linkedin_o3_content}
                  icon={FiLinkedin}
                />
                <ContentPreview 
                  title="Gemini Content" 
                  content={formData.linkedin_gemini_content}
                  icon={FiLinkedin}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-text-secondary font-semibold mb-2">
                    LinkedIn Feedback <span className="text-blue-400 text-sm">(User Input)</span>
                  </label>
                  <textarea
                    name="linkedin_feedback"
                    value={formData.linkedin_feedback}
                    onChange={handleInputChange}
                    className="form-input min-h-32"
                    placeholder="Enter your feedback for LinkedIn content..."
                  />
                </div>
                
                <div>
                  <label className="block text-text-secondary font-semibold mb-2">
                    Choose LinkedIn LLM <span className="text-blue-400 text-sm">(User Input)</span>
                  </label>
                  <select
                    name="linkedin_chosen_llm"
                    value={formData.linkedin_chosen_llm}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="">Select LLM</option>
                    <option value="Grok">Grok</option>
                    <option value="o3">o3</option>
                    <option value="Gemini">Gemini</option>
                  </select>
                </div>
              </div>

              <div className="mt-6">
                <label className="block text-text-secondary font-semibold mb-2">
                  LinkedIn Custom Content <span className="text-blue-400 text-sm">(User Input)</span>
                </label>
                <textarea
                  name="linkedin_custom_content"
                  value={formData.linkedin_custom_content}
                  onChange={handleInputChange}
                  className="form-input min-h-32"
                  placeholder="Enter custom LinkedIn content..."
                />
              </div>
            </div>

            {/* X/Twitter Content Section */}
            <div className="card">
              <h2 className="section-title flex items-center gap-2">
                <FiTwitter className="text-primary" />
                X/Twitter Content
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <ContentPreview 
                  title="Grok Content" 
                  content={formData.x_grok_content}
                  icon={FiTwitter}
                />
                <ContentPreview 
                  title="o3 Content" 
                  content={formData.x_o3_content}
                  icon={FiTwitter}
                />
                <ContentPreview 
                  title="Gemini Content" 
                  content={formData.x_gemini_content}
                  icon={FiTwitter}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-text-secondary font-semibold mb-2">
                    X Feedback <span className="text-blue-400 text-sm">(User Input)</span>
                  </label>
                  <textarea
                    name="x_feedback"
                    value={formData.x_feedback}
                    onChange={handleInputChange}
                    className="form-input min-h-32"
                    placeholder="Enter your feedback for X content..."
                  />
                </div>
                
                <div>
                  <label className="block text-text-secondary font-semibold mb-2">
                    Choose X LLM <span className="text-blue-400 text-sm">(User Input)</span>
                  </label>
                  <select
                    name="x_chosen_llm"
                    value={formData.x_chosen_llm}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="">Select LLM</option>
                    <option value="Grok">Grok</option>
                    <option value="o3">o3</option>
                    <option value="Gemini">Gemini</option>
                  </select>
                </div>
              </div>

              <div className="mt-6">
                <label className="block text-text-secondary font-semibold mb-2">
                  X Custom Content <span className="text-blue-400 text-sm">(User Input)</span>
                </label>
                <textarea
                  name="x_custom_content"
                  value={formData.x_custom_content}
                  onChange={handleInputChange}
                  className="form-input min-h-32"
                  placeholder="Enter custom X content..."
                />
              </div>
            </div>

            {/* Image Section */}
            <div className="card">
              <h2 className="section-title flex items-center gap-2">
                <FiImage className="text-primary" />
                Generated Images
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <ImagePreview 
                  title="Stable Diffusion" 
                  url={formData.stable_diffusion_image_url}
                  icon={FiImage}
                />
                <ImagePreview 
                  title="Pixabay" 
                  url={formData.pixabay_image_url}
                  icon={FiImage}
                />
                <ImagePreview 
                  title="GPT1" 
                  url={formData.gpt1_image_url}
                  icon={FiImage}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-text-secondary font-semibold mb-2">
                    Image Feedback <span className="text-blue-400 text-sm">(User Input)</span>
                  </label>
                  <textarea
                    name="image_feedback"
                    value={formData.image_feedback}
                    onChange={handleInputChange}
                    className="form-input min-h-32"
                    placeholder="Enter your feedback for images..."
                  />
                </div>
                
                <div>
                  <label className="block text-text-secondary font-semibold mb-2">
                    Choose Image LLM <span className="text-blue-400 text-sm">(User Input)</span>
                  </label>
                  <select
                    name="image_chosen_llm"
                    value={formData.image_chosen_llm}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="">Select LLM</option>
                    <option value="Stable">Stable Diffusion</option>
                    <option value="Pixabay">Pixabay</option>
                    <option value="GPT1">GPT1</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="text-center">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Submitting...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <FiSend />
                    Submit Feedback
                  </div>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App; 