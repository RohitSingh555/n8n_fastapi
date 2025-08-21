import React from 'react';
import { Link } from 'react-router-dom';
import { 
  FiShield, 
  FiCheckCircle,
  FiAward,
  FiHeart,
  FiTarget,
  FiUser
} from 'react-icons/fi';
import logo from '../assets/logo_landing_page.png';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white text-gray-800">
      {/* Navigation */}
      <nav className="border-b border-gray-200 backdrop-blur-sm bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <img 
                src={logo} 
                alt="Ultrasound AI Logo" 
                className="h-10 w-auto object-contain drop-shadow-sm"
              />
              <span className="text-xl font-bold text-gray-800">Ultrasound AI</span>
            </div>
            <div className="flex items-center space-x-6">
              <Link 
                to="/social-media" 
                className="text-gray-600 hover:text-gray-800 transition-colors"
              >
                Social Media
              </Link>
                             <Link
                 to="/login"
                 className="bg-[#878eff] hover:bg-[#6b6eff] text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
               >
                <FiUser className="w-4 h-4" />
                <span>Login</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <div className="animate-fade-in">
              {/* Main Logo */}
              <div className="flex justify-center mb-8">
                <img 
                  src={logo} 
                  alt="Ultrasound AI Logo" 
                  className="h-36 w-auto object-contain drop-shadow-lg"
                />
              </div>
              
                             <div className="flex items-center justify-center mb-6">
                 <FiAward className="w-8 h-8 text-[#878eff] mr-3" />
                 <span className="text-lg text-[#878eff] font-semibold">2023 Geneva Innovation Award Winner</span>
               </div>
                             <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
                 Transform Your Social Media
                 <span className="text-[#878eff] block">with AI-Powered Intelligence</span>
               </h1>
               <p className="text-xl text-gray-800 max-w-4xl mx-auto mb-8 leading-relaxed">
                 Stop juggling multiple platforms and struggling with content creation. Our intelligent social media platform automatically generates engaging posts, handles multi-platform publishing, and learns from your feedback to deliver better results every time. Focus on your business while we handle your social presence.
               </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
                                 <Link
                   to="/login"
                   className="bg-[#878eff] hover:bg-[#6b6eff] text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all transform hover:scale-105 flex items-center space-x-3"
                 >
                  <FiUser className="w-5 h-5" />
                  <span>Sign In to Access Tools</span>
                </Link>
              </div>

              <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-800">
                <div className="flex items-center space-x-2">
                  <FiCheckCircle className="w-4 h-4 text-green-500" />
                  <span>Approved in Brazil</span>
                </div>
                <div className="flex items-center space-x-2">
                  <FiCheckCircle className="w-4 h-4 text-green-500" />
                  <span>Available in Chile</span>
                </div>
                <div className="flex items-center space-x-2">
                  <FiTarget className="w-4 h-4 text-yellow-500" />
                  <span>Not approved by the FDA for use in the US</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
                 {/* Background decoration */}
         <div className="absolute inset-0 -z-10">
           <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-[#878eff]/20 rounded-full blur-3xl"></div>
           <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#878eff]/10 rounded-full blur-3xl"></div>
         </div>
      </section>

      {/* Crisis Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 animate-fade-in-delay">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              The future of social media management is here
            </h2>
            <p className="text-gray-800 text-lg max-w-4xl mx-auto mb-12 leading-relaxed">
              Stop struggling with content creation and platform management. Our intelligent social media platform automatically generates engaging posts, handles multi-platform publishing, and learns from your feedback to deliver better results every time. Focus on your business while we handle your social presence.
            </p>
            
            <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-4xl font-bold text-[#878eff] mb-2">3x</div>
                <div className="text-gray-800">Faster content creation with AI assistance</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-[#878eff] mb-2">100%</div>
                <div className="text-gray-800">Multi-platform posting automation</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-[#878eff] mb-2">24/7</div>
                <div className="text-gray-800">Automated posting and engagement</div>
              </div>
            </div>
            
            <div className="mt-12 p-6 bg-gray-50 border border-gray-200 rounded-xl max-w-2xl mx-auto">
              <p className="text-lg italic text-gray-800 mb-3">
                "Our platform handles the complexity so you can focus on what matters most."
              </p>
              <p className="text-gray-800 font-semibold">Social Media AI Team</p>
            </div>
          </div>
        </div>
      </section>

      {/* Transform Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Transform your social media presence with intelligent automation
            </h2>
            <p className="text-gray-800 text-lg max-w-4xl mx-auto leading-relaxed">
              Say goodbye to manual posting and content creation headaches. Our AI automatically generates engaging posts, handles multiple platforms simultaneously, and continuously improves based on your feedback. Experience the power of intelligent social media management that works while you sleep.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: FiTarget,
                title: "AI-Powered Content Generation",
                description: "Our intelligent system automatically creates engaging posts tailored to your brand voice and audience preferences. No more staring at blank screens wondering what to post."
              },
              {
                icon: FiShield,
                title: "Multi-Platform Automation",
                description: "Post to Twitter, LinkedIn, and other platforms simultaneously with a single click. Our system handles the formatting and optimization for each platform automatically."
              },
              {
                icon: FiHeart,
                title: "Continuous Learning & Improvement",
                description: "The more you use our platform, the smarter it gets. Our AI learns from your feedback and engagement data to deliver better results over time."
              }
            ].map((feature, index) => (
              <div 
                key={index}
                className="bg-white border border-gray-200 rounded-xl p-6 hover:border-[#878eff]/60 transition-all duration-300 hover:transform hover:scale-105 shadow-sm hover:shadow-md"
              >
                                 <div className="w-12 h-12 bg-[#878eff]/20 rounded-lg flex items-center justify-center mb-4">
                   <feature.icon className="w-6 h-6 text-[#878eff]" />
                 </div>
                <h3 className="text-xl font-semibold mb-2 text-gray-800">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Powerful automation. Simple workflow.
            </h2>
            <p className=" text-lg max-w-4xl mx-auto mb-8 leading-relaxed">
              <strong>Social Media AI</strong> handles the entire content creation and publishing process—from generating engaging posts to managing multiple platforms and collecting feedback for continuous improvement.
            </p>
            <h3 className="text-2xl font-semibold mb-8">How it works</h3>
            <p className="text-xl text-[#878eff] font-semibold mb-12">Create. Automate. Optimize.</p>
            <p className="text-gray-800 text-lg max-w-3xl mx-auto mb-12">
              Our workflow is simple: Choose your content type, let our AI generate and optimize posts, and watch as your content automatically publishes across all platforms while collecting valuable feedback.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                number: "1",
                title: "Scan",
                description: "Use existing standard ultrasound scans—the same ones already taken—easily and securely uploaded into our cloud AI."
              },
              {
                number: "2",
                title: "Analyze",
                description: "Within seconds, our AI processes the images, detecting subtle patterns invisible to the human eye."
              },
              {
                number: "3",
                title: "Forecast",
                description: "You receive a personalized delivery date estimate based on your ultrasound. No new machines or equipment, no workflow changes. It's just simple, seamless, and smart."
              }
            ].map((step, index) => (
              <div 
                key={index}
                className="text-center"
              >
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white">
                  {step.number}
                </div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-gray-800">{step.description}</p>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-12 p-6 bg-surface border border-border/20 rounded-xl max-w-2xl mx-auto">
            <p className="text-lg italic  mb-3">
              "Delivery Date AI™ is like having a second pair of expert eyes on every scan."
            </p>
          </div>
        </div>
      </section>

      {/* Clinical Validation Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Clinically Validated. Scientifically Proven.
            </h2>
            <p className=" text-lg max-w-4xl mx-auto mb-8 leading-relaxed">
              Validated through rigorous clinical studies across multiple countries.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-semibold mb-6">Regulatory Approvals & Recognition</h3>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <FiCheckCircle className="w-5 h-5 text-green-400" />
                  <span>Brazil (ANVISA)</span>
                </div>
                <div className="flex items-center space-x-3">
                  <FiCheckCircle className="w-5 h-5 text-green-400" />
                  <span>Chile</span>
                </div>
                <div className="flex items-center space-x-3">
                  <FiTarget className="w-5 h-5 text-yellow-400" />
                  <span>USA (Pending FDA Approval)</span>
                </div>
              </div>
            </div>
            
            <div className="bg-surface border border-border/20 rounded-xl p-8">
              <h3 className="text-2xl font-semibold mb-6">University of Kentucky PAIR Study</h3>
              <p className=" mb-6">The largest independent validation of AI-powered delivery date prediction</p>
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary mb-2">5,714</div>
                  <div className=" text-sm">Patients</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary mb-2">19,940</div>
                  <div className=" text-sm">Exams</div>
                </div>
              </div>
              <p className="text-sm  mt-4">University of Kentucky. Independent Validation.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-white border border-gray-200 rounded-2xl p-12 shadow-lg">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-800">
              Ready to Transform Your Social Media?
            </h2>
            <p className="text-gray-600 text-lg mb-8 max-w-2xl mx-auto">
              Access our powerful AI-powered social media management platform and start automating your content creation today.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/login"
                className="bg-[#878eff] hover:bg-[#6b6eff] text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all transform hover:scale-105 flex items-center justify-center space-x-3"
              >
                <FiUser className="w-5 h-5" />
                <span>Sign In Now</span>
              </Link>
            </div>

          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <img 
                src={logo} 
                alt="Ultrasound AI Logo" 
                className="h-10 w-auto object-contain drop-shadow-sm"
              />
              <span className="text-lg font-bold text-gray-800">Social Media AI</span>
            </div>
            <div className="flex items-center space-x-6 text-gray-600">
              <Link to="/social-media" className="hover:text-gray-800 transition-colors">
                Social Media
              </Link>
              <span>&copy; 2025 Social Media AI. All rights reserved.</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
