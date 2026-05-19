import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { journalAPI } from '../api/client';

const MOOD_DATA = [
  { emoji: '😢', label: 'Very Sad' },
  { emoji: '😕', label: 'Sad' },
  { emoji: '😊', label: 'Normal' },
  { emoji: '😄', label: 'Happy' },
  { emoji: '🤩', label: 'Very Happy' },
];

const TYPE_NAMES = {
  release_worry: 'Release Worry',
  calm_anxiety: 'Calm Anxiety',
  feeling_angry: 'Feeling Angry',
  feeling_happy: 'Feeling Happy',
};

export default function JournalEntry() {
  const { type } = useParams();
  const navigate = useNavigate();
  const fileRef = useRef();

  const [prompts, setPrompts] = useState([]);
  const [answers, setAnswers] = useState({});
  const [mood, setMood] = useState(3);
  const [note, setNote] = useState('');
  const [feelings, setFeelings] = useState([]);
  const [activities, setActivities] = useState([]);
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState('');
  const [feelingOptions, setFeelingOptions] = useState([]);
  const [activityOptions, setActivityOptions] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    journalAPI.getPrompts(type).then(d => setPrompts(d.prompts)).catch(() => {});
    journalAPI.getOptions().then(d => {
      setFeelingOptions(d.feelings);
      setActivityOptions(d.activities);
    }).catch(() => {});
  }, [type]);

  const toggleChip = (list, setList, item) => {
    setList(list.includes(item) ? list.filter(x => x !== item) : [...list, item]);
  };

  const handlePhoto = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('journal_type', type);
      formData.append('note', note);
      formData.append('mood', mood);
      formData.append('feelings', JSON.stringify(feelings));
      formData.append('activities', JSON.stringify(activities));
      formData.append('answers', JSON.stringify(answers));
      if (photo) formData.append('photo', photo);

      await journalAPI.createEntry(formData);
      setSaved(true);
      setTimeout(() => navigate('/journal'), 1500);
    } catch (e) {
      alert('Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const moodInfo = MOOD_DATA[mood - 1] || MOOD_DATA[2];

  return (
    <div className="page journal-entry-page">
      <button className="back-btn" onClick={() => navigate('/journal')}>
        ← Back to Journal
      </button>

      <h2 style={{ marginBottom: '20px' }}>{TYPE_NAMES[type] || 'Journal Entry'}</h2>

      {saved && <div className="success-msg">Entry saved successfully! Redirecting...</div>}

      {/* Note */}
      <div className="note-section">
        <h3>Your Note</h3>
        <textarea value={note} onChange={e => setNote(e.target.value)} placeholder="Add a note..." />
      </div>

      {/* Guided Questions */}
      {prompts.map((p, i) => (
        <div key={p.id} className="question-card">
          <div className="q-num">Question {i + 1} of {prompts.length}</div>
          <div className="q-text">{p.question_text}</div>
          <textarea
            value={answers[p.id] || ''}
            onChange={e => setAnswers({ ...answers, [p.id]: e.target.value })}
            placeholder="Write your thoughts..."
          />
        </div>
      ))}

      {/* Mood */}
      <div className="mood-section">
        <h3>Mood</h3>
        <div className="mood-slider-container">
          <div className="mood-emoji">{moodInfo.emoji}</div>
          <div className="mood-label">{moodInfo.label}</div>
          <input
            type="range" min="1" max="5" value={mood}
            onChange={e => setMood(parseInt(e.target.value))}
            className="mood-slider"
          />
          <div className="mood-labels">
            <span>Unhappy</span>
            <span>Happy</span>
          </div>
        </div>
      </div>

      {/* Feelings */}
      <div className="chips-section">
        <h3>Which words describe your feelings?</h3>
        <div className="chips-grid">
          {feelingOptions.map(f => (
            <button
              key={f}
              className={`chip ${feelings.includes(f) ? 'selected' : ''}`}
              onClick={() => toggleChip(feelings, setFeelings, f)}
            >{f}</button>
          ))}
        </div>
      </div>

      {/* Activities */}
      <div className="chips-section">
        <h3>What have you been up to?</h3>
        <div className="chips-grid">
          {activityOptions.map(a => (
            <button
              key={a}
              className={`chip ${activities.includes(a) ? 'selected' : ''}`}
              onClick={() => toggleChip(activities, setActivities, a)}
            >{a}</button>
          ))}
        </div>
      </div>

      {/* Photo */}
      <div className="photo-section">
        <h3>What photo recaptures the atmosphere of the day?</h3>
        <div className="photo-upload" onClick={() => fileRef.current?.click()}>
          {photoPreview ? (
            <img src={photoPreview} alt="Preview" className="photo-preview" />
          ) : (
            <>
              <p style={{ fontSize: '32px', marginBottom: '8px' }}>📷</p>
              <p>Tap to upload a photo</p>
            </>
          )}
        </div>
        <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handlePhoto} />
      </div>

      <button className="btn btn-primary btn-lg" onClick={handleSave} disabled={saving} style={{ marginTop: '16px' }}>
        {saving ? 'Saving...' : 'Save Card'}
      </button>
    </div>
  );
}
