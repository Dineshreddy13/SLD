export const playTTS = async (text) => {
  if (!text || !text.trim()) return;

  try {
    const response = await fetch('http://127.0.0.1:8000/api/tts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text.trim() }),
    });

    if (!response.ok) {
      throw new Error(`TTS failed with status: ${response.status}`);
    }

    const blob = await response.blob();
    const audioUrl = URL.createObjectURL(blob);
    
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);
      
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        resolve();
      };
      
      audio.onerror = (err) => {
        URL.revokeObjectURL(audioUrl);
        reject(err);
      };

      audio.play().catch(reject);
    });

  } catch (error) {
    console.error('Error playing TTS:', error);
    throw error;
  }
};
