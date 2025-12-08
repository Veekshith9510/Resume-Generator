// Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import { useState, useEffect } from 'react';
import mammoth from 'mammoth';
import './ResumePreview.css';

function ResumePreview({ fileUrl }) {
    const [htmlContent, setHtmlContent] = useState('');
    const [error, setError] = useState('');

    /**
     * Effect hook to fetch and parse the DOCX file when fileUrl changes.
     * Uses mammoth to convert DOCX ArrayBuffer to HTML.
     */
    useEffect(() => {
        const fetchAndParse = async () => {
            if (!fileUrl) return;

            try {
                const response = await fetch(fileUrl);
                const arrayBuffer = await response.arrayBuffer();

                const result = await mammoth.convertToHtml({ arrayBuffer });
                setHtmlContent(result.value);
            } catch (err) {
                console.error("Error parsing DOCX:", err);
                setError("Failed to load preview.");
            }
        };

        fetchAndParse();
    }, [fileUrl]);

    if (error) {
        return <div className="preview-error">{error}</div>;
    }

    return (
        <div className="resume-preview">
            <h3>Preview</h3>
            <div
                className="preview-content"
                dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
        </div>
    );
}

export default ResumePreview;
