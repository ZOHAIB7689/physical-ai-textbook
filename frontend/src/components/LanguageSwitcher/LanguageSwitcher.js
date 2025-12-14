import React, { useState, useEffect } from 'react';
import { usePersonalization } from '../../context/PersonalizationContext';

const LanguageSwitcher = () => {
  const { preferences, setPreferences } = usePersonalization();
  const [selectedLanguage, setSelectedLanguage] = useState(preferences.language || 'en');
  
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ur', name: 'اردو' }  // Urdu
  ];

  useEffect(() => {
    // Update the selected language when preferences change
    setSelectedLanguage(preferences.language || 'en');
  }, [preferences.language]);

  const handleLanguageChange = (langCode) => {
    setSelectedLanguage(langCode);
    
    // Update preferences in context
    setPreferences({ language: langCode });
    
    // Update language in localStorage
    const userPrefs = JSON.parse(localStorage.getItem('userPrefs') || '{}');
    localStorage.setItem('userPrefs', JSON.stringify({
      ...userPrefs,
      language: langCode
    }));
    
    // Optionally trigger a page refresh or content update here
    // For now, we'll just update the context which components can react to
  };

  return (
    <div className="language-switcher">
      <select 
        value={selectedLanguage} 
        onChange={(e) => handleLanguageChange(e.target.value)}
        aria-label="Select language"
      >
        {languages.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
      <span className="language-indicator">
        {selectedLanguage === 'ur' ? 'اردو' : 'EN'}
      </span>
    </div>
  );
};

export default LanguageSwitcher;