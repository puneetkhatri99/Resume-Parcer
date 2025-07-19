import React, { useState } from 'react';
import axios from 'axios';

const JobDescriptionAI = () => {
  const [jobInput, setJobInput] = useState('');
  const [promptInput, setPromptInput] = useState('');
  const [generatedOutput, setGeneratedOutput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5050/generateDes', {
        job_summary: jobInput || 'No description provided.'
      });
      
      setGeneratedOutput(response.data.job_description);
    } catch (error) {
      console.error('Error generating job description:', error);
      setGeneratedOutput('❌ Error generating output.');
    }
    setLoading(false);
  };

  const handleCopy = () => {
    setJobInput(generatedOutput);
  };

  return (
    <div
      style={{
        maxWidth: '800px',
        margin: '50px auto',
        padding: '30px',
        background: '#fff',
        borderRadius: '16px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
      }}
    >
      <h2 style={{ marginBottom: '20px', color: '#222' }}>🧠 AI Job Description Generator</h2>

      <label style={{ fontWeight: '600', color: '#444' }}>Job Description Input:</label>
      <textarea
        value={jobInput}
        onChange={(e) => setJobInput(e.target.value)}
        rows={5}
        placeholder="Enter a job description, responsibilities, etc..."
        style={{
          width: '100%',
          padding: '12px',
          marginTop: '8px',
          marginBottom: '20px',
          borderRadius: '10px',
          border: '1px solid #ccc',
          fontFamily: 'inherit',
        }}
      />

      <label style={{ fontWeight: '600', color: '#444' }}>Custom Prompt (Optional):</label>
      <input
        type="text"
        value={promptInput}
        onChange={(e) => setPromptInput(e.target.value)}
        placeholder="e.g., Senior React Developer"
        style={{
          width: '100%',
          padding: '12px',
          marginTop: '8px',
          marginBottom: '20px',
          borderRadius: '10px',
          border: '1px solid #ccc',
          fontFamily: 'inherit',
        }}
      />

      <button
        onClick={handleGenerate}
        disabled={loading}
        style={{
          backgroundColor: loading ? '#888' : '#007bff',
          color: '#fff',
          padding: '12px 24px',
          borderRadius: '8px',
          border: 'none',
          fontSize: '16px',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? '⏳ Generating...' : '⚡ Generate with AI'}
      </button>

      {generatedOutput && (
        <div style={{ marginTop: '30px' }}>
          <label style={{ fontWeight: '600', color: '#444' }}>AI Output:</label>
          <textarea
            readOnly
            value={generatedOutput}
            rows={10}
            style={{
              width: '100%',
              padding: '12px',
              marginTop: '10px',
              borderRadius: '10px',
              background: '#f9f9f9',
              border: '1px solid #ccc',
              fontFamily: 'monospace',
              color: '#333',
            }}
          />

          <button
            onClick={handleCopy}
            style={{
              marginTop: '15px',
              backgroundColor: '#28a745',
              color: '#fff',
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              fontSize: '15px',
              cursor: 'pointer',
            }}
          >
            📋 Copy to Description
          </button>
        </div>
      )}
    </div>
  );
};

export default JobDescriptionAI;