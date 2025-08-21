import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FiUser, FiLock, FiEye, FiEyeOff, FiLogIn, FiKey, FiCheckCircle, FiHome } from 'react-icons/fi';
import logo from '../assets/logo_landing_page.png';
import API_BASE_URL from '../config';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState(false);

  const navigate = useNavigate();

  // Initialize users from backend API
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load users from backend API
  const loadUsersFromAPI = async () => {
    try {
      // Fetch users from backend API
      const response = await fetch(`${API_BASE_URL}/api/users`);
      if (response.ok) {
        const usersData = await response.json();
        // Only store non-sensitive user information
        const safeUsers = usersData.map(user => ({
          id: user.id,
          name: user.name,
          email: user.email,
          username: user.username,
          is_active: user.is_active
        }));
        setUsers(safeUsers);
      } else {
        // Fallback to basic user list without passwords
        const fallbackUsers = [
          { 
            id: 1, 
            name: 'Bob', 
            email: 'bob@example.com',
            username: 'bob',
            is_active: true
          },
          { 
            id: 2, 
            name: 'Leah', 
            email: 'leah@example.com',
            username: 'leah',
            is_active: true
          },
          { 
            id: 3, 
            name: 'Matthew', 
            email: 'matthew@example.com',
            username: 'matthew',
            is_active: true
          }
        ];
        setUsers(fallbackUsers);
      }
    } catch (error) {
      console.error('Error loading users:', error);
      // Fallback to basic user list without passwords
      const fallbackUsers = [
        { 
          id: 1, 
          name: 'Bob', 
          email: 'bob@example.com',
          username: 'bob',
          is_active: true
        },
        { 
          id: 2, 
          name: 'Leah', 
          email: 'leah@example.com',
          username: 'leah',
          is_active: true
        },
        { 
          id: 3, 
          name: 'Matthew', 
          email: 'matthew@example.com',
          username: 'matthew',
          is_active: true
        }
      ];
      setUsers(fallbackUsers);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load users when component mounts
    loadUsersFromAPI();
  }, []);

  useEffect(() => {
    // Check if user is already logged in
    const loggedInUser = localStorage.getItem('loggedInUser');
    if (loggedInUser) {
      const user = JSON.parse(loggedInUser);
      onLogin(user);
      navigate('/social-media');
    }
  }, [onLogin, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    if (!username) {
      setError('Please select a user account.');
      return;
    }

    try {
      // Call backend API to authenticate
      const response = await fetch(`${API_BASE_URL}/api/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const userData = await response.json();
      
      // Login successful - only store non-sensitive user information
      const userToStore = {
        id: userData.id,
        name: userData.name,
        email: userData.email,
        username: userData.username,
        is_active: userData.is_active
      };

      // Store only non-sensitive user data in localStorage
      localStorage.removeItem('loggedInUser');
      localStorage.setItem('loggedInUser', JSON.stringify(userToStore));
      onLogin(userToStore);
      navigate('/social-media');
    } catch (error) {
      setError(error.message);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setError('');

    if (!username) {
      setError('Please select a user account.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }

    if (newPassword.length < 8) {
      setError('New password must be at least 8 characters long.');
      return;
    }

    try {
      // Call backend API to change password
      const response = await fetch(`${API_BASE_URL}/api/users/change-password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to change password');
      }

      // Password change successful
      setPasswordChangeSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      
      setTimeout(() => {
        setPasswordChangeSuccess(false);
        setIsChangingPassword(false);
      }, 2000);
    } catch (error) {
      setError(error.message || 'Failed to update password. Please try again.');
    }
  };

  const resetForm = () => {
    setUsername('');
    setPassword('');
    setError('');
    setIsChangingPassword(false);
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setPasswordChangeSuccess(false);
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6">
            <img 
              src={logo} 
              alt="Ultrasound AI Logo" 
              className="h-32 w-auto object-contain drop-shadow-lg"
            />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome Back</h1>
          <p className="text-gray-600">Sign in to your Ultrasound AI account</p>
        </div>

        {/* Go Back to Home Button */}
                   <div className="text-center mb-6">
             <Link 
               to="/"
               className="inline-flex items-center space-x-2 text-[#878eff] hover:text-[#6b6eff] text-sm font-medium transition-colors"
             >
            <FiHome className="w-4 h-4" />
            <span>Go Back to Home</span>
          </Link>
        </div>

        {/* Login Form */}
        {!isChangingPassword && (
          <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-lg">
            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-800 mb-2">
                  Select User
                </label>
                <div className="relative">
                                       <select
                       id="username"
                       value={username}
                       onChange={(e) => setUsername(e.target.value)}
                       className="w-full px-4 py-3 pr-12 bg-white border border-gray-300 rounded-lg text-gray-800 focus:border-[#878eff] focus:ring-1 focus:ring-[#878eff] transition-colors appearance-none cursor-pointer hover:border-[#878eff]/80"
                       required
                     >
                    <option value="" className="text-gray-500">Select a user account</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.username} className="text-gray-800 bg-white">
                        {user.name} ({user.email})
                      </option>
                    ))}
                  </select>
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-800 mb-2">
                  Password
                </label>
                <div className="relative">
                                       <input
                       id="password"
                       type={showPassword ? 'text' : 'password'}
                       value={password}
                       onChange={(e) => setPassword(e.target.value)}
                       className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-500 focus:border-[#878eff] focus:ring-1 focus:ring-[#878eff] transition-colors pr-12"
                       placeholder="Enter your password"
                       required
                     />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
                  {error}
                </div>
              )}

                               <button
                   type="submit"
                   className="w-full bg-[#878eff] hover:bg-[#6b6eff] text-white py-3 px-4 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
                 >
                <FiLogIn className="w-5 h-5" />
                <span>Sign In</span>
              </button>
            </form>

            <div className="mt-6 text-center">
                               <button
                   onClick={() => setIsChangingPassword(true)}
                   className="text-[#878eff] hover:text-[#6b6eff] text-sm font-medium transition-colors flex items-center justify-center space-x-2 mx-auto"
                 >
                <FiKey className="w-4 h-4" />
                <span>Change Password</span>
              </button>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                Available users: bob, leah, matthew<br />
              </p>
            </div>
          </div>
        )}

        {/* Password Change Form */}
        {isChangingPassword && (
          <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-lg">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Change Password</h2>
              <p className="text-gray-600">Update your account password</p>
            </div>

            {passwordChangeSuccess && (
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3 text-green-600 text-sm mb-4 flex items-center space-x-2">
                <FiCheckCircle className="w-4 h-4" />
                <span>Password changed successfully!</span>
              </div>
            )}

            <form onSubmit={handlePasswordChange} className="space-y-6">
              <div>
                <label htmlFor="changeUsername" className="block text-sm font-medium text-gray-800 mb-2">
                  Select User
                </label>
                <div className="relative">
                                       <select
                       id="changeUsername"
                       value={username}
                       onChange={(e) => setUsername(e.target.value)}
                       className="w-full px-4 py-3 pr-12 bg-white border border-gray-300 rounded-lg text-gray-800 focus:border-[#878eff] focus:ring-1 focus:ring-[#878eff] transition-colors appearance-none cursor-pointer hover:border-[#878eff]/80"
                       required
                     >
                    <option value="" className="text-gray-500">Select a user account</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.username} className="text-gray-800 bg-white">
                        {user.name} ({user.email})
                      </option>
                    ))}
                  </select>
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                    <svg className="w-5 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

                            <div>
                <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-800 mb-2">
                  Current Password
                </label>
                                   <input
                     id="currentPassword"
                     type="password"
                     value={currentPassword}
                     onChange={(e) => setCurrentPassword(e.target.value)}
                     className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-500 focus:border-[#878eff] focus:ring-1 focus:ring-[#878eff] transition-colors"
                     placeholder="Enter current password"
                     required
                   />
              </div>

              <div>
                <label htmlFor="newPassword" className="block text-sm font-medium text-gray-800 mb-2">
                  New Password
                </label>
                <div className="relative">
                                       <input
                       id="newPassword"
                       type={showNewPassword ? 'text' : 'password'}
                       value={newPassword}
                       onChange={(e) => setNewPassword(e.target.value)}
                       className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-500 focus:border-[#878eff] focus:ring-1 focus:ring-[#878eff] transition-colors pr-12"
                       placeholder="Enter new password"
                       required
                     />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showNewPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-800 mb-2">
                  Confirm New Password
                </label>
                <div className="relative">
                                       <input
                       id="confirmPassword"
                       type={showConfirmPassword ? 'text' : 'password'}
                       value={confirmPassword}
                       onChange={(e) => setConfirmPassword(e.target.value)}
                       className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-800 placeholder-gray-500 focus:border-[#878eff] focus:ring-1 focus:ring-[#878eff] transition-colors pr-12"
                       placeholder="Confirm new password"
                       required
                     />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showConfirmPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
                  {error}
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setIsChangingPassword(false)}
                  className="flex-1 border border-gray-300 text-gray-800 py-3 px-4 rounded-lg font-semibold transition-colors hover:bg-gray-100"
                >
                  Cancel
                </button>
                                   <button
                     type="submit"
                     className="flex-1 bg-[#878eff] hover:bg-[#6b6eff] text-white py-3 px-4 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
                   >
                  <FiKey className="w-5 h-5" />
                  <span>Save</span>
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
