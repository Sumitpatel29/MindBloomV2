import { useState, useEffect } from 'react';
import { growthAPI } from '../api/client';

export default function Growth() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [pastResults, setPastResults] = useState([]);
  const [started, setStarted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [hasTaken, setHasTaken] = useState(false);

  useEffect(() => {
    growthAPI.getAssessment().then(d => {
      setQuestions(d.questions);
      setHasTaken(d.has_taken || false);
    }).catch(() => {});
    growthAPI.getResults().then(d => setPastResults(d.results)).catch(() => {});
  }, []);

  const answeredCount = Object.keys(answers).length;

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const data = await growthAPI.submitAssessment(answers);
      setResult(data);
    } catch (e) {
      alert('Failed to submit. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (result) {
    const summary = result.summary;
    return (
      <div className="page">
        <div className="result-card">
          <div className="result-score">{result.percentage}%</div>
          <h2>{summary.category}</h2>
          <p>{summary.summary}</p>
        </div>
        <h3 style={{ marginBottom: '12px' }}>Tips for You</h3>
        <ul className="tips-list">
          {summary.tips.map((tip, i) => <li key={i}>{tip}</li>)}
        </ul>
        <button className="btn btn-primary" onClick={() => { setResult(null); setStarted(false); setAnswers({}); }} style={{ marginTop: '16px' }}>
          Take Again
        </button>
      </div>
    );
  }

  if (!started) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Growth</h1>
        </div>

        <div className="growth-hero">
          <div className="hero-icon">🧩</div>
          <h2>Personal Growth Assessment</h2>
          <p>Discover where you are on your growth journey. Answer {questions.length} questions to get personalized insights and tips.</p>
        </div>

        <button className="btn btn-success btn-lg" onClick={() => setStarted(true)}>
          {hasTaken ? '🔄 Retake Assessment' : 'Take Assessment'}
        </button>

        {hasTaken && (
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '13px', marginTop: '8px' }}>
            Questions will be shuffled for a fresh experience!
          </p>
        )}

        {pastResults.length > 0 && (
          <div className="entries-section" style={{ marginTop: '24px' }}>
            <h3 className="section-title">📊 Past Assessments</h3>
            {pastResults.map(r => (
              <div key={r.id} className="entry-item">
                <div className="entry-icon" style={{ background: '#E8F5E9' }}>📊</div>
                <div className="entry-details">
                  <h4>{r.category || 'Assessment'}</h4>
                  <p>Score: {r.score} · {new Date(r.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="page">
      <button onClick={() => setStarted(false)} style={{ background: 'none', border: 'none', color: 'var(--primary)', fontWeight: 600, fontSize: '14px', cursor: 'pointer', marginBottom: '12px', fontFamily: 'inherit' }}>
        ← Back
      </button>

      <h2 style={{ marginBottom: '4px' }}>Growth Assessment</h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
        For each statement, choose True or False based on how you genuinely feel.
      </p>

      <div className="progress-header" style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <div className="progress-bar" style={{ flex: 1, margin: 0 }}>
          <div className="progress-fill" style={{ width: `${(answeredCount / questions.length) * 100}%`, background: 'var(--success)' }} />
        </div>
        <span style={{ fontSize: '13px', color: 'var(--muted)', fontWeight: 600 }}>{answeredCount}/{questions.length}</span>
      </div>

      {questions.map(q => (
        <div key={q.id} className="assessment-q">
          <div className="aq-cat">{q.category.replace(/_/g, ' ')}</div>
          <p>{q.question_text}</p>
          <div className="tf-buttons">
            <button
              className={`tf-btn ${answers[q.id] === true ? 'selected-true' : ''}`}
              onClick={() => setAnswers({ ...answers, [q.id]: true })}
            >True</button>
            <button
              className={`tf-btn ${answers[q.id] === false ? 'selected-false' : ''}`}
              onClick={() => setAnswers({ ...answers, [q.id]: false })}
            >False</button>
          </div>
        </div>
      ))}

      {answeredCount === questions.length && (
        <button className="btn btn-success btn-lg" onClick={handleSubmit} disabled={submitting} style={{ marginTop: '12px' }}>
          {submitting ? 'Analyzing...' : 'See My Results'}
        </button>
      )}
    </div>
  );
}
