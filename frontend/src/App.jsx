// Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import { useState } from 'react';
import './App.css';

import { validateUrl, uploadResume, generateResume, getDownloadUrl } from './api';
import ResumePreview from './ResumePreview';

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

  /**
   * Handles the Job URL submission.
   * Validates the URL via API and transitions state based on result.
   */
  const handleUrlSubmit = async () => {
    if (!url) return;
    setIsLoading(true);
    setMessage('Analyzing URL...');
    setStatus('analyzing');

    const result = await validateUrl(url);
    setIsLoading(false);

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
      setMessage(result.message);
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

    try {
      const result = await uploadResume(file);
      setResumeId(result.data.resume_id);
      setStatus('uploaded');
      setMessage(result.message);
    } catch (error) {
      setMessage('Error uploading resume');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Triggers the resume generation process.
   * Sends Job ID, Resume ID, and API Key to backend.
   * Updates state with download link and preview content.
   */
  const handleGenerate = async () => {
    if (!jobId || !resumeId) return;

    setIsLoading(true);
    setMessage('Generating resume with Copilot...');
    setStatus('generating');

    try {
      const result = await generateResume(jobId, resumeId, apiKey);
      const fileUrl = getDownloadUrl(result.download_url);
      setDownloadLink(fileUrl);
      setPreviewUrl(fileUrl); // Set content for preview
      setStatus('generated');
      setMessage(result.message);
    } catch (error) {
      setMessage('Error generating resume');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="scrolling-welcome">
        <span>Welcome Veekshith</span>
      </div>
      <header>

        <h1>Resume Generator</h1>
      </header>

      <main className="dashboard">
        <div className="card">
          <div className="input-group">
            <input
              type="text"
              placeholder="Paste LinkedIn or Monster Job URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={status === 'valid' || status === 'uploaded' || status === 'generated'}
            />
            <button
              onClick={handleUrlSubmit}
              disabled={isLoading || !url || status === 'valid' || status === 'uploaded' || status === 'generated'}
            >
              Enter
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
                placeholder="Optional: Enter Gemini/OpenAI API Key for Copilot"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="api-key-input"
              />
              <button className="generate-btn" onClick={handleGenerate} disabled={isLoading}>
                Generate Resume
              </button>
            </div>
          )}

          {status === 'generated' && (
            <div className="action-section fade-in">
              <a href={downloadLink} className="download-btn" target="_blank" rel="noopener noreferrer">
                Download Resume
              </a>
              {previewUrl && <ResumePreview fileUrl={previewUrl} />}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
