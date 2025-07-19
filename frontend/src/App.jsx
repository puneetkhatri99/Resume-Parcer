import JobDescriptionAI from './JobDescriptionAI.jsx';
import ResumeUploader from './ResumeUploader.jsx';

function App() {


  return (
    <div>
       <ResumeUploader />
       <div className="min-h-screen bg-gray-100">
      <JobDescriptionAI />
       </div>
    </div>
   
  )
}

export default App
