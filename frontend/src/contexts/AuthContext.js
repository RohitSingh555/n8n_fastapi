import React, { createContext, useContext, useState, useEffect } from 'react';
import API_BASE_URL from '../config';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (from localStorage)
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser);
        setCurrentUser(user);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('currentUser');
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
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
      
      // Only store non-sensitive user information
      const userWithoutPassword = {
        id: userData.id,
        username: userData.username,
        name: userData.name,
        email: userData.email,
        is_active: userData.is_active
      };

      setCurrentUser(userWithoutPassword);
      setIsAuthenticated(true);
      localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));
      return { success: true, user: userWithoutPassword };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    setCurrentUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('currentUser');
  };

  const changePassword = async (username, currentPassword, newPassword) => {
    try {
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

      return { success: true, message: 'Password changed successfully' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const getUsers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users`);
      if (response.ok) {
        const usersData = await response.json();
        return usersData.map(user => ({ 
          id: user.id, 
          name: user.name, 
          email: user.email,
          username: user.username,
          is_active: user.is_active
        }));
      } else {
        // Fallback to basic user list without passwords
        return [
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
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      // Fallback to basic user list without passwords
      return [
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
    }
  };

  const value = {
    currentUser,
    isAuthenticated,
    loading,
    login,
    logout,
    changePassword,
    getUsers
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
