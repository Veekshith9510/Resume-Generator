import React, { useState } from 'react';

const OptimizationReview = ({ plan, onApprove, onCancel }) => {
    const [editedPlan, setEditedPlan] = useState(plan);

    const handleSummaryChange = (val) => {
        setEditedPlan({
            ...editedPlan,
            summary: { ...editedPlan.summary, optimized: val }
        });
    };

    const handleCompanyChange = (val) => {
        setEditedPlan({ ...editedPlan, company_name: val });
    };

    const handleBulletChange = (entryIdx, bulletIdx, val) => {
        const newEntries = [...editedPlan.experience_entries];
        newEntries[entryIdx].optimized_bullets[bulletIdx] = val;
        setEditedPlan({ ...editedPlan, experience_entries: newEntries });
    };

    return (
        <div className="optimization-review-container fade-in">
            <h2>Preview & Edit Optimization</h2>
            <p>Review the AI-suggested changes for your resume. You can edit any field before generating the final document.</p>

            <div className="review-section">
                <h3>Target Company (used for filename)</h3>
                <div className="summary-edit">
                    <input
                        type="text"
                        value={editedPlan.company_name}
                        onChange={(e) => handleCompanyChange(e.target.value)}
                        className="company-input"
                        placeholder="e.g. Vlink.inc"
                    />
                </div>
            </div>

            <div className="review-section">
                <h3>Professional Summary</h3>
                <div className="summary-edit">
                    <label>Original:</label>
                    <div className="read-only">{plan.summary.original}</div>
                    <label>Optimized:</label>
                    <textarea
                        value={editedPlan.summary.optimized}
                        onChange={(e) => handleSummaryChange(e.target.value)}
                        rows={4}
                    />
                </div>
            </div>

            <div className="review-section">
                <h3>Work Experience</h3>
                {editedPlan.experience_entries.map((entry, eIdx) => (
                    <div key={eIdx} className="entry-review">
                        <h4>{entry.header}</h4>

                        <div className="original-section">
                            <label>Original:</label>
                            <ul className="original-list">
                                {plan.experience_entries[eIdx].bullets && plan.experience_entries[eIdx].bullets.map((b, i) => (
                                    <li key={i}>{b}</li>
                                ))}
                                {(!plan.experience_entries[eIdx].bullets || plan.experience_entries[eIdx].bullets.length === 0) && (
                                    <li>(No bullet points detected)</li>
                                )}
                            </ul>
                        </div>

                        <label>Optimized & New (Editable):</label>
                        {entry.optimized_bullets.map((bullet, bIdx) => (
                            <div key={bIdx} className="bullet-edit">
                                <textarea
                                    value={bullet}
                                    onChange={(e) => handleBulletChange(eIdx, bIdx, e.target.value)}
                                    rows={2}
                                />
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            <div className="review-actions">
                <button className="cancel-btn" onClick={onCancel}>Cancel</button>
                <button className="generate-btn" onClick={() => onApprove(editedPlan)}>
                    Generate Final Resume
                </button>
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .optimization-review-container {
                    background: rgba(255, 255, 255, 0.05);
                    padding: 20px;
                    border-radius: 12px;
                    margin-top: 20px;
                    text-align: left;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .review-section { margin-bottom: 25px; }
                .summary-edit textarea, .bullet-edit textarea, .company-input {
                    width: 100%;
                    background: #1a1a1a;
                    color: #fff;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 10px;
                    margin-top: 8px;
                    font-family: inherit;
                    line-height: 1.5;
                }
                .read-only {
                    font-size: 0.9em;
                    color: #888;
                    margin-bottom: 10px;
                    font-style: italic;
                }
                .entry-review {
                    margin-bottom: 20px;
                    padding-left: 15px;
                    border-left: 2px solid #007bff;
                }
                .original-section {
                    margin-bottom: 15px;
                    padding: 10px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 6px;
                }
                .original-list {
                    padding-left: 20px;
                    color: #aaa;
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                .bullet-edit { margin-bottom: 10px; }
                .review-actions {
                    display: flex;
                    gap: 15px;
                    justify-content: flex-end;
                    margin-top: 20px;
                }
                .cancel-btn {
                    background: transparent;
                    border: 1px solid #444;
                    color: #fff;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                }
            `}} />
        </div>
    );
};

export default OptimizationReview;
