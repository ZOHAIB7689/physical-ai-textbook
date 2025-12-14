// frontend/src/services/personalizationService.js

class PersonalizationService {
  constructor(apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '/api') {
    this.apiBaseUrl = apiBaseUrl;
  }

  async getUserLearningPatterns(userId) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/users/${userId}/learning-patterns`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting user learning patterns:', error);
      throw error;
    }
  }

  async getPersonalizedRecommendations(userId) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/users/${userId}/recommendations`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting personalized recommendations:', error);
      throw error;
    }
  }

  async updatePersonalizedSettings(userId, settings) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/users/${userId}/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(settings)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating personalized settings:', error);
      throw error;
    }
  }
}

export default new PersonalizationService();