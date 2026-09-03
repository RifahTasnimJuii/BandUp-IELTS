'use client';

import * as React from 'react';
import { Pause, Play, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { speak, stopAllAudio } from '@/lib/audio-controller';

interface AudioPlayerProps {
  src?: string;
  transcript?: string;
  title?: string;
  strictExamMode?: boolean;
  allowReplay?: boolean;
  allowSeek?: boolean;
  isLocked?: boolean;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  src,
  transcript,
  title,
  strictExamMode = false,
  allowReplay = true,
  allowSeek = true,
  isLocked = false,
}) => {
  const audioRef = React.useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [currentTime, setCurrentTime] = React.useState(0);
  const [duration, setDuration] = React.useState(0);
  const [hasEnded, setHasEnded] = React.useState(false);
  const [audioFailed, setAudioFailed] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const playbackLocked = strictExamMode && !allowReplay && hasEnded;
  const usesSpeech = (!src || audioFailed) && Boolean(transcript) && typeof window !== 'undefined' && 'speechSynthesis' in window;

  React.useEffect(() => {
    const el = audioRef.current;
    if (!el) return;

    const handleTimeUpdate = () => setCurrentTime(el.currentTime);
    const handleLoadedMetadata = () => setDuration(el.duration || 0);
    const handleEnded = () => {
      setIsPlaying(false);
      setHasEnded(true);
    };
    const handleError = () => { setAudioFailed(true); setErrorMessage(`Audio failed: ${src || 'no source'}`); };

    el.addEventListener('timeupdate', handleTimeUpdate);
    el.addEventListener('loadedmetadata', handleLoadedMetadata);
    el.addEventListener('ended', handleEnded);
    el.addEventListener('error', handleError);

    return () => {
      el.removeEventListener('timeupdate', handleTimeUpdate);
      el.removeEventListener('loadedmetadata', handleLoadedMetadata);
      el.removeEventListener('ended', handleEnded);
      el.removeEventListener('error', handleError);
    };
  }, [src]);

  React.useEffect(() => {
    if (isLocked) stopAllAudio();
    return () => stopAllAudio();
  }, [isLocked]);

  const togglePlayback = async () => {
    if (isLocked || playbackLocked) return;

    if (usesSpeech) {
      if (isPlaying) {
        window.speechSynthesis.pause();
        setIsPlaying(false);
      } else {
        speak(transcript, () => { setIsPlaying(false); setHasEnded(true); });
        setIsPlaying(true);
      }
      return;
    }
    if (!audioRef.current || !src) return;

    if (audioRef.current.paused) {
      await audioRef.current.play();
      setIsPlaying(true);
    } else {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleSeek = (value: number) => {
    if (!audioRef.current || !allowSeek || isLocked) return;
    audioRef.current.currentTime = value;
    setCurrentTime(value);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Audio</p>
          {title ? <h2 className="mt-1 text-lg font-semibold text-slate-900">{title}</h2> : null}
        </div>
        <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">
          <Volume2 size={14} />
          {isPlaying ? 'Playing' : 'Ready'}
        </div>
      </div>

      <audio ref={audioRef} src={src} preload="metadata" className="hidden" />

      <div className="flex items-center gap-3">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={togglePlayback}
          disabled={isLocked || playbackLocked || (!src && !usesSpeech)}
          className="shrink-0"
        >
          {isPlaying ? <Pause size={16} className="mr-2" /> : <Play size={16} className="mr-2" />}
          {isPlaying ? 'Pause' : 'Play'}
        </Button>

        {allowReplay || !strictExamMode ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={isLocked || playbackLocked || (!src && !usesSpeech)}
            onClick={() => {
              if (usesSpeech) { window.speechSynthesis.cancel(); setIsPlaying(false); setHasEnded(false); return; }
              if (!audioRef.current || !src) return;
              audioRef.current.currentTime = 0;
              setCurrentTime(0);
              setHasEnded(false);
            }}
          >
            Replay
          </Button>
        ) : null}
      </div>

      <div className="mt-4 space-y-2">
        <input
          type="range"
          min={0}
          max={duration || 0}
          step={0.1}
          value={currentTime}
          onChange={(event) => handleSeek(Number(event.target.value))}
          disabled={isLocked || !allowSeek}
          aria-label="Audio playback position"
          className="h-2 w-full cursor-pointer accent-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
        />

        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>{formatTime(currentTime)}</span>
          <div className="flex items-center gap-2">
            <span>{Math.round(progress)}%</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      </div>

      {strictExamMode && !allowReplay && hasEnded ? (
        <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Replay is disabled in strict exam mode after the audio ends.
        </div>
      ) : null}

      {isLocked ? (
        <div className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700">
          Time&apos;s up - Audio locked
        </div>
      ) : null}
      {errorMessage ? <div className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{errorMessage}</div> : null}
    </div>
  );
};

const formatTime = (seconds: number) => {
  if (!Number.isFinite(seconds) || seconds <= 0) return '00:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export default AudioPlayer;
