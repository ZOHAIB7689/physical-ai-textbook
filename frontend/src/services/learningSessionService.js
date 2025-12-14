// frontend/src/services/learningSessionService.js

class LearningSessionService {
  constructor(apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '/api') {
    this.apiBaseUrl = apiBaseUrl;
  }

  async createLearningSession(sessionData) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/learning-sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}` // Assuming JWT token is stored in localStorage
        },
        body: JSON.stringify(sessionData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating learning session:', error);
      throw error;
    }
  }

  async getLearningSessionByUserAndChapter(userId, chapterId) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/learning-sessions/user/${userId}/chapter/${chapterId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // No session exists yet
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting learning session:', error);
      throw error;
    }
  }

  async updateLearningSession(sessionId, updateData) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/learning-sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating learning session:', error);
      throw error;
    }
  }

  async updateProgress(sessionId, progress, page) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/learning-sessions/${sessionId}/progress`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          progress_percentage: progress,
          last_accessed_page: page
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating progress:', error);
      throw error;
    }
  }
}

export default new LearningSessionService();