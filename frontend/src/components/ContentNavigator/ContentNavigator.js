import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const ContentNavigator = ({ modules }) => {
  const router = useRouter();
  const [selectedModule, setSelectedModule] = useState(null);
  const [expandedModules, setExpandedModules] = useState({});

  useEffect(() => {
    // Set the currently selected module based on the URL
    if (router.query.moduleId) {
      setSelectedModule(router.query.moduleId);
      setExpandedModules(prev => ({ ...prev, [router.query.moduleId]: true }));
    }
  }, [router.query.moduleId]);

  const toggleModule = (moduleId) => {
    setExpandedModules(prev => ({
      ...prev,
      [moduleId]: !prev[moduleId]
    }));
  };

  return (
    <div className="content-navigator">
      <h2>Textbook Contents</h2>
      <ul className="module-list">
        {modules?.map(module => (
          <li key={module.id} className="module-item">
            <button 
              className={`module-title ${selectedModule === module.id ? 'selected' : ''}`}
              onClick={() => toggleModule(module.id)}
            >
              {module.title}
            </button>
            
            {expandedModules[module.id] && (
              <ul className="chapter-list">
                {module.chapters?.map(chapter => (
                  <li key={chapter.id} className="chapter-item">
                    <Link href={`/chapter/${chapter.slug}`}>
                      <a className={`chapter-link ${router.query.chapterId === chapter.id ? 'current' : ''}`}>
                        {chapter.chapter_number}. {chapter.title}
                      </a>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ContentNavigator;