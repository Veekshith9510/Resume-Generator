import { useState } from 'react';
import './App.css';

import { validateUrl, uploadResume, generateResume, getDownloadUrl, previewOptimization } from './api';
import ResumePreview from './ResumePreview';
import OptimizationReview from './OptimizationReview';

function App() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState(''); // 'valid', 'invalid', 'analyzing', 'uploaded', 'generating', 'generated'
  const [message, setMessage] = useState('');
  const [jobId, setJobId] = useState(null);
  const [resumeId, setResumeId] = useState(null);
  const [downloadLink, setDownloadLink] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState(''); // New state for API Key
  const [previewUrl, setPreviewUrl] = useState(''); // New state for Preview URL
  const [optimizationPlan, setOptimizationPlan] = useState(null); // New state for the plan


  /**
   * Handles the Job URL submission.
   * Validates the URL via API and transitions state based on result.
   */
  const handleUrlSubmit = async () => {
    if (!url) return;
    setIsLoading(true);
    setMessage('Analyzing URL...');
    setStatus('analyzing');

    try {
      const result = await validateUrl(url);

      if (result.valid) {
        setStatus('valid');
        setMessage(result.message);
        setJobId(result.data.job_id);
        // Wait briefly before prompting for resume upload
        setTimeout(() => {
          setMessage("The Process has analyzed the Job Description, Upload a Resume to generate a new resume");
        }, 1500);
      } else {
        setStatus('invalid');
        setMessage(result.message || 'Invalid Job URL');
      }
    } catch (error) {
      setStatus('invalid');
      setMessage('Error validating URL');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handles the Resume file upload.
   * Uploads file to backend and stores the returned resume ID.
   */
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setMessage('Uploading resume...');
    setStatus('uploading');

    try {
      const result = await uploadResume(file);
      // Check if result has date.resume_id or direct property depending on api.js implementation
      // Assuming result.data.resume_id based on previous code usage
      const id = result.data ? result.data.resume_id : result.resume_id;

      if (id) {
        setResumeId(id);
        setStatus('uploaded');
        setMessage(result.message || 'Resume uploaded successfully');
      } else {
        throw new Error('No resume ID returned');
      }
    } catch (error) {
      console.error(error);
      setMessage('Error uploading resume');
      setStatus('valid'); // Revert to valid so user can try again
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Fetches the optimization plan from the AI.
   */
  const handlePreview = async () => {
    if (!jobId || !resumeId) return;
    setIsLoading(true);
    setMessage('AI is analyzing your experience and job requirements...');
    setStatus('previewing');

    try {
      const plan = await previewOptimization(resumeId, jobId, apiKey);
      setOptimizationPlan(plan);
      setStatus('reviewing');
      setMessage('Optimization plan ready for review.');
    } catch (error) {
      console.error(error);
      setMessage(error.message || 'Error fetching optimization plan');
      setStatus('uploaded');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Triggers the final resume generation process with the approved plan.
   */
  const handleGenerate = async (approvedPlan = null) => {
    if (!jobId || !resumeId) return;

    setIsLoading(true);
    setMessage('Generating final tailored resume...');
    setStatus('generating');

    try {
      const result = await generateResume(resumeId, jobId, apiKey, approvedPlan || optimizationPlan);

      if (result.download_url) {
        setDownloadLink(getDownloadUrl(result.download_url));
        setStatus('generated');
        setMessage('Resume generated successfully!');
      } else {
        throw new Error('No download URL returned');
      }
    } catch (error) {
      console.error(error);
      setMessage('Error generating resume');
      setStatus('reviewing');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Resume Generator</h1>
        <p>Tailor your resume to any job description in seconds.</p>
      </header>

      <main className="main-content">
        <div className="input-section">
          <input
            type="text"
            placeholder="Paste Job URL (LinkedIn/Monster)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading || status === 'analyzing'}
            className="url-input"
          />
          <button
            onClick={handleUrlSubmit}
            disabled={!url || isLoading || status === 'analyzing'}
            className="submit-btn"
          >
            Analyze Job
          </button>
        </div>

        {isLoading && <div className="status-message analyzing">Processing...</div>}
        {!isLoading && message && <div className={`status-message ${status}`}>{message}</div>}

        {status === 'valid' && (
          <div className="action-section fade-in">
            <label className="upload-btn">
              Upload Resume
              <input type="file" onChange={handleFileUpload} accept=".pdf,.docx" hidden />
            </label>
          </div>
        )}

        {status === 'uploaded' && (
          <div className="action-section fade-in">
            <input
              type="password"
              placeholder="Optional: Enter Gemini API Key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="api-key-input"
            />
            <button className="generate-btn" onClick={handlePreview} disabled={isLoading}>
              Analyze & Preview
            </button>
          </div>
        )}

        {status === 'reviewing' && optimizationPlan && (
          <OptimizationReview
            plan={optimizationPlan}
            onApprove={handleGenerate}
            onCancel={() => setStatus('uploaded')}
          />
        )}

        {status === 'generated' && (
          <div className="action-section fade-in">
            <a href={downloadLink} className="download-btn" target="_blank" rel="noopener noreferrer">
              Download Resume
            </a>
            {previewUrl && <ResumePreview fileUrl={previewUrl} />}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
