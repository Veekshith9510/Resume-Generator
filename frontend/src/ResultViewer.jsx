import React from 'react';

function ResultViewer({ result, onReset }) {
    if (!result) return null;

    return (
        <div className="card">
            <h2>3. Your New Resume</h2>
            <p>Success! Your resume has been rewritten to match the job description.</p>

            <div className="actions">
                <a href={result.download_url} target="_blank" rel="noopener noreferrer" className="download-btn">
                    Download Resume
                </a>
            </div>

            <br />
            <button className="secondary" onClick={onReset}>
                Start Over
            </button>
        </div>
    );
}

export default ResultViewer;
