// Copyright (c) 2025 Veekshith Gullapudi. All rights reserved.

import axios from 'axios';

const API_URL = 'http://127.0.0.1:8002';

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

/**
 * Requests the server to generate a tailored resume.
 * @param {number} jobId - The ID of the job post.
 * @param {number} resumeId - The ID of the uploaded resume.
 * @param {string} [apiKey] - Optional Gemini API Key.
 * @returns {Promise<Object>} - The API response containing the download URL.
 */
export const generateResume = async (jobId, resumeId, apiKey = null) => {
    try {
        const response = await axios.post(`${API_URL}/generate-resume`, {
            job_id: jobId,
            resume_id: resumeId,
            api_key: apiKey
        });
        return response.data;
    } catch (error) {
        console.error("Error generating resume:", error);
        throw error;
    }
};


/**
 * Constructs the full download URL for a file.
 * @param {string} path - The relative path returned by the API.
 * @returns {string} - The absolute URL.
 */
export const getDownloadUrl = (path) => {
    return `${API_URL}${path}`;
};
