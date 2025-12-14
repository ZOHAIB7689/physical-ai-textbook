// frontend/src/utils/i18n.js

// Translation dictionary
const translations = {
  en: {
    // Navigation
    'textbook': 'Textbook',
    'modules': 'Modules',
    'chapters': 'Chapters',
    'search': 'Search',
    'settings': 'Settings',
    
    // Common UI elements
    'previous': 'Previous',
    'next': 'Next',
    'page': 'Page',
    'of': 'of',
    'complete': 'complete',
    
    // Chatbot
    'askQuestion': 'Ask a question...',
    'send': 'Send',
    'aiAssistant': 'AI Learning Assistant',
    
    // Accessibility
    'highContrast': 'High Contrast',
    'fontSize': 'Font Size',
    'small': 'Small',
    'normal': 'Normal',
    'large': 'Large',
    'extraLarge': 'Extra Large',
    
    // Language
    'language': 'Language',
    
    // Content
    'estimatedReadingTime': 'Estimated Reading Time',
    'module': 'Module',
  },
  ur: {
    // Navigation
    'textbook': 'متن کتاب',
    'modules': 'ماڈیولز',
    'chapters': 'ابواب',
    'search': 'تلاش',
    'settings': 'ترتیبات',
    
    // Common UI elements
    'previous': 'پچھلا',
    'next': 'اگلا',
    'page': 'صفحہ',
    'of': 'میں سے',
    'complete': 'مکمل',
    
    // Chatbot
    'askQuestion': 'سوال پوچھیں...',
    'send': 'بھیجیں',
    'aiAssistant': 'مصنوعی ذہنی معاون',
    
    // Accessibility
    'highContrast': 'زیادہ کانٹراسٹ',
    'fontSize': 'حرف کا سائز',
    'small': 'چھوٹا',
    'normal': 'عام',
    'large': 'بڑا',
    'extraLarge': 'بہت بڑا',
    
    // Language
    'language': 'زبان',
    
    // Content
    'estimatedReadingTime': 'تقریبی پڑھنے کا وقت',
    'module': 'ماڈیول',
  }
};

// Default language
const DEFAULT_LANGUAGE = 'en';

// Get the current language from preferences or localStorage
const getCurrentLanguage = () => {
  const storedPrefs = localStorage.getItem('userPrefs');
  if (storedPrefs) {
    const prefs = JSON.parse(storedPrefs);
    return prefs.language || DEFAULT_LANGUAGE;
  }
  
  // Check system language
  const systemLang = navigator.language.split('-')[0];
  if (translations[systemLang]) {
    return systemLang;
  }
  
  return DEFAULT_LANGUAGE;
};

// Translate a key to the current language
export const t = (key, lang = null) => {
  const language = lang || getCurrentLanguage();
  const langTranslations = translations[language] || translations[DEFAULT_LANGUAGE];
  return langTranslations[key] || key; // Return the key if translation not found
};

// Get all available languages
export const getAvailableLanguages = () => {
  return Object.keys(translations);
};

// Change the current language
export const setLanguage = (lang) => {
  if (translations[lang]) {
    const userPrefs = JSON.parse(localStorage.getItem('userPrefs') || '{}');
    localStorage.setItem('userPrefs', JSON.stringify({
      ...userPrefs,
      language: lang
    }));
    return true;
  }
  return false;
};

// Get text direction for the current language (LTR/RTL)
export const getTextDirection = (lang = null) => {
  const language = lang || getCurrentLanguage();
  // Arabic, Urdu, and Hebrew are RTL languages
  if (['ar', 'ur', 'he'].includes(language)) {
    return 'rtl';
  }
  return 'ltr';
};