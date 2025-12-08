import axios from 'axios';

const API_URL = 'http://127.0.0.1:8002';

export const validateUrl = async (url) => {
    try {
        const response = await axios.post(`${API_URL}/validate-url`, { url });
        return response.data;
    } catch (error) {
        console.error("Error validating URL:", error);
        return { valid: false, message: "Error connecting to server" };
    }
};

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


export const getDownloadUrl = (path) => {
    return `${API_URL}${path}`;
};
