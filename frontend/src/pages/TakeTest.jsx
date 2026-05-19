import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { testsAPI } from '../api/client';

export default function TakeTest() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState(null);
  const [answers, setAnswers] = useState({});
  const [currentQ, setCurrentQ] = useState(0);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    testsAPI.get(id).then(d => setTest(d.test)).catch(() => navigate('/tests'));
  }, [id]);

  if (!test) return <div className="page"><div className="loading-screen"><div className="spinner" /></div></div>;

  const questions = test.questions || [];
  const q = questions[currentQ];
  const answeredCount = Object.keys(answers).length;
  const allAnswered = answeredCount === questions.length;

  const handleAnswer = (value) => {
    const newAnswers = { ...answers, [q.id]: value };
    setAnswers(newAnswers);
    if (currentQ < questions.length - 1) {
      setTimeout(() => setCurrentQ(currentQ + 1), 300);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const data = await testsAPI.submit(id, answers);
      setResult(data);
    } catch (e) {
      alert('Failed to submit. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (result) {
    return (
      <div className="page">
        <div className="result-card">
          <div className="result-score">{result.percentage}%</div>
          <h2>{test.title} Results</h2>
          <p>{result.result.result_text}</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-primary" onClick={() => navigate('/tests')}>
            Back to Tests
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page take-test-page">
      <button className="back-btn" onClick={() => navigate('/tests')} style={{ background: 'none', border: 'none', color: 'var(--primary)', fontWeight: 600, fontSize: '14px', cursor: 'pointer', marginBottom: '12px', fontFamily: 'inherit' }}>
        ← Back
      </button>

      <h2 style={{ marginBottom: '4px' }}>{test.title}</h2>

      {test.taken && (
        <div className="retake-banner">
          <span>🔄</span> Retake #{test.times_taken + 1} — questions are shuffled for a fresh experience!
        </div>
      )}

      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
        Answer True or False for each statement
      </p>

      <div className="progress-header">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(answeredCount / questions.length) * 100}%`, background: 'var(--primary)' }} />
        </div>
        <span>{answeredCount}/{questions.length}</span>
      </div>

      {/* Current Question */}
      {q && (
        <div className="tf-question">
          <p>{q.question_text}</p>
          <div className="tf-buttons">
            <button
              className={`tf-btn ${answers[q.id] === true ? 'selected-true' : ''}`}
              onClick={() => handleAnswer(true)}
            >True</button>
            <button
              className={`tf-btn ${answers[q.id] === false ? 'selected-false' : ''}`}
              onClick={() => handleAnswer(false)}
            >False</button>
          </div>
        </div>
      )}

      {/* Navigation dots */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '6px', margin: '16px 0' }}>
        {questions.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrentQ(i)}
            style={{
              width: i === currentQ ? '24px' : '8px',
              height: '8px',
              borderRadius: '4px',
              border: 'none',
              background: answers[questions[i].id] !== undefined ? 'var(--primary)' : 'var(--border)',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          />
        ))}
      </div>

      {allAnswered && (
        <button className="btn btn-success btn-lg" onClick={handleSubmit} disabled={submitting} style={{ marginTop: '12px' }}>
          {submitting ? 'Submitting...' : 'See Results'}
        </button>
      )}
    </div>
  );
}
