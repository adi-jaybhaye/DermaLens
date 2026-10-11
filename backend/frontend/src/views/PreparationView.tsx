import React from 'react';
import { CameraIcon, CheckCircleIcon, SparklesIcon, ShieldCheckIcon } from '../components/Icons';

interface PreparationViewProps {
  onProceed: () => void;
  onBack: () => void;
}

export const PreparationView: React.FC<PreparationViewProps> = ({ onProceed, onBack }) => {
  const steps = [
    {
      title: 'Even Natural Lighting',
      desc: 'Position yourself facing a window or soft ambient light. Avoid strong backlights or harsh shadows.',
    },
    {
      title: 'Clean Surface & Neutral Expression',
      desc: 'Remove heavy cosmetic makeup and glasses for optimal pore, redness, and texture evaluation.',
    },
    {
      title: 'Frontal Distance & Alignment',
      desc: 'Keep your face approximately 40-50 cm from the lens with eyes level and face centered.',
    },
    {
      title: '3-Perspective Multi-View Protocol',
      desc: 'Capture 3 distinct angles: Frontal direct gaze, Left profile (45°), and Right profile (45°).',
    },
  ];

  return (
    <div style={{ maxWidth: 780, margin: '0 auto', padding: '40px 20px 80px' }}>
      <div className="glass-panel" style={{ padding: '40px 36px', backgroundColor: '#FFFFFF' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div className="pill-badge pill-terracotta" style={{ marginBottom: 12 }}>
            <SparklesIcon size={14} />
            Preparation Protocol
          </div>
          <h2 style={{ fontSize: 30, fontWeight: 700, marginBottom: 8 }}>
            Optimising Your Capture Quality
          </h2>
          <p style={{ fontSize: 15, color: 'var(--color-muted)', maxWidth: 520, margin: '0 auto' }}>
            Our automated photo check validates resolution, lighting, and clarity before starting assessment. Follow these recommendations for best results.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16, marginBottom: 36 }}>
          {steps.map((step, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 14,
                padding: '18px 20px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1px solid var(--color-border-light)',
              }}
            >
              <div style={{ color: 'var(--color-sage)', flexShrink: 0, marginTop: 2 }}>
                <CheckCircleIcon size={20} />
              </div>
              <div>
                <h5 style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>{step.title}</h5>
                <p style={{ fontSize: 13, color: 'var(--color-muted)', lineHeight: 1.5 }}>{step.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Photo Clarity Notice */}
        <div style={{
          padding: '16px 20px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--color-warning-bg)',
          border: '1px solid var(--color-warning-border)',
          display: 'flex',
          alignItems: 'center',
          gap: 14,
          marginBottom: 36,
        }}>
          <div style={{ color: 'var(--color-warning-text)', flexShrink: 0 }}>
            <ShieldCheckIcon size={22} />
          </div>
          <div style={{ fontSize: 13, color: 'var(--color-warning-text)', lineHeight: 1.5 }}>
            <strong>Clarity Check Active:</strong> Photos with insufficient lighting, severe blur, or low resolution will prompt a recapture request to ensure your assessment is reliable and accurate.
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 14,
        }}>
          <button onClick={onBack} className="btn-ghost" style={{ padding: '10px 18px' }}>
            Back
          </button>

          <button
            onClick={onProceed}
            className="btn-primary"
            style={{ padding: '13px 26px', flex: 1, minWidth: 220, justifyContent: 'center' }}
          >
            <CameraIcon size={18} />
            Continue to Multi-View Capture
          </button>
        </div>
      </div>
    </div>
  );
};
