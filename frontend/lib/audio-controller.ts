const voicePreferences = ['natural', 'neural', 'online', 'aria', 'jenny', 'guy', 'libby', 'sonia', 'google us english', 'google uk english'];

export const backendOrigin = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api').replace(/\/api\/?$/, '');
export const absoluteAudioUrl = (url?: string | null) => !url ? undefined : url.startsWith('http') ? url : `${backendOrigin}${url}`;

export const getBestEnglishVoice = () => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  const englishVoices = voices.filter((voice) => voice.lang.toLowerCase().startsWith('en'));
  for (const preference of voicePreferences) {
    const match = englishVoices.find((voice) => voice.name.toLowerCase().includes(preference));
    if (match) return match;
  }
  return englishVoices[0] ?? voices[0] ?? null;
};

export const stopAllAudio = () => {
  if (typeof window === 'undefined') return;
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  document.querySelectorAll('audio').forEach((audio) => {
    audio.pause();
    audio.currentTime = 0;
  });
};

export const speak = (text: string, onEnd?: () => void) => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text.trim()) return;
  stopAllAudio();
  const sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g)?.map((sentence) => sentence.trim()).filter(Boolean) ?? [text];
  let index = 0;
  const speakNext = () => {
    if (index >= sentences.length) { onEnd?.(); return; }
    const utterance = new SpeechSynthesisUtterance(sentences[index++]);
    const voice = getBestEnglishVoice();
    if (voice) utterance.voice = voice;
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.onend = speakNext;
    utterance.onerror = () => onEnd?.();
    window.speechSynthesis.speak(utterance);
  };
  speakNext();
};
