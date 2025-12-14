// frontend/src/pages/textbook.js
import React, { useState, useEffect } from 'react';
import ContentNavigator from '../components/ContentNavigator/ContentNavigator';
import ChapterReader from '../components/ChapterReader/ChapterReader';
import learningSessionService from '../services/learningSessionService';

const TextbookPage = () => {
  const [modules, setModules] = useState([]);
  const [currentChapter, setCurrentChapter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch modules from backend API
  useEffect(() => {
    const fetchModules = async () => {
      try {
        const response = await fetch('/api/modules'); // This would connect to our backend
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setModules(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchModules();
  }, []);

  // Fetch chapter when selected
  useEffect(() => {
    const fetchChapter = async () => {
      if (!currentChapter) return;

      try {
        const response = await fetch(`/api/chapters/${currentChapter.slug}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const chapterData = await response.json();
        setCurrentChapter(chapterData);
      } catch (err) {
        setError(err.message);
      }
    };

    if (currentChapter?.slug) {
      fetchChapter();
    }
  }, [currentChapter?.slug]);

  // Handle progress updates
  const handleProgressUpdate = async (progress, page) => {
    if (!currentChapter || !localStorage.getItem('user_id')) return;

    try {
      // Check if a learning session already exists for this user and chapter
      let session = await learningSessionService.getLearningSessionByUserAndChapter(
        localStorage.getItem('user_id'), 
        currentChapter.id
      );

      if (session) {
        // Update existing session
        await learningSessionService.updateProgress(session.id, progress, page);
      } else {
        // Create new session
        await learningSessionService.createLearningSession({
          user_id: localStorage.getItem('user_id'),
          chapter_id: currentChapter.id,
          start_time: new Date(),
          progress_percentage: progress,
          last_accessed_page: page
        });
      }
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  if (loading) return <div>Loading textbook content...</div>;
  if (error) return <div>Error loading content: {error}</div>;

  return (
    <div className="textbook-page">
      <h1>Physical AI & Humanoid Robotics Textbook</h1>
      <div className="textbook-layout">
        <aside className="navigation-panel">
          <ContentNavigator 
            modules={modules} 
          />
        </aside>
        <main className="content-panel">
          {currentChapter ? (
            <ChapterReader 
              chapter={currentChapter} 
              onProgressUpdate={handleProgressUpdate}
            />
          ) : (
            <div className="welcome-message">
              <h2>Welcome to the AI-Native Textbook</h2>
              <p>Select a chapter from the navigation panel to begin reading.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default TextbookPage;