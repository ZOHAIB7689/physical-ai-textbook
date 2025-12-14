import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChapterReader = ({ chapter, onProgressUpdate }) => {
  const [progress, setProgress] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedLanguage, setSelectedLanguage] = useState('en'); // Default to English

  // Calculate content length for progress tracking
  useEffect(() => {
    if (chapter) {
      // Simple approach: count paragraphs to estimate pages
      const content = selectedLanguage === 'ur' ? chapter.content_ur : chapter.content;
      if (content) {
        const paragraphs = content.split('\n\n');
        setTotalPages(Math.ceil(paragraphs.length / 5)); // Estimate 5 paragraphs per "page"
      }
    }
  }, [chapter, selectedLanguage]);

  // Update progress as user reads
  useEffect(() => {
    if (chapter && onProgressUpdate) {
      const progressPercent = Math.min(100, Math.floor((currentPage / totalPages) * 100));
      setProgress(progressPercent);
      onProgressUpdate(progressPercent, currentPage);
    }
  }, [currentPage, totalPages, chapter, onProgressUpdate]);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const toggleLanguage = () => {
    setSelectedLanguage(prev => prev === 'en' ? 'ur' : 'en');
  };

  if (!chapter) {
    return <div className="chapter-reader">Select a chapter to begin reading</div>;
  }

  const content = selectedLanguage === 'ur' && chapter.content_ur 
    ? chapter.content_ur 
    : chapter.content;

  return (
    <div className="chapter-reader">
      <div className="chapter-header">
        <h1>{chapter.title}</h1>
        <div className="chapter-meta">
          <span>Module: {chapter.module_title}</span>
          <span>Estimated Reading Time: {chapter.estimated_reading_time} min</span>
        </div>
        <div className="chapter-controls">
          <button onClick={toggleLanguage} className="language-toggle">
            {selectedLanguage === 'en' ? 'اردو' : 'English'}
          </button>
        </div>
      </div>

      <div className="chapter-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>

      <div className="chapter-navigation">
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <span className="progress-text">{progress}% complete</span>
        </div>

        <div className="page-controls">
          <button 
            onClick={() => handlePageChange(currentPage - 1)} 
            disabled={currentPage <= 1}
            className="nav-button prev"
          >
            Previous
          </button>
          <span className="page-info">Page {currentPage} of {totalPages}</span>
          <button 
            onClick={() => handlePageChange(currentPage + 1)} 
            disabled={currentPage >= totalPages}
            className="nav-button next"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChapterReader;