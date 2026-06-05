import React, { useState } from 'react';

const QuizPage = ({ questions }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [score, setScore] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  const currentQuestion = questions[currentQuestionIndex];

  const handleAnswerClick = (answer, correct) => {
    if (selectedAnswers[currentQuestionIndex] !== undefined) return;

    setSelectedAnswers({
      ...selectedAnswers,
      [currentQuestionIndex]: answer,
    });

    if (correct) setScore(score + 1);
  };

  const goToNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = () => {
    setSubmitted(true);
  };

  // HTML ફાઇલ ડાઉનલોડ કરવાનું નવું ફીચર
  const downloadHTMLReport = () => {
    let htmlContent = `
      <!DOCTYPE html>
      <html lang="gu">
      <head>
        <meta charset="UTF-8">
        <title>Quiz Test Paper</title>
        <style>
          body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f7f9fa; color: #333; }
          .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
          h1 { text-align: center; color: #4f46e5; border-bottom: 2px solid #e5e7eb; padding-bottom: 15px; }
          .score-box { background: #e0e7ff; padding: 15px; border-radius: 6px; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 30px; color: #3730a3; }
          .question-block { margin-bottom: 30px; padding: 20px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; }
          .question-title { font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #111827; }
          .option { padding: 10px 15px; margin: 8px 0; border-radius: 4px; background: #f3f4f6; border-left: 4px solid #d1d5db; }
          .correct { background: #def7ec; border-left: 4px solid #03543f; color: #03543f; font-weight: bold; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Quiz Test Paper</h1>
          <div class="score-box">તમારો ફાઈનલ સ્કોર: ${score} / ${questions.length}</div>
    `;

    questions.forEach((q, index) => {
      htmlContent += `
        <div class="question-block">
          <div class="question-title">${index + 1}. ${q.question}</div>
      `;
      q.answers.forEach((ans) => {
        const isCorrectClass = ans.correct ? 'correct' : '';
        const checkMark = ans.correct ? ' ✓ (સાચો જવાબ)' : '';
        htmlContent += `
          <div class="option ${isCorrectClass}">${ans.text}${checkMark}</div>
        `;
      });
      htmlContent += `</div>`;
    });

    htmlContent += `
        </div>
      </body>
      </html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `Quiz_Test_${Date.now()}.html`;
    link.click();
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      {!submitted ? (
        <>
          <div className="bg-white p-6 rounded shadow-md w-full max-w-xl">
            <div className="text-sm text-gray-500 mb-2">પ્રશ્ન: {currentQuestionIndex + 1} / {questions.length}</div>
            <h2 className="text-2xl font-bold mb-4">{currentQuestion.question}</h2>

            <div className="grid gap-4">
              {currentQuestion.answers.map((answer, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAnswerClick(answer.text, answer.correct)}
                  className={`px-4 py-2 rounded border text-left ${selectedAnswers[currentQuestionIndex] === answer.text
                    ? answer.correct
                      ? 'bg-green-500 text-white'
                      : 'bg-red-500 text-white'
                    : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                  disabled={selectedAnswers[currentQuestionIndex] !== undefined}
                >
                  {answer.text}
                </button>
              ))}
            </div>

            <div className="mt-6 flex justify-between">
              <button
                onClick={goToPreviousQuestion}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500"
                disabled={currentQuestionIndex === 0}
              >
                પાછળ
              </button>

              {currentQuestionIndex < questions.length - 1 ? (
                <button
                  onClick={goToNextQuestion}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-500"
                  disabled={selectedAnswers[currentQuestionIndex] === undefined}
                >
                  આગળ
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-500"
                  disabled={selectedAnswers[currentQuestionIndex] === undefined}
                >
                  સબમિટ કરો
                </button>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white p-6 rounded shadow-md w-full max-w-xl text-center">
          <h2 className="text-2xl font-bold mb-4">ક્વિઝ પૂર્ણ થઈ!</h2>
          <p className="text-xl mb-6">તમારો ફાઈનલ સ્કોર: <span className="font-bold text-indigo-600">{score} / {questions.length}</span></p>
          
          
          <button
            onClick={downloadHTMLReport}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-500 shadow-md transition"
          >
            Download Test File (HTML) 📥
          </button>
        </div>
      )}
    </div>
  );
};

export default QuizPage;
