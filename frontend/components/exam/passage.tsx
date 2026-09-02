'use client';

import * as React from 'react';

interface PassageProps {
  title?: string;
  bodyText?: string;
  sourceNote?: string;
  className?: string;
}

export const Passage: React.FC<PassageProps> = ({
  title,
  bodyText,
  sourceNote,
  className,
}) => {
  const text = bodyText && bodyText.trim().length > 0 ? bodyText : 'No passage content available.';

  return (
    <div className={`rounded-3xl border border-slate-200 bg-white p-5 shadow-sm ${className ?? ''}`}>
      <div className="mb-4 border-b border-slate-200 pb-3">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Reading Passage</p>
        {title ? <h2 className="mt-2 text-xl font-semibold text-slate-900">{title}</h2> : null}
      </div>

      <div className="prose prose-slate max-w-none select-text text-[15px] leading-8 text-slate-700 [text-wrap:pretty]">
        <div className="whitespace-pre-wrap break-words font-[Georgia,Times_New_Roman,serif] tracking-[0.01em]">
          {text}
        </div>
      </div>

      {sourceNote ? (
        <div className="mt-5 border-t border-slate-200 pt-3 text-xs text-slate-500">
          Source: {sourceNote}
        </div>
      ) : null}
    </div>
  );
};

export default Passage;
