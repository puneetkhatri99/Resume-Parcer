import React, { useState, useRef } from 'react';
import axios from 'axios';

const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2 MB
const ALLOWED_TYPES = [
'application/pdf',
'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
'text/plain',
];

const ResumeUploader = () => {
const [selectedFile, setSelectedFile] = useState(null);
const [uploadStatus, setUploadStatus] = useState('');
const [parsedData, setParsedData] = useState(null);
const [isUploading, setIsUploading] = useState(false);
const fileInputRef = useRef();

const validateFile = (file) => {
if (!ALLOWED_TYPES.includes(file.type)) {
return '❌ Invalid file type. Only PDF, DOCX, and TXT are allowed.';
}
if (file.size > MAX_FILE_SIZE) {
return '❌ File is too large. Max allowed size is 2 MB.';
}
return null;
};

const handleDrop = (e) => {
e.preventDefault();
const file = e.dataTransfer.files[0];
const error = validateFile(file);
if (error) {
setUploadStatus(error);
setSelectedFile(null);
} else {
setSelectedFile(file);
setUploadStatus('');
}
};

const handleFileChange = (e) => {
const file = e.target.files[0];
const error = validateFile(file);
if (error) {
setUploadStatus(error);
setSelectedFile(null);
} else {
setSelectedFile(file);
setUploadStatus('');
}
};

const handleUpload = async () => {
if (!selectedFile) {
setUploadStatus('Please select a valid file.');
return;
}

setIsUploading(true);
setUploadStatus('⏳ Uploading and parsing resume...');

const formData = new FormData();
formData.append('resume', selectedFile);

try {
const response = await axios.post('http://127.0.0.1:5050/upload', formData, {
headers: { 'Content-Type': 'multipart/form-data' },
});

setParsedData(response.data);
setUploadStatus('✅ Upload complete!');
setSelectedFile(null);
fileInputRef.current.value = '';
} catch (err) {
console.error(err);
setUploadStatus('❌ Upload failed.');
} finally {
setIsUploading(false);
}
};

return (
<div
onDrop={handleDrop}
onDragOver={(e) => e.preventDefault()}
style={{
border: '2px dashed #ccc',
borderRadius: '10px',
padding: '30px',
textAlign: 'center',
width: '500px',
margin: '50px auto',
background: '#fafafa',
boxShadow: '0 4px 10px rgba(0, 0, 0, 0.05)',
}}
>
<h2 style={{ marginBottom: '20px', color: '#333' }}>📄 Upload Your Resume</h2>

<input
type="file"
accept=".pdf,.docx,.txt"
ref={fileInputRef}
onChange={handleFileChange}
style={{ marginTop: '10px' }}
/>

<p style={{ marginTop: '15px', fontStyle: 'italic' }}>
{selectedFile
? `📎 Selected: ${selectedFile.name}`
: '📥 Drag and drop or click to upload'}
</p>

{/* Upload Button */}
<button
onClick={handleUpload}
disabled={isUploading}
style={{
marginTop: '20px',
padding: '10px 25px',
backgroundColor: isUploading ? '#999' : '#007bff',
color: '#fff',
border: 'none',
borderRadius: '5px',
fontSize: '16px',
cursor: isUploading ? 'not-allowed' : 'pointer',
}}
>
{isUploading ? '⏳ Uploading...' : '🚀 Upload'}
</button>

{/* Progress bar */}
{isUploading && (
<div style={{ marginTop: '20px' }}>
<div style={{
height: '8px',
width: '100%',
backgroundColor: '#eee',
borderRadius: '5px',
overflow: 'hidden'
}}>
<div className="progress-bar" style={{
height: '8px',
width: '100%',
background: 'linear-gradient(to right, #007bff 30%, #00bfff 70%)',
animation: 'progress-animation 1s infinite linear'
}} />
</div>

{/* Progress animation keyframes */}
<style>
{`
@keyframes progress-animation {
0% { transform: translateX(-100%); }
100% { transform: translateX(100%); }
}
.progress-bar {
transform: translateX(-100%);
animation: progress-animation 1.2s infinite linear;
}
`}
</style>
</div>
)}

{/* Status text */}
<p
style={{
marginTop: '15px',
color: uploadStatus.includes('✅') ? 'green' : uploadStatus.includes('❌') ? 'red' : '#333',
fontWeight: '500',
}}
>
{uploadStatus}
</p>

{/* Parsed data preview */}
{parsedData && (
<div style={{ marginTop: '30px', textAlign: 'left' }}>
<h3 style={{ color: '#444' }}>🧠 Parsed Resume Data:</h3>
<pre
style={{
background: '#f5f5f5',
padding: '15px',
borderRadius: '5px',
maxHeight: '300px',
overflowY: 'auto',
fontSize: '14px',
whiteSpace: 'pre-wrap',
wordBreak: 'break-word',
}}
>
{JSON.stringify(parsedData, null, 2)}
</pre>
</div>
)}
</div>
);
};

export default ResumeUploader;