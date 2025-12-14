// frontend/src/context/PersonalizationContext.js
import React, { createContext, useContext, useReducer } from 'react';

const PersonalizationContext = createContext();

const initialState = {
  preferences: {
    language: 'en',
    theme: 'light',
    readingSpeed: 'medium', // slow, medium, fast
    contentDensity: 'balanced', // dense, balanced, sparse
  },
  recommendations: [],
  loading: false,
  error: null,
};

function personalizationReducer(state, action) {
  switch (action.type) {
    case 'SET_PREFERENCES':
      return {
        ...state,
        preferences: { ...state.preferences, ...action.payload },
      };
    case 'SET_RECOMMENDATIONS':
      return {
        ...state,
        recommendations: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'UPDATE_READING_PROGRESS':
      return {
        ...state,
        preferences: {
          ...state.preferences,
          lastReadChapter: action.payload.chapterId,
          lastReadPosition: action.payload.position,
        },
      };
    default:
      return state;
  }
}

export const PersonalizationProvider = ({ children }) => {
  const [state, dispatch] = useReducer(personalizationReducer, initialState);

  const setPreferences = (preferences) => {
    dispatch({ type: 'SET_PREFERENCES', payload: preferences });
  };

  const setRecommendations = (recommendations) => {
    dispatch({ type: 'SET_RECOMMENDATIONS', payload: recommendations });
  };

  const setLoading = (loading) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const updateReadingProgress = (chapterId, position) => {
    dispatch({ 
      type: 'UPDATE_READING_PROGRESS', 
      payload: { chapterId, position } 
    });
  };

  return (
    <PersonalizationContext.Provider
      value={{
        ...state,
        setPreferences,
        setRecommendations,
        setLoading,
        setError,
        updateReadingProgress,
      }}
    >
      {children}
    </PersonalizationContext.Provider>
  );
};

export const usePersonalization = () => {
  const context = useContext(PersonalizationContext);
  if (!context) {
    throw new Error('usePersonalization must be used within a PersonalizationProvider');
  }
  return context;
};