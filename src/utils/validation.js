// Validation utility functions

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateServerUrl = (url) => {
  if (!url) return { isValid: false, error: 'Server URL is required' };
  
  // Remove trailing slash
  const cleanUrl = url.replace(/\/$/, '');
  
  if (!validateUrl(cleanUrl)) {
    return { isValid: false, error: 'Invalid URL format' };
  }
  
  // Check if it's HTTP or HTTPS
  if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
    return { isValid: false, error: 'URL must start with http:// or https://' };
  }
  
  return { isValid: true, cleanUrl };
};

export const validatePassword = (password) => {
  if (!password) return { isValid: false, error: 'Password is required' };
  
  if (password.length < 6) {
    return { isValid: false, error: 'Password must be at least 6 characters' };
  }
  
  return { isValid: true };
};

export const validateUsername = (username) => {
  if (!username) return { isValid: false, error: 'Username is required' };
  
  if (username.length < 3) {
    return { isValid: false, error: 'Username must be at least 3 characters' };
  }
  
  return { isValid: true };
};

export const validateLoginForm = (username, password, serverUrl) => {
  const errors = {};
  
  if (!username || username.length < 3) {
    errors.username = 'Username must be at least 3 characters';
  }
  
  if (!password || password.length < 6) {
    errors.password = 'Password must be at least 6 characters';
  }
  
  const urlValidation = validateServerUrl(serverUrl);
  if (!urlValidation.isValid) {
    errors.serverUrl = urlValidation.error;
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    cleanServerUrl: urlValidation.cleanUrl
  };
}; 