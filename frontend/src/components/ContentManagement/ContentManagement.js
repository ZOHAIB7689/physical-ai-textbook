import React, { useState, useEffect } from 'react';

const ContentManagement = ({ currentUser }) => {
  const [activeTab, setActiveTab] = useState('overview'); // overview, translation, review, publish
  const [translations, setTranslations] = useState([]);
  const [contentItems, setContentItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0); // State to trigger refresh

  // Check if current user is an educator
  const isEducator = currentUser?.role === 'educator' || currentUser?.role === 'admin';

  useEffect(() => {
    if (isEducator) {
      fetchContentData();
    }
  }, [isEducator, refreshTrigger]); // Added refreshTrigger to dependencies

  const fetchContentData = async () => {
    try {
      setLoading(true);

      // Fetch translation sets
      const translationResponse = await fetch('/api/content-management/translations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (translationResponse.ok) {
        const translationData = await translationResponse.json();
        setTranslations(translationData);
      }

      // Fetch content items that need translation/review (this endpoint may need to be created)
      try {
        const contentResponse = await fetch('/api/modules', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (contentResponse.ok) {
          const contentData = await contentResponse.json();
          setContentItems(contentData);
        }
      } catch (contentError) {
        console.error('Error fetching content items:', contentError);
        // Fallback: show empty content items
        setContentItems([]);
      }
    } catch (error) {
      console.error('Error fetching content data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Function to update translation status
  const updateTranslationStatus = async (translationId, newStatus) => {
    try {
      const response = await fetch(`/api/content-management/translations/${translationId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          status: newStatus
        })
      });

      if (response.ok) {
        // Refresh the data to reflect the updates
        setRefreshTrigger(prev => prev + 1);
      } else {
        console.error('Failed to update translation status:', response.status);
      }
    } catch (error) {
      console.error('Error updating translation status:', error);
    }
  };

  if (!isEducator) {
    return (
      <div className="content-management-container">
        <div className="unauthorized-message">
          <h3>Access Denied</h3>
          <p>Only educators and administrators can access the content management system.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="content-management-container">
        <div className="loading">Loading content management tools...</div>
      </div>
    );
  }

  return (
    <div className="content-management-container">
      <div className="management-header">
        <h2>Content Management Dashboard</h2>
        <p>Manage textbook content, translations, and review materials</p>
      </div>
      
      <div className="management-tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'translation' ? 'active' : ''}
          onClick={() => setActiveTab('translation')}
        >
          Translation Management
        </button>
        <button 
          className={activeTab === 'review' ? 'active' : ''}
          onClick={() => setActiveTab('review')}
        >
          Content Review
        </button>
        <button 
          className={activeTab === 'publish' ? 'active' : ''}
          onClick={() => setActiveTab('publish')}
        >
          Publishing Tools
        </button>
      </div>
      
      <div className="management-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <h3>Content Dashboard</h3>
            <div className="dashboard-stats">
              <div className="stat-card">
                <h4>Content Items</h4>
                <p>{contentItems.length}</p>
              </div>
              <div className="stat-card">
                <h4>Translations</h4>
                <p>{translations.length}</p>
              </div>
              <div className="stat-card">
                <h4>Needs Review</h4>
                <p>{translations.filter(t => t.status === 'draft').length}</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'translation' && (
          <div className="translation-section">
            <h3>Translation Management</h3>
            <div className="translation-filters">
              <select>
                <option>All Languages</option>
                <option>Urdu</option>
                <option>Others</option>
              </select>
              <select>
                <option>All Statuses</option>
                <option>Draft</option>
                <option>Reviewed</option>
                <option>Approved</option>
              </select>
            </div>
            
            <div className="translation-list">
              {translations.map((translation, index) => (
                <div key={index} className="translation-item">
                  <div className="translation-header">
                    <span className="translation-entity">{translation.entity_type}: {translation.entity_id}</span>
                    <span className={`status status-${translation.status}`}>{translation.status}</span>
                  </div>
                  <div className="translation-preview">
                    {translation.translated_content.substring(0, 100)}...
                  </div>
                  <div className="translation-actions">
                    <button className="edit-btn">Edit</button>
                    <button className="review-btn">Review</button>
                    <button className="delete-btn">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'review' && (
          <div className="review-section">
            <h3>Content Review</h3>
            <div className="review-queue">
              <h4>Pending Reviews</h4>
              <ul>
                {translations.filter(t => t.status === 'draft').map((translation, index) => (
                  <li key={index} className="review-item">
                    <div className="review-content">
                      <strong>{translation.entity_type} {translation.entity_id}</strong>
                      <p>{translation.translated_content.substring(0, 150)}...</p>
                    </div>
                    <div className="review-actions">
                      <button 
                        className="approve-btn" 
                        onClick={() => updateTranslationStatus(translation.id, 'reviewed')}
                      >
                        Approve
                      </button>
                      <button 
                        className="request-changes-btn"
                        onClick={() => updateTranslationStatus(translation.id, 'draft')}
                      >
                        Request Changes
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        {activeTab === 'publish' && (
          <div className="publish-section">
            <h3>Publishing Tools</h3>
            <div className="publish-actions">
              <button className="publish-btn">Publish Content Updates</button>
              <button className="export-btn">Export Content Package</button>
              <button className="import-btn">Import Content Package</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentManagement;