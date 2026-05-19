import { useEffect, useMemo, useState } from 'react';
import { homeAPI } from '../api/client';

function toIsoDay(dateValue) {
  const year = dateValue.getFullYear();
  const month = `${dateValue.getMonth() + 1}`.padStart(2, '0');
  const day = `${dateValue.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function weekFrom(selectedDate) {
  const start = new Date(selectedDate);
  start.setDate(selectedDate.getDate() - selectedDate.getDay());
  const days = [];
  const names = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
  for (let i = 0; i < 7; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    days.push({
      name: names[i],
      num: d.getDate(),
      date: new Date(d),
    });
  }
  return days;
}

function nextStatus(currentStatus) {
  if (currentStatus === 'pending') return 'done';
  if (currentStatus === 'done') return 'missed';
  return 'pending';
}

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const [summary, setSummary] = useState({ total: 0, done: 0, missed: 0, pending: 0, percentage: 0 });
  const [quest, setQuest] = useState({ tests_completed: 0, total_required: 3 });
  const [newTask, setNewTask] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [suggestions, setSuggestions] = useState(null);
  const [selectedDate, setSelectedDate] = useState(() => new Date());
  const [reflection, setReflection] = useState('');
  const [quote, setQuote] = useState('');
  const [quoteSource, setQuoteSource] = useState('MindBloom daily analysis');
  const [analyzing, setAnalyzing] = useState(false);
  const [loadingTasks, setLoadingTasks] = useState(true);
  const [error, setError] = useState('');

  const selectedDayIso = toIsoDay(selectedDate);
  const weekDays = useMemo(() => weekFrom(selectedDate), [selectedDate]);

  const prettyDate = useMemo(() => {
    return selectedDate.toLocaleDateString(undefined, {
      weekday: 'long',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  }, [selectedDate]);

  const completionCircumference = 150.8;
  const scoreOffset = completionCircumference - (completionCircumference * summary.percentage) / 100;

  useEffect(() => {
    homeAPI.getQuest().then((d) => setQuest(d)).catch(() => {});
    homeAPI.getSuggestions().then((d) => setSuggestions(d)).catch(() => {});
  }, []);

  const loadTasks = async (dayIso) => {
    setLoadingTasks(true);
    setError('');
    try {
      const data = await homeAPI.getTasks(dayIso);
      setTasks(data.tasks || []);
      setSummary({
        total: data.total || 0,
        done: data.done || 0,
        missed: data.missed || 0,
        pending: data.pending || 0,
        percentage: data.percentage || 0,
      });
    } catch (e) {
      setError('Could not load tasks for this day.');
    } finally {
      setLoadingTasks(false);
    }
  };

  useEffect(() => {
    loadTasks(selectedDayIso);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDayIso]);

  const toggleTaskStatus = async (task) => {
    const status = nextStatus(task.status || (task.completed ? 'done' : 'pending'));
    const optimistic = tasks.map((item) => (item.id === task.id ? { ...item, status, completed: status === 'done' } : item));
    setTasks(optimistic);
    const done = optimistic.filter((item) => item.status === 'done').length;
    const missed = optimistic.filter((item) => item.status === 'missed').length;
    const total = optimistic.length;
    setSummary({
      total,
      done,
      missed,
      pending: total - done - missed,
      percentage: total ? Math.round((done / total) * 100) : 0,
    });

    try {
      await homeAPI.toggleTask(task.id, { status });
    } catch (e) {
      await loadTasks(selectedDayIso);
    }
  };

  const updateTaskNoteLocal = (taskId, note) => {
    setTasks((prev) => prev.map((item) => (item.id === taskId ? { ...item, note } : item)));
  };

  const persistTaskNote = async (taskId, note) => {
    try {
      await homeAPI.toggleTask(taskId, { note });
    } catch (e) {}
  };

  const addTask = async (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;
    try {
      await homeAPI.addTask(newTask.trim(), 'custom', selectedDayIso);
      setNewTask('');
      setShowAdd(false);
      await loadTasks(selectedDayIso);
    } catch (e) {
      setError('Could not add task.');
    }
  };

  const runAnalysis = async () => {
    setAnalyzing(true);
    setError('');
    try {
      const data = await homeAPI.analyzeDay({ day: selectedDayIso, reflection });
      if (data?.result) {
        setSummary(data.result);
      }
      setQuote(data?.quote || 'You showed up today, and that already matters.');
      setQuoteSource(data?.quote_source || 'MindBloom daily analysis');
    } catch (e) {
      setError('Could not analyze your day right now.');
    } finally {
      setAnalyzing(false);
    }
  };

  const scoreLabel = summary.percentage === 100
    ? 'Perfect day!'
    : summary.percentage >= 80
      ? 'Excellent work!'
      : summary.percentage >= 60
        ? 'Good progress!'
        : summary.percentage >= 35
          ? 'Keep going!'
          : 'Ready to begin?';

  const scoreCaption = summary.percentage >= 60
    ? 'Consistency is shaping your growth.'
    : 'Small wins now will lift your next day.';

  return (
    <div className="tasknb-wrap">
      <div className="tasknb-header">
        <div>
          <h2>Daily Routine</h2>
          <p>{prettyDate}</p>
        </div>
        <div className="tasknb-header-actions">
          <span className="tasknb-date-pill">Day {selectedDate.getDate()}</span>
          <button type="button" className="tasknb-add-btn" onClick={() => setShowAdd((s) => !s)}>
            {showAdd ? 'Close' : 'Add Task'}
          </button>
        </div>
      </div>

      <div className="tasknb-days">
        {weekDays.map((day) => {
          const isActive = toIsoDay(day.date) === selectedDayIso;
          return (
            <button
              key={toIsoDay(day.date)}
              type="button"
              className={`tasknb-day ${isActive ? 'active' : ''}`}
              onClick={() => setSelectedDate(new Date(day.date))}
            >
              <span className="tasknb-day-name">{day.name}</span>
              <span className="tasknb-day-num">{day.num}</span>
            </button>
          );
        })}
      </div>

      {showAdd && (
        <form className="tasknb-add-form" onSubmit={addTask}>
          <input
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="Add a new daily task"
            aria-label="New task title"
          />
          <button type="submit">Add</button>
        </form>
      )}

      {error && <div className="tasknb-error">{error}</div>}

      <section className="tasknb-book">
        <div className="tasknb-book-header">
          <div className="tasknb-book-title">Task Checklist</div>
          <div className="tasknb-book-meta">tap to toggle · add notes</div>
        </div>
        <div className="tasknb-col-heads">
          <div>#</div>
          <div>Task</div>
          <div className="center">Status</div>
          <div>Notes</div>
        </div>

        {loadingTasks ? (
          <div className="tasknb-loading">Loading tasks...</div>
        ) : (
          <div>
            {tasks.map((task, index) => {
              const taskStatus = task.status || (task.completed ? 'done' : 'pending');
              return (
                <div key={task.id} className={`tasknb-task-row ${taskStatus}`}>
                  <div className="tasknb-num">{index + 1}</div>
                  <div className="tasknb-task-label">{task.title}</div>
                  <button
                    type="button"
                    className={`tasknb-status-btn ${taskStatus}`}
                    onClick={() => toggleTaskStatus(task)}
                    aria-label={`Toggle status for ${task.title}`}
                  >
                    {taskStatus === 'done' ? '✓' : taskStatus === 'missed' ? '✗' : ''}
                  </button>
                  <textarea
                    className="tasknb-note-input"
                    rows={1}
                    value={task.note || ''}
                    onChange={(e) => updateTaskNoteLocal(task.id, e.target.value)}
                    onBlur={(e) => persistTaskNote(task.id, e.target.value)}
                    placeholder="add note..."
                  />
                </div>
              );
            })}
          </div>
        )}
      </section>

      <section className="tasknb-score-band">
        <div className="tasknb-score-ring">
          <svg viewBox="0 0 58 58">
            <circle cx="29" cy="29" r="24" fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth="5" />
            <circle
              cx="29"
              cy="29"
              r="24"
              fill="none"
              stroke="#7c6cff"
              strokeWidth="5"
              strokeLinecap="round"
              strokeDasharray={completionCircumference}
              strokeDashoffset={scoreOffset}
            />
          </svg>
          <div className="tasknb-score-pct">{summary.percentage}%</div>
        </div>
        <div className="tasknb-score-info">
          <h3>{scoreLabel}</h3>
          <p>{scoreCaption}</p>
          <div className="tasknb-score-fraction">{summary.done} / {summary.total} tasks done</div>
        </div>
      </section>

      <section className="tasknb-reflection">
        <div className="tasknb-reflection-head">Reflection for today...</div>
        <textarea
          value={reflection}
          onChange={(e) => setReflection(e.target.value)}
          placeholder="How did today feel? What went well? What could be better?"
        />
      </section>

      <button type="button" className="tasknb-analyze-btn" onClick={runAnalysis} disabled={analyzing}>
        {analyzing ? 'Analyzing your day...' : 'Analyze my day & get a quote'}
      </button>

      {quote && (
        <section className="tasknb-quote-card">
          <div className="tasknb-quote-mark">"</div>
          <div className="tasknb-quote-text">{quote}</div>
          <div className="tasknb-quote-source">{quoteSource}</div>
          <button type="button" className="tasknb-quote-refresh" onClick={runAnalysis} disabled={analyzing}>
            {analyzing ? 'Refreshing...' : 'New motivating quote'}
          </button>
        </section>
      )}

      {suggestions?.insight && (
        <section className="tasknb-insight-card" style={{ background: suggestions.insight.color }}>
          <div className="insight-emoji">{suggestions.insight.emoji}</div>
          <div>
            <div className="insight-text">{suggestions.insight.message}</div>
            <div className="insight-sub">{suggestions.time_context}</div>
          </div>
        </section>
      )}

      {suggestions?.music?.length > 0 && (
        <section className="ai-section">
          <h3>Music For Your Mood</h3>
          {suggestions.music.map((item, index) => (
            <div key={index} className="music-card">
              <div className="music-emoji">{item.emoji}</div>
              <div className="music-info">
                <h4>{item.title}</h4>
                <div className="music-artist">{item.artist}</div>
                <div className="music-reason">{item.reason}</div>
              </div>
              <div className="music-genre">{item.genre}</div>
            </div>
          ))}
        </section>
      )}

      {suggestions?.activities?.length > 0 && (
        <section className="ai-section">
          <h3>Suggested Activities</h3>
          {suggestions.activities.map((item, index) => (
            <div key={index} className="activity-card">
              <div className="activity-emoji">{item.emoji}</div>
              <div className="activity-info">
                <h4>{item.title}</h4>
                <p>{item.benefit}</p>
              </div>
              <div className="activity-duration">{item.duration}</div>
            </div>
          ))}
        </section>
      )}

      <section className="quest-card">
        <h3>Self-Discovery Quest</h3>
        <p>Take {quest.total_required} tests to unlock a reward and better understand yourself</p>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${quest.total_required ? (quest.tests_completed / quest.total_required) * 100 : 0}%` }}
          />
        </div>
        <span className="progress-text">{quest.tests_completed}/{quest.total_required}</span>
      </section>
    </div>
  );
}
