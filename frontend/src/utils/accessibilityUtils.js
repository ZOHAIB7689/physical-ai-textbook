// frontend/src/utils/accessibilityUtils.js

// Function to set high contrast mode
export const setHighContrast = (enable) => {
  if (enable) {
    document.body.classList.add('high-contrast');
  } else {
    document.body.classList.remove('high-contrast');
  }
};

// Function to adjust text size
export const setTextSize = (size) => {
  // Valid sizes: 'small', 'normal', 'large', 'extra-large'
  document.body.classList.remove('text-small', 'text-normal', 'text-large', 'text-extra-large');
  document.body.classList.add(`text-${size}`);
};

// Function to manage focus indicators for keyboard navigation
export const setupFocusIndicators = () => {
  // Add visual indicators for keyboard focus
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-nav');
    }
  });

  document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-nav');
  });
};

// Function to announce messages to screen readers
export const announceToScreenReader = (message) => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  // Remove the element after a delay
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

// Function to check color contrast (simplified version)
export const hasSufficientContrast = (foregroundColor, backgroundColor) => {
  // This is a simplified version - a full implementation would calculate
  // the actual contrast ratio according to WCAG guidelines
  return true; // Placeholder implementation
};

// Initialize accessibility features
export const initAccessibility = () => {
  setupFocusIndicators();
  
  // Apply user preferences from localStorage if available
  const accessibilityPrefs = JSON.parse(localStorage.getItem('accessibilityPrefs') || '{}');
  
  if (accessibilityPrefs.highContrast) {
    setHighContrast(accessibilityPrefs.highContrast);
  }
  
  if (accessibilityPrefs.textSize) {
    setTextSize(accessibilityPrefs.textSize);
  }
};

// Save accessibility preferences
export const saveAccessibilityPrefs = (prefs) => {
  localStorage.setItem('accessibilityPrefs', JSON.stringify(prefs));
};