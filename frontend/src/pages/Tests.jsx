import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { testsAPI } from '../api/client';

const CATEGORY_ICONS = {
  personality: '🧠',
  emotional: '💜',
  wellness: '🌱',
  social: '💬',
};

export default function Tests() {
  const [tests, setTests] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    testsAPI.list(search).then(d => {
      setTests(d.tests);
      setFeatured(d.featured);
    }).catch(() => {});
  }, [search]);

  const featuredTest = featured[0];

  return (
    <div className="page">
      {/* Search */}
      <div className="search-bar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search tests"
        />
      </div>

      {/* Featured */}
      {featuredTest && (
        <Link to={`/tests/${featuredTest.id}`} style={{ textDecoration: 'none' }}>
          <div className="featured-banner">
            <div className="featured-badge">Featured Today</div>
            <h2>{featuredTest.title}</h2>
            <div className="featured-meta">
              <span>{featuredTest.duration_min} min</span>
              <span>{featuredTest.question_count} questions</span>
            </div>
            <button className="btn btn-lg" style={{ background: 'var(--warning)', color: 'white', border: 'none' }}>
              {featuredTest.taken ? 'Retake test →' : 'Take test →'}
            </button>
          </div>
        </Link>
      )}

      {/* Popular */}
      <div className="section-title">⭐ Most Popular</div>
      <div className="tests-grid">
        {tests.map(test => (
          <Link key={test.id} to={`/tests/${test.id}`} className="test-card">
            {test.taken && <div className="taken-badge">✓ Taken</div>}
            <div className="test-card-img" style={{ background: test.image_color + '20' }}>
              {CATEGORY_ICONS[test.category] || '📋'}
            </div>
            <div className="test-card-body">
              <h3>{test.title}</h3>
              <p>{test.description}</p>
              <div className="test-meta">
                <span>{test.duration_min} min</span>
                <span>{test.question_count} questions</span>
                {test.taken && <span style={{ background: 'var(--primary)', color: 'white' }}>Retake</span>}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
