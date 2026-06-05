
import { useState } from 'react';
import axios from 'axios';
import QuizPage from './QuizPage';
import { ClipLoader } from 'react-spinners';

const App = () => {
  const [file, setFile] = useState(null);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [topic, setTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(5); // <-- 1. यहाँ नए नंबर का स्टेट जोड़ा (डिफ़ॉल्ट 5)
  const [quizReady, setQuizReady] = useState(false);
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('https://quizcrafter-k3r8.onrender.com/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log(response.data);
      setFileUploaded(true);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleStartQuiz = async () => {
    if (!topic) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('num_questions', numQuestions); // <-- 2. यहाँ बैकएंड को नंबर भेजना शुरू किया

    try {
      const response = await axios.post('https://quizcrafter-k3r8.onrender.com/generate-questions/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log("Questions requested successfully");
      setQuestions(response.data); 
      setLoading(false); 
      setQuizReady(true);
    } catch (error) {
      console.error('Error generating quiz:', error);
      setLoading(false);
    }
  };


  return (
    <div>
      {questions ? (
        <QuizPage questions={questions} />
      ) : (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
          {loading ? (
            <div className="flex items-center justify-center min-h-screen">
              <ClipLoader color="#4A90E2" size={50} />  
            </div>
          ) : (
            <div className="bg-white p-6 rounded shadow-md w-full max-w-md">
              <h1 className="text-2xl font-bold mb-4">Upload PDF to Start Quiz</h1>
              <input
                type="file"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <button
                onClick={handleUpload}
                className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-500 w-full"
              >
                Upload
              </button>

              {fileUploaded && (
                <>
                  <div className="mt-4">
                    <label htmlFor="topic" className="block text-sm font-medium text-gray-700">Select Topic</label>
                    <input
                      type="text"
                      id="topic"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Enter quiz topic..."
                    />
                  </div>

                  {/* 3. यहाँ स्क्रीन पर नंबर ऑफ क्वेश्चंस सिलेक्ट करने का नया बॉक्स जोड़ा */}
                  <div className="mt-4">
                    <label htmlFor="numQuestions" className="block text-sm font-medium text-gray-700">Number of Questions</label>
                    <select
                      id="numQuestions"
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(Number(e.target.value))}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    >
                      <option value={5}>5 Questions</option>
                      <option value={10}>10 Questions</option>
                      <option value={15}>15 Questions</option>
                      <option value={20}>20 Questions</option>
                    </select>
                  </div>

                  <button
                    onClick={handleStartQuiz}
                    className="mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-500 w-full"
                  >
                    Start Quiz
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default App;
