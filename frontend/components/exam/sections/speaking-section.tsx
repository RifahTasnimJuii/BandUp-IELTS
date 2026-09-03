'use client';

import * as React from 'react';
import { Mic, MicOff, Square, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/useAuthStore';
import { saveSpeakingConsent, uploadSpeakingAudio } from '@/lib/api/exam';
import { useExamStore } from '@/store/useExamStore';
import { speak, stopAllAudio } from '@/lib/audio-controller';

interface SpeakingPrompt {
  id: string;
  questionId?: string;
  part: string;
  prompt: string;
  promptAudioFile?: string;
  durationSeconds?: number;
  preparationSeconds?: number;
}

interface SpeakingSectionProps {
  prompts?: SpeakingPrompt[];
  examinerAudioAssets?: Array<{ title: string; audio_url: string | null }>;
  attemptId?: string;
  isLocked?: boolean;
}

const defaultPrompts: SpeakingPrompt[] = [
  {
    id: 'part-1',
    part: 'Part 1',
    prompt: 'Describe your hometown or the place where you live.',
    durationSeconds: 45,
  },
  {
    id: 'part-2',
    part: 'Part 2',
    prompt: 'Describe a person who has influenced your life.',
    preparationSeconds: 60,
    durationSeconds: 120,
  },
  {
    id: 'part-3',
    part: 'Part 3',
    prompt: 'Do you think it is better to have many friends or a few close friends? Why?',
    durationSeconds: 60,
  },
];

const formatTimer = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${remainder.toString().padStart(2, '0')}`;
};

const useAudioRecorder = (options?: { onStop?: (blob: Blob, file: File) => void | Promise<void> }) => {
  const [isRecording, setIsRecording] = React.useState(false);
  const [permissionError, setPermissionError] = React.useState<string | null>(null);
  const [isSupported, setIsSupported] = React.useState(true);
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const chunksRef = React.useRef<Blob[]>([]);

  React.useEffect(() => {
    if (typeof window === 'undefined' || !('MediaRecorder' in window)) {
      setIsSupported(false);
    }
  }, []);

  const startRecording = React.useCallback(async () => {
    if (typeof window === 'undefined') return;

    if (!('MediaRecorder' in window)) {
      setIsSupported(false);
      return;
    }

    try {
      stopAllAudio();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const file = new File([blob], 'speaking-response.webm', { type: 'audio/webm' });
        stream.getTracks().forEach((track) => track.stop());
        options?.onStop?.(blob, file);
      };

      recorder.start();
      setPermissionError(null);
      setIsRecording(true);
    } catch (error) {
      setPermissionError('Microphone permission was denied. Please allow access to record your speaking answer.');
      console.error('Recording failed', error);
    }
  }, [options]);

  const stopRecording = React.useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  return {
    isRecording,
    permissionError,
    isSupported,
    startRecording,
    stopRecording,
  };
};

export const SpeakingSection: React.FC<SpeakingSectionProps> = ({
  prompts = defaultPrompts,
  examinerAudioAssets = [],
  attemptId,
  isLocked = false,
}) => {
  const user = useAuthStore((state) => state.user);
  const [consentOpen, setConsentOpen] = React.useState(false);
  const [currentPromptIndex, setCurrentPromptIndex] = React.useState(0);
  const [preparationRemaining, setPreparationRemaining] = React.useState<number>(0);
  const [recordingRemaining, setRecordingRemaining] = React.useState<number>(0);
  const [status, setStatus] = React.useState<'idle' | 'preparing' | 'recording' | 'completed'>('idle');
  const [uploading, setUploading] = React.useState(false);
  const [uploadError, setUploadError] = React.useState<string | null>(null);
  const [examinerSpeaking, setExaminerSpeaking] = React.useState(false);
  const promptAudioRef = React.useRef<HTMLAudioElement | null>(null);
  const greetingAudioRef = React.useRef<HTMLAudioElement | null>(null);
  const setAnswer = useExamStore((state) => state.setAnswer);
  const setUser = useAuthStore((state) => state.setUser);
  const activePrompt = prompts[currentPromptIndex] ?? prompts[0] ?? defaultPrompts[0];
  const questionId = activePrompt.questionId ?? activePrompt.id;

  const handleUpload = React.useCallback(async (file: File) => {
    if (!attemptId) return;

    try {
      setUploading(true);
      setUploadError(null);
      await uploadSpeakingAudio(attemptId, questionId, file);
      setAnswer(questionId, { answer_text: file.name });
      setStatus('completed');
      if (currentPromptIndex < prompts.length - 1) window.setTimeout(() => setCurrentPromptIndex((index) => index + 1), 1000);
    } catch (error) {
      console.error('Speaking upload failed', error);
      setUploadError('Audio upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  }, [attemptId, currentPromptIndex, prompts.length, questionId, setAnswer]);

  const { isRecording, permissionError, isSupported, startRecording, stopRecording } = useAudioRecorder({
    onStop: async (_, file) => {
      await handleUpload(file);
    },
  });

  React.useEffect(() => {
    const currentPrompt = prompts[currentPromptIndex] ?? prompts[0];
    const initialPreparation = currentPrompt?.preparationSeconds ?? 0;
    const initialRecording = currentPrompt?.durationSeconds ?? 0;
    setPreparationRemaining(initialPreparation);
    setRecordingRemaining(initialRecording);
    setStatus('idle');
  }, [currentPromptIndex, prompts]);

  React.useEffect(() => {
    if (status !== 'preparing' || preparationRemaining <= 0) return;

    const timer = window.setTimeout(() => {
      setPreparationRemaining((prev) => {
        const nextValue = Math.max(prev - 1, 0);
        if (nextValue === 0) {
          setStatus('recording');
        }
        return nextValue;
      });
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [preparationRemaining, status]);

  React.useEffect(() => {
    if (status !== 'recording' || recordingRemaining <= 0) return;

    const timer = window.setTimeout(() => {
      setRecordingRemaining((prev) => {
        const nextValue = Math.max(prev - 1, 0);
        if (nextValue === 0) {
          stopRecording();
          setStatus('completed');
        }
        return nextValue;
      });
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [recordingRemaining, status, stopRecording]);

  const beginSpeakingFlow = async (consentGranted = false) => {
    if (isLocked || !attemptId || uploading) return;

    const hasConsent = Boolean(user && (user as { speaking_audio_consent?: boolean }).speaking_audio_consent);
    if (!hasConsent && !consentGranted) {
      setConsentOpen(true);
      return;
    }

    const current = prompts[currentPromptIndex] ?? prompts[0] ?? defaultPrompts[0];
    stopAllAudio();
    if (current.preparationSeconds && current.preparationSeconds > 0) {
      setStatus('preparing');
      setPreparationRemaining(current.preparationSeconds);
      setRecordingRemaining(current.durationSeconds ?? 0);
      return;
    }

    setStatus('recording');
    setRecordingRemaining(current.durationSeconds ?? 0);
    await startRecording();
  };

  const onConsentApprove = async () => {
    try {
      await saveSpeakingConsent();
      setUser(user ? { ...user, speaking_audio_consent: true } : user);
      setConsentOpen(false);
      await beginSpeakingFlow(true);
    } catch (error) {
      console.error('Speaking consent failed', error);
      setUploadError('Unable to save microphone consent. Please try again.');
    }
  };

  React.useEffect(() => {
    stopAllAudio();
    const greeting = currentPromptIndex === 0 ? examinerAudioAssets.find((asset) => asset.title === 'speaking_greeting')?.audio_url : null;
    if (greeting && greetingAudioRef.current) {
      setExaminerSpeaking(true);
      greetingAudioRef.current.currentTime = 0;
      void greetingAudioRef.current.play().catch(() => setExaminerSpeaking(false));
    } else if (activePrompt.promptAudioFile && promptAudioRef.current) {
      promptAudioRef.current.currentTime = 0;
      setExaminerSpeaking(true);
      void promptAudioRef.current.play().catch(() => setExaminerSpeaking(false));
    } else {
      setExaminerSpeaking(true);
      speak(activePrompt.prompt, () => setExaminerSpeaking(false));
    }
    return () => stopAllAudio();
  }, [activePrompt.prompt, activePrompt.promptAudioFile, currentPromptIndex, examinerAudioAssets]);

  React.useEffect(() => {
    return () => stopAllAudio();
  }, []);

  React.useEffect(() => {
    if (status === 'recording' && !isRecording) {
      void startRecording();
    }
  }, [status, isRecording, startRecording]);

  React.useEffect(() => {
    if (status === 'preparing' && preparationRemaining === 0 && !isRecording) {
      setStatus('recording');
      setRecordingRemaining(activePrompt.durationSeconds ?? 0);
      void startRecording();
    }
  }, [status, preparationRemaining, isRecording, startRecording, activePrompt.durationSeconds]);

  const timerLabel = status === 'preparing' ? 'Preparation Time' : 'Recording Time';
  const timerValue = status === 'preparing' ? preparationRemaining : recordingRemaining;
  const promptCount = prompts.length;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Speaking</p>
            <h3 className="mt-1 text-xl font-semibold text-slate-900">{activePrompt.part}</h3>
          </div>
          <div className="rounded-full bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700">
            {timerLabel}: {formatTimer(timerValue)}
          </div>
        </div>

        <p className="text-base leading-7 text-slate-700">{activePrompt.prompt}</p>
        {activePrompt.promptAudioFile ? <><audio ref={greetingAudioRef} src={examinerAudioAssets.find((asset) => asset.title === 'speaking_greeting')?.audio_url ?? undefined} onEnded={() => { setExaminerSpeaking(false); if (promptAudioRef.current) { promptAudioRef.current.currentTime = 0; void promptAudioRef.current.play(); } }} preload="auto" className="hidden" /><audio ref={promptAudioRef} src={activePrompt.promptAudioFile} onEnded={() => setExaminerSpeaking(false)} preload="auto" className="hidden" /><Button type="button" variant="ghost" onClick={() => { if (promptAudioRef.current) { promptAudioRef.current.currentTime = 0; setExaminerSpeaking(true); void promptAudioRef.current.play(); } }} disabled={isLocked}><Volume2 size={16} className="mr-2" /> Replay question</Button></> : <Button type="button" variant="ghost" onClick={() => { setExaminerSpeaking(true); speak(activePrompt.prompt, () => setExaminerSpeaking(false)); }} disabled={isLocked}><Volume2 size={16} className="mr-2" /> Replay question</Button>}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {examinerSpeaking ? <span className="text-sm font-medium text-sky-700">Examiner is speaking...</span> : null}
        <Button
          type="button"
          variant="outline"
          onClick={() => setCurrentPromptIndex((prev) => (prev + 1) % promptCount)}
          disabled={promptCount <= 1 || isLocked || isRecording || status !== 'completed'}
        >
            Next Part
        </Button>
        <Button
          type="button"
          onClick={() => void beginSpeakingFlow()}
          disabled={isLocked || uploading || isRecording}
          className="gap-2"
        >
          {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
          {isRecording ? 'Recording...' : 'Start Recording'}
        </Button>

        {isRecording ? <span className="inline-flex items-center gap-2 text-sm font-medium text-red-700"><span className="h-2.5 w-2.5 animate-pulse rounded-full bg-red-600" /> Recording {formatTimer((activePrompt.durationSeconds ?? 0) - recordingRemaining)} / {formatTimer(activePrompt.durationSeconds ?? 0)}</span> : null}
        <Button
          type="button"
          variant="outline"
          onClick={() => {
            stopRecording();
            setStatus('idle');
          }}
          disabled={!isRecording || isLocked}
          className="gap-2"
        >
          <Square size={16} />
          Stop
        </Button>
      </div>

      {permissionError ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{permissionError}</div>
      ) : null}

      {!isSupported ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Your browser does not support audio recording.
        </div>
      ) : null}

      {uploadError ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{uploadError}</div>
      ) : null}

      {uploading ? (
        <div className="rounded-xl border border-sky-200 bg-sky-50 px-3 py-2 text-sm text-sky-700">
          Uploading recording...
        </div>
      ) : null}

      {status === 'completed' && !uploading ? (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
          Recorded ✓
        </div>
      ) : null}

      {isLocked ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700">
          Time&apos;s up - Answers locked
        </div>
      ) : null}

      {consentOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
          <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-xl">
            <h4 className="text-xl font-semibold text-slate-900">Microphone consent required</h4>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              This speaking task records your audio for IELTS evaluation. By continuing, you confirm that you understand your microphone will be used to record your response.
            </p>
            <div className="mt-5 flex justify-end gap-3">
              <Button type="button" variant="outline" onClick={() => setConsentOpen(false)}>
                Cancel
              </Button>
              <Button type="button" onClick={onConsentApprove}>
                I agree
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SpeakingSection;
export { useAudioRecorder };
