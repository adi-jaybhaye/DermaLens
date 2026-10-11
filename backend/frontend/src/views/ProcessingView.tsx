import React, { useState, useEffect } from 'react';
import { api, type AssessmentResults } from '../api/client';
import { SparklesIcon, CheckCircleIcon, AlertCircleIcon, RefreshIcon } from '../components/Icons';

interface ProcessingViewProps {
  viewFiles: Record<'front' | 'left' | 'right', File>;
  captureModes?: Record<'front' | 'left' | 'right', 'camera' | 'upload'>;
  onSuccess: (results: AssessmentResults) => void;
  onError: (message: string) => void;
}

export const ProcessingView: React.FC<ProcessingViewProps> = ({ viewFiles, captureModes, onSuccess, onError }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const steps = [
    'Checking Photo Clarity, Lighting & Resolution',
    'Detecting Facial Contours & Alignment Landmarks',
    'Mapping 5 Facial Zones (Forehead, Cheeks, Nose, Chin)',
    'Analyzing Skin Surface Patterns & Textures',
    'Generating Visual Focus Heatmaps',
    'Synthesizing Dermatological Insights & Evidence',
  ];

  useEffect(() => {
    let isCancelled = false;

    const runPipeline = async () => {
      try {
        // Step 0: Create assessment
        setCurrentStepIndex(0);
        const viewsToSubmit = Object.keys(viewFiles) as Array<'front' | 'left' | 'right'>;
        const modes = captureModes || { front: 'upload' };
        const modeValues = Object.values(modes);
        const allCamera = modeValues.length > 0 && modeValues.every((m) => m === 'camera');
        const allUpload = modeValues.length > 0 && modeValues.every((m) => m === 'upload');
        const overallType = allCamera ? 'camera' : allUpload ? 'upload' : 'hybrid';

        const assessment = await api.createAssessment(overallType, viewsToSubmit, modes);
        const assessmentId = assessment.assessment_id;

        // Step 1 & 2: Upload each view (triggers quality check + face detection + initial inference)
        setCurrentStepIndex(1);
        for (const view of viewsToSubmit) {
          const file = viewFiles[view];
          if (file) {
            await api.uploadViewImage(assessmentId, view, file);
          }
        }

        // Step 3 & 4: Trigger deep analysis & Grad-CAM
        setCurrentStepIndex(3);
        await api.triggerAnalysis(assessmentId);

        // Step 5: Fetch enriched results
        setCurrentStepIndex(5);
        const results = await api.getResults(assessmentId);

        if (!isCancelled) {
          onSuccess(results);
        }
      } catch (err: any) {
        if (!isCancelled) {
          setErrorMessage(err.message || 'Pipeline processing failed.');
        }
      }
    };

    runPipeline();

    return () => {
      isCancelled = true;
    };
  }, []);

  return (
    <div style={{ maxWidth: 640, margin: '60px auto', padding: '0 20px' }}>
      <div className="glass-panel" style={{ padding: '44px 36px', backgroundColor: '#FFFFFF', textAlign: 'center' }}>
        {errorMessage ? (
          <div>
            <div style={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              backgroundColor: 'var(--color-danger-bg)',
              color: 'var(--color-danger-text)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 18px',
            }}>
              <AlertCircleIcon size={28} />
            </div>

            <h3 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
              Photo Verification Notice
            </h3>

            <p style={{
              fontSize: 14,
              color: 'var(--color-mocha)',
              backgroundColor: 'var(--color-danger-bg)',
              border: '1px solid var(--color-danger-border)',
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              marginBottom: 24,
              textAlign: 'left',
              wordBreak: 'break-word',
            }}>
              {errorMessage}
            </p>

            <button
              onClick={() => onError(errorMessage)}
              className="btn-primary"
              style={{ padding: '12px 28px' }}
            >
              <RefreshIcon size={16} /> Return to Capture &amp; Recapture
            </button>
          </div>
        ) : (
          <div>
            {/* Spinning decorative ring */}
            <div style={{
              width: 68,
              height: 68,
              borderRadius: '50%',
              border: '3px solid var(--color-border)',
              borderTopColor: 'var(--color-terracotta)',
              margin: '0 auto 24px',
              animation: 'spin 1.2s linear infinite',
            }} />

            <h3 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
              Analyzing Facial Skin Features
            </h3>
            <p style={{ fontSize: 14, color: 'var(--color-muted)', marginBottom: 32 }}>
              Performing comprehensive facial skin assessment...
            </p>

            {/* Stepper progress list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, textAlign: 'left' }}>
              {steps.map((step, idx) => {
                const isCompleted = idx < currentStepIndex;
                const isCurrent = idx === currentStepIndex;

                return (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      padding: '10px 14px',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: isCurrent ? 'var(--color-blush-light)' : 'transparent',
                      border: isCurrent ? '1px solid var(--color-blush-border)' : '1px solid transparent',
                    }}
                  >
                    <div style={{
                      color: isCompleted ? 'var(--color-sage)' : isCurrent ? 'var(--color-terracotta)' : 'var(--color-subtle)',
                      flexShrink: 0,
                    }}>
                      {isCompleted ? (
                        <CheckCircleIcon size={18} />
                      ) : isCurrent ? (
                        <SparklesIcon size={18} className="animate-spin" />
                      ) : (
                        <div style={{ width: 18, height: 18, borderRadius: '50%', border: '2px solid var(--color-sand-dark)' }} />
                      )}
                    </div>
                    <span style={{
                      fontSize: 13.5,
                      fontWeight: isCurrent ? 600 : 500,
                      color: isCurrent ? 'var(--color-charcoal)' : isCompleted ? 'var(--color-mocha)' : 'var(--color-subtle)',
                    }}>
                      {step}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
