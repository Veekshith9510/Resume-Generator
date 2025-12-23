// Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/**
 * Validates the provided job URL.
 * @param {string} url - The Job URL to validate (LinkedIn/Monster).
 * @returns {Promise<Object>} - The API response containing validation status and job ID.
 */
export const validateUrl = async (url) => {
    try {
        const response = await axios.post(`${API_URL}/validate-url`, { url });
        return response.data;
    } catch (error) {
        console.error("Error validating URL:", error);
        return { valid: false, message: "Error connecting to server" };
    }
};

/**
 * Uploads the resume file to the server.
 * @param {File} file - The resume file object.
 * @returns {Promise<Object>} - The API response containing resume ID.
 */
export const uploadResume = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post(`${API_URL}/upload-resume`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error("Error uploading resume:", error);
        throw error;
    }
};


export const previewOptimization = async (resumeId, jobId, apiKey = null) => {
    try {
        const response = await axios.post(`${API_URL}/preview-optimization`, {
            resume_id: resumeId,
            job_id: jobId,
            api_key: apiKey
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching preview:", error);
        if (error.response && error.response.data) {
            // Throw the actual server error message if available
            throw new Error(error.response.data.detail || error.response.data.message || "Server Error");
        }
        throw error;
    }
};

export async function generateResume(resumeId, jobId, apiKey = null, approvedPlan = null) {
    const response = await fetch(`${API_URL}/generate-resume`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            resume_id: resumeId,
            job_id: jobId,
            api_key: apiKey,
            approved_plan: approvedPlan
        }),
    });

    if (!response.ok) {
        throw new Error('Failed to start generation');
    }
    return response.json(); // { message: "...", download_url: "..." }
}

/**
 * Constructs the full download URL for a file.
 * @param {string} path - The relative path returned by the API or full URL.
 * @returns {string} - The absolute URL.
 */
export const getDownloadUrl = (path) => {
    if (path.startsWith('http')) {
        return path;
    }
    return `${API_URL}${path}`;
};
