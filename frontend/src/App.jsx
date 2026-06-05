  const handleStartQuiz = async () => {
    if (!topic) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('num_questions', numQuestions); 

    try {
      const response = await axios.post('https://quizcrafter-k3r8.onrender.com/generate-questions/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // सुरक्षा चेक: अगर डेटा खाली आया तो क्रैश होने से बचाए
      if (response.data && response.data.length > 0) {
        console.log("Questions requested successfully");
        setQuestions(response.data); 
        setQuizReady(true);
      } else {
        alert("AI આ ટોપિક પર પ્રશ્નો બનાવી શક્યું નથી. કૃપા કરીને બીજો ટોપિક ટ્રાય કરો અથવા પ્રોમ્પટ ચેક કરો.");
      }
      setLoading(false); 
    } catch (error) {
      console.error('Error generating quiz:', error);
      alert("સર્વર તરફથી ભૂલ આવી છે, ફરી પ્રયાસ કરો.");
      setLoading(false);
    }
  };
