import React, { useState, useEffect } from 'react';
import { usePersonalization } from '../../context/PersonalizationContext';

const LearningAgent = ({ userId, currentChapter }) => {
  const [learningPath, setLearningPath] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('recommendations'); // recommendations, analysis, goals
  
  const { preferences } = usePersonalization();

  useEffect(() => {
    const fetchLearningData = async () => {
      try {
        setLoading(true);

        // Fetch personalized learning path
        const pathResponse = await fetch('/api/ai/learning-path', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (pathResponse.ok) {
          const pathData = await pathResponse.json();
          setLearningPath(pathData);
        } else {
          console.error('Failed to fetch learning path:', pathResponse.status);
        }

        // Fetch user progress analysis (we'll need to add this endpoint)
        // For now, we'll use the learning path data to simulate analysis
        // In a real system, progress analysis would be a separate endpoint
        if (pathResponse.ok) {
          // Simulate basic analysis based on the learning path
          const simulatedAnalysis = {
            engagement_analysis: {
              engagement_level: 'medium',
            },
            progress_metrics: {
              average_progress: pathData.progress_summary?.average_progress || 0,
            },
            learning_style: 'balanced', // Would come from actual analysis
            strengths: [], // Would come from actual analysis
            weaknesses: [] // Would come from actual analysis
          };
          setAnalysis(simulatedAnalysis);
        }
      } catch (error) {
        console.error('Error fetching learning data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchLearningData();
    }
  }, [userId]);

  if (loading) {
    return (
      <div className="learning-agent-container">
        <div className="agent-header">
          <h3>AI Learning Assistant</h3>
        </div>
        <div className="loading">Analyzing your learning progress...</div>
      </div>
    );
  }

  const submitFeedback = async (recommendationId, feedbackType) => {
    try {
      const response = await fetch('/api/ai/recommendation-feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          recommendation_id: recommendationId,
          feedback_type: feedbackType
        })
      });

      if (response.ok) {
        // Simple UI feedback for the user
        alert(`Thank you for your feedback on recommendation ${recommendationId}`);
      } else {
        console.error('Failed to submit feedback:', response.status);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <div className="learning-agent-container">
      <div className="agent-header">
        <h3>Your AI Learning Assistant</h3>
        <div className="agent-subtitle">Personalized recommendations based on your progress</div>
      </div>
      
      <div className="agent-tabs">
        <button 
          className={activeTab === 'recommendations' ? 'active' : ''}
          onClick={() => setActiveTab('recommendations')}
        >
          Recommendations
        </button>
        <button 
          className={activeTab === 'analysis' ? 'active' : ''}
          onClick={() => setActiveTab('analysis')}
        >
          Progress Analysis
        </button>
        <button 
          className={activeTab === 'goals' ? 'active' : ''}
          onClick={() => setActiveTab('goals')}
        >
          Learning Goals
        </button>
      </div>
      
      <div className="agent-content">
        {activeTab === 'recommendations' && (
          <div className="recommendations-section">
            <h4>Recommended Next Steps</h4>
            {learningPath?.recommended_chapters && learningPath.recommended_chapters.length > 0 ? (
              <ul className="recommendations-list">
                {learningPath.recommended_chapters.map((rec, index) => (
                  <li key={index} className={`recommendation-item priority-${rec.priority}`}>
                    <div className="rec-title">{rec.title}</div>
                    <div className="rec-module">{rec.module_title}</div>
                    <div className="rec-reason">{rec.reason}</div>
                    {rec.estimated_reading_time && (
                      <div className="rec-time">Est. {rec.estimated_reading_time} min</div>
                    )}
                    <div className="feedback-controls">
                      <button
                        onClick={() => submitFeedback(rec.id, 'helpful')}
                        className="feedback-btn helpful"
                        title="This recommendation is helpful"
                      >
                        👍
                      </button>
                      <button
                        onClick={() => submitFeedback(rec.id, 'not_helpful')}
                        className="feedback-btn not-helpful"
                        title="This recommendation is not helpful"
                      >
                        👎
                      </button>
                      <button
                        onClick={() => submitFeedback(rec.id, 'like')}
                        className="feedback-btn like"
                        title="I like this recommendation"
                      >
                        ❤️
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No specific recommendations at this time. Continue with your current chapter!</p>
            )}
          </div>
        )}
        
        {activeTab === 'analysis' && analysis && (
          <div className="analysis-section">
            <h4>Your Learning Analysis</h4>
            <div className="analysis-metrics">
              <div className="metric">
                <span className="metric-label">Engagement Level:</span>
                <span className="metric-value">{analysis.engagement_analysis?.engagement_level || 'Unknown'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Average Progress:</span>
                <span className="metric-value">{analysis.progress_metrics?.average_progress || 0}%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Learning Style:</span>
                <span className="metric-value">{analysis.learning_style || 'Unknown'}</span>
              </div>
            </div>
            
            <div className="strengths-weaknesses">
              <div className="strengths">
                <h5>Strengths</h5>
                <ul>
                  {analysis.strengths?.length > 0 ? analysis.strengths.map((strength, idx) => (
                    <li key={idx}>{strength.topic}</li>
                  )) : <li>No specific strengths identified yet</li>}
                </ul>
              </div>
              
              <div className="weaknesses">
                <h5>Areas for Improvement</h5>
                <ul>
                  {analysis.weaknesses?.length > 0 ? analysis.weaknesses.map((weakness, idx) => (
                    <li key={idx}>{weakness.topic}</li>
                  )) : <li>No specific areas identified yet</li>}
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'goals' && (
          <div className="goals-section">
            <h4>Your Learning Goals</h4>
            {learningPath?.learning_goals && learningPath.learning_goals.length > 0 ? (
              <ul className="goals-list">
                {learningPath.learning_goals.map((goal, index) => (
                  <li key={index} className={`goal-item status-${goal.status}`}>
                    <div className="goal-title">{goal.title}</div>
                    <div className="goal-status">{goal.status}</div>
                    <div className="goal-target">Target: {goal.target_date}</div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>You haven't set any specific learning goals yet.</p>
            )}
            
            <div className="progress-summary">
              <h5>Progress Summary</h5>
              {learningPath?.progress_summary && (
                <div className="summary-details">
                  <p><strong>Completed Sessions:</strong> {learningPath.progress_summary.completed_sessions}</p>
                  <p><strong>In Progress:</strong> {learningPath.progress_summary.in_progress_sessions}</p>
                  <p><strong>Average Progress:</strong> {learningPath.progress_summary.average_progress}%</p>
                  {learningPath.progress_summary.last_active_chapter && (
                    <p><strong>Last Active:</strong> {learningPath.progress_summary.last_active_chapter.chapter_title}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LearningAgent;