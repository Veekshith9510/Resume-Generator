import React, { useState } from 'react';
import { generateResume } from './api';

function JobUrlInput({ resumeId, onGenerationStarted }) {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async () => {
        if (!url) {
            setError("Please enter a valid URL.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const data = await generateResume(resumeId, url);
            // Backend returns { status: "success", download_url: "..." }
            // If it returns immediately, we can show result.
            // If it allows polling, we might handle that.
            // The current Lambda implementation returns the download URL immediately (synchronous generation).
            onGenerationStarted(data);
        } catch (err) {
            setError("Failed to generate resume. Please check the URL and try again.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>2. Enter Job Description URL</h2>
            <div className="input-group">
                <input
                    type="url"
                    placeholder="https://linkedin.com/jobs/..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />
            </div>
            {error && <p className="error">{error}</p>}
            <button onClick={handleSubmit} disabled={!url || loading}>
                {loading ? "Generating..." : "Generate Resume"}
            </button>
        </div>
    );
}

export default JobUrlInput;
