import {useEffect, useRef, useState} from 'react';

const snap = (v: number, step: number) => Math.round(v / step) * step;
const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

type SliderProps = {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  detents: number[];
  orientation: 'vertical' | 'horizontal';
  disabled?: boolean;
  onChange: (value: number) => void;
};

// Touch slider with detents. Drag or tap anywhere on the track. Values snap to
// the step. Arrow keys move one step. The track is at least 56 px across so it
// can be hit reliably while the vessel is moving.
export function Slider({label, value, min, max, step, detents, orientation, disabled, onChange}: SliderProps) {
  const ref = useRef<HTMLDivElement>(null);
  const vertical = orientation === 'vertical';

  const setFromPointer = (clientX: number, clientY: number) => {
    const rect = ref.current!.getBoundingClientRect();
    const fraction = vertical ? 1 - (clientY - rect.top) / rect.height : (clientX - rect.left) / rect.width;
    onChange(clamp(snap(min + clamp(fraction, 0, 1) * (max - min), step), min, max));
  };

  const fraction = (value - min) / (max - min);
  const cssPos = `${fraction * 100}%`;

  return (
    <div
      ref={ref}
      className={`slider ${vertical ? 'v' : 'h'} ${disabled ? 'off' : ''}`}
      role="slider"
      aria-label={label}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={value}
      aria-disabled={disabled}
      tabIndex={disabled ? -1 : 0}
      onPointerDown={(e) => {
        if (disabled) return;
        e.currentTarget.setPointerCapture(e.pointerId);
        setFromPointer(e.clientX, e.clientY);
      }}
      onPointerMove={(e) => {
        if (disabled || !e.currentTarget.hasPointerCapture(e.pointerId)) return;
        setFromPointer(e.clientX, e.clientY);
      }}
      onKeyDown={(e) => {
        if (disabled) return;
        const up = vertical ? 'ArrowUp' : 'ArrowRight';
        const down = vertical ? 'ArrowDown' : 'ArrowLeft';
        if (e.key === up) onChange(clamp(value + step, min, max));
        if (e.key === down) onChange(clamp(value - step, min, max));
      }}
    >
      <div className="slider-track" />
      {detents.map((d) => {
        const p = `${((d - min) / (max - min)) * 100}%`;
        return <span key={d} className="detent" style={vertical ? {bottom: p} : {left: p}} />;
      })}
      <div className="slider-fill" style={vertical ? {height: cssPos} : {width: cssPos}} />
      <div className="slider-knob" style={vertical ? {bottom: `calc(${cssPos} - 24px)`} : {left: `calc(${cssPos} - 24px)`}} />
    </div>
  );
}

type HoldProps = {
  label: string;
  holdMs?: number;
  disabled?: boolean;
  tone?: 'normal' | 'danger';
  onHold: () => void;
};

// Press and hold to act. A tap does nothing. Used for any change that moves the
// vessel, stops it, or changes who is in control. Keyboard users press and hold
// Enter or Space.
export function HoldButton({label, holdMs = 1500, disabled, tone = 'normal', onHold}: HoldProps) {
  const [progress, setProgress] = useState(0);
  const timer = useRef<number | null>(null);
  const startedAt = useRef(0);
  const holdRef = useRef(onHold);
  holdRef.current = onHold;

  const stop = () => {
    if (timer.current !== null) {
      window.clearInterval(timer.current);
      timer.current = null;
    }
    setProgress(0);
  };

  const start = () => {
    if (disabled || timer.current !== null) return;
    startedAt.current = Date.now();
    timer.current = window.setInterval(() => {
      const f = Math.min(1, (Date.now() - startedAt.current) / holdMs);
      setProgress(f);
      if (f >= 1) {
        stop();
        holdRef.current();
      }
    }, 30);
  };

  useEffect(() => () => {
    if (timer.current !== null) window.clearInterval(timer.current);
  }, []);

  return (
    <button
      type="button"
      className={`hold ${tone} ${disabled ? 'off' : ''}`}
      disabled={disabled}
      aria-label={`${label}. Press and hold for ${holdMs / 1000} seconds.`}
      onPointerDown={start}
      onPointerUp={stop}
      onPointerLeave={stop}
      onPointerCancel={stop}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          start();
        }
      }}
      onKeyUp={(e) => {
        if (e.key === 'Enter' || e.key === ' ') stop();
      }}
    >
      <span className="hold-fill" style={{transform: `scaleX(${progress})`}} />
      <span className="hold-text">{label}</span>
      <small>Hold {holdMs / 1000} s</small>
    </button>
  );
}
