import { useEffect, useMemo, useState } from 'react';
import { adminAPI } from '../../api/client';

export default function ModelManager({ onRetrainComplete }) {
  const [epochs, setEpochs] = useState(40);
  const [batchSize, setBatchSize] = useState(32);
  const [contamination, setContamination] = useState(0.1);
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState('');
  const [jobs, setJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobError, setJobError] = useState('');
  const [selectedJobId, setSelectedJobId] = useState(null);

  useEffect(() => () => setRunning(false), []);

  const selectedJob = useMemo(
    () => jobs.find((job) => job.job_id === selectedJobId) || jobs[0] || null,
    [jobs, selectedJobId],
  );

  const loadJobs = async () => {
    setJobsLoading(true);
    setJobError('');
    try {
      const res = await adminAPI.listModelJobs({ model_dir: 'backend/ml_models' });
      const nextJobs = res?.jobs || [];
      setJobs(nextJobs);
      setSelectedJobId((current) => current || nextJobs[0]?.job_id || null);
    } catch (err) {
      setJobError('Unable to load training history.');
    } finally {
      setJobsLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const startPoll = async (jobId, modelDir) => {
    setRunning(true);
    setMessage('Polling job status...');
    try {
      while (true) {
        const res = await adminAPI.getModelJob(jobId, { model_dir: modelDir });
        const job = res?.job;
        if (!job) { setMessage('Job not found'); break; }
        setMessage(`Status: ${job.status}`);
        if (job.status === 'completed') { setMessage('Retrain complete'); onRetrainComplete?.(job); await loadJobs(); break; }
        if (job.status === 'failed') { setMessage('Retrain failed'); await loadJobs(); break; }
        // wait
        // eslint-disable-next-line no-await-in-loop
        await new Promise((r) => setTimeout(r, 2000));
      }
    } catch (e) {
      setMessage('Error polling job status');
    } finally {
      setRunning(false);
    }
  };

  const handleRetrain = async () => {
    setMessage('');
    try {
      const payload = { epochs, batch_size: batchSize, contamination };
      const res = await adminAPI.retrain(payload);
      setMessage(res?.message || 'Retrain started');
      await loadJobs();
      if (res?.job_id) startPoll(res.job_id, res.model_dir || 'backend/ml_models');
    } catch (err) {
      setMessage(err?.data?.errors?.[0] || 'Retrain failed');
    }
  };

  return (
    <div className="admin-panel admin-model-panel" style={{ marginTop: 16 }}>
      <div className="admin-panel-header">
        <div>
          <h2>Model Manager</h2>
          <span>Train, inspect, and manage model artifacts</span>
        </div>
        <button className="mini-button" type="button" onClick={loadJobs}>Refresh history</button>
      </div>
      <div className="admin-model-grid">
        <div className="admin-model-form">
          <div className="admin-field-row">
            <label>Epochs</label>
            <input type="number" min={1} value={epochs} onChange={(e) => setEpochs(Number(e.target.value))} />
          </div>
          <div className="admin-field-row">
            <label>Batch</label>
            <input type="number" min={1} value={batchSize} onChange={(e) => setBatchSize(Number(e.target.value))} />
          </div>
          <div className="admin-field-row">
            <label>Contamination</label>
            <input type="number" step="0.01" min="0" max="0.5" value={contamination} onChange={(e) => setContamination(Number(e.target.value))} />
          </div>
          <button className="admin-button primary" onClick={handleRetrain} disabled={running}>{running ? 'Running...' : 'Retrain Model'}</button>
          {message && <div className="admin-model-message">{message}</div>}
        </div>

        <div className="admin-model-history">
          <div className="admin-model-history-head">
            <div>
              <h3>Training history</h3>
              <p>Recent job runs and their latest state</p>
            </div>
            <span className="admin-section-pill">{jobs.length} jobs</span>
          </div>

          {jobsLoading ? (
            <div className="admin-empty-state">Loading job history...</div>
          ) : jobError ? (
            <div className="admin-empty-state">{jobError}</div>
          ) : jobs.length === 0 ? (
            <div className="admin-empty-state">No model jobs yet.</div>
          ) : (
            <div className="admin-job-list">
              {jobs.slice(0, 5).map((job) => (
                <button
                  type="button"
                  key={job.job_id}
                  className={`admin-job-item ${selectedJob?.job_id === job.job_id ? 'active' : ''}`}
                  onClick={() => setSelectedJobId(job.job_id)}
                >
                  <div>
                    <div className="admin-job-title">{job.job_id.slice(0, 8)}</div>
                    <div className="admin-job-sub">{job.meta?.contamination ?? 'n/a'} contamination</div>
                  </div>
                  <span className={`admin-status-pill severity-${job.status === 'completed' ? 1 : job.status === 'failed' ? 5 : 2}`}>
                    {job.status}
                  </span>
                </button>
              ))}
            </div>
          )}

          {selectedJob && (
            <div className="admin-job-detail">
              <div className="admin-job-detail-row">
                <span>Job</span>
                <strong>{selectedJob.job_id}</strong>
              </div>
              <div className="admin-job-detail-row">
                <span>Started</span>
                <strong>{selectedJob.started_at ? new Date(selectedJob.started_at).toLocaleString() : '—'}</strong>
              </div>
              <div className="admin-job-detail-row">
                <span>Completed</span>
                <strong>{selectedJob.completed_at ? new Date(selectedJob.completed_at).toLocaleString() : '—'}</strong>
              </div>
              <div className="admin-job-detail-row">
                <span>Model dir</span>
                <strong>{selectedJob.model_dir || 'backend/ml_models'}</strong>
              </div>
              <div className="admin-job-log">
                <span>Latest log</span>
                <div>
                  {(selectedJob.log || []).slice(-3).map((entry, index) => (
                    <div key={`${entry.at}-${index}`} className="admin-job-log-line">
                      {entry.note}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
