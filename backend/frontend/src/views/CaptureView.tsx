import React, { useState, useRef, useEffect } from 'react';
import { CameraIcon, UploadIcon, CheckCircleIcon, AlertCircleIcon, XIcon, RefreshIcon } from '../components/Icons';

interface CaptureViewProps {
  onComplete: (
    viewFiles: Record<'front' | 'left' | 'right', File>,
    captureModes: Record<'front' | 'left' | 'right', 'camera' | 'upload'>
  ) => void;
  onBack: () => void;
}

export const CaptureView: React.FC<CaptureViewProps> = ({ onComplete, onBack }) => {
  const [activeView, setActiveView] = useState<'front' | 'left' | 'right'>('front');
  const [viewFiles, setViewFiles] = useState<Partial<Record<'front' | 'left' | 'right', File>>>({});
  const [viewPreviews, setViewPreviews] = useState<Partial<Record<'front' | 'left' | 'right', string>>>({});
  const [captureModes, setCaptureModes] = useState<Record<'front' | 'left' | 'right', 'camera' | 'upload'>>({
    front: 'upload',
    left: 'upload',
    right: 'upload',
  });
  const [useCamera, setUseCamera] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Setup camera stream when toggled
  useEffect(() => {
    if (useCamera) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [useCamera]);

  const startCamera = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err: any) {
      setCameraError('Camera access unavailable. Please use file upload.');
      setUseCamera(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const handleCaptureFromCamera = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        setCaptureModes((prev) => ({ ...prev, [activeView]: 'camera' }));
        const file = new File([blob], `${activeView}_capture.jpg`, { type: 'image/jpeg' });
        attachFileToView(activeView, file);
      }
    }, 'image/jpeg', 0.95);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCaptureModes((prev) => ({ ...prev, [activeView]: 'upload' }));
      attachFileToView(activeView, file);
    }
  };

  // Rebind stream if video element remounts when active view changes
  useEffect(() => {
    if (useCamera && videoRef.current && streamRef.current) {
      if (videoRef.current.srcObject !== streamRef.current) {
        videoRef.current.srcObject = streamRef.current;
      }
    }
  }, [activeView, useCamera]);

  // Keep ref to previews for unmount cleanup ONLY
  const viewPreviewsRef = useRef<Partial<Record<'front' | 'left' | 'right', string>>>({});
  useEffect(() => {
    viewPreviewsRef.current = viewPreviews;
  }, [viewPreviews]);

  // Clean up any remaining blob URLs ONLY when component unmounts (never during angle switching)
  useEffect(() => {
    return () => {
      Object.values(viewPreviewsRef.current).forEach((url) => {
        if (url && url.startsWith('blob:')) {
          try {
            URL.revokeObjectURL(url);
          } catch (_) {}
        }
      });
    };
  }, []);

  const attachFileToView = (view: 'front' | 'left' | 'right', file: File) => {
    // Revoke previous blob for this view if it was a blob URL
    const oldUrl = viewPreviews[view];
    if (oldUrl && oldUrl.startsWith('blob:')) {
      try {
        URL.revokeObjectURL(oldUrl);
      } catch (_) {}
    }

    setViewFiles((prev) => ({ ...prev, [view]: file }));

    // Read as persistent base64 Data URL so it is permanent and never gets revoked by the browser
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string;
      if (dataUrl) {
        setViewPreviews((prev) => ({ ...prev, [view]: dataUrl }));
      }
    };
    reader.readAsDataURL(file);

    // Auto-advance to next uncaptured view
    if (view === 'front' && !viewFiles.left) {
      setActiveView('left');
      setFeedbackMsg('✓ Front view saved! Now capturing Left profile (45°). You can review Front in the reel below.');
    } else if (view === 'left' && !viewFiles.right) {
      setActiveView('right');
      setFeedbackMsg('✓ Left view saved! Now capturing Right profile (45°). You can review earlier captures below.');
    } else {
      setFeedbackMsg(`✓ ${view.toUpperCase()} angle photo saved successfully!`);
    }

    setTimeout(() => {
      setFeedbackMsg(null);
    }, 5000);
  };

  const handleRemoveView = (view: 'front' | 'left' | 'right') => {
    const oldUrl = viewPreviews[view];
    if (oldUrl && oldUrl.startsWith('blob:')) {
      try {
        URL.revokeObjectURL(oldUrl);
      } catch (_) {}
    }
    setViewFiles((prev) => {
      const next = { ...prev };
      delete next[view];
      return next;
    });
    setViewPreviews((prev) => {
      const next = { ...prev };
      delete next[view];
      return next;
    });
    setActiveView(view);
  };

  const isReadyToProceed = Boolean(viewFiles.front);
  const allCaptured = Boolean(viewFiles.front && viewFiles.left && viewFiles.right);

  // Find next pending view for the "Resume Capture" button
  const nextPendingView = (['front', 'left', 'right'] as const).find((v) => !viewFiles[v]);

  const viewGuidance: Record<'front' | 'left' | 'right', { title: string; instruction: string }> = {
    front: {
      title: 'Frontal View (Direct)',
      instruction: 'Look straight at the camera. Ensure forehead, cheeks, nose, and chin are visible.',
    },
    left: {
      title: 'Left Profile (45° Angle)',
      instruction: 'Rotate your head slightly to your right (~45°) to capture your left cheek and jawline.',
    },
    right: {
      title: 'Right Profile (45° Angle)',
      instruction: 'Rotate your head slightly to your left (~45°) to capture your right cheek and jawline.',
    },
  };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '30px 20px 80px' }}>
      {/* Capture Completion State (Loop 17) */}
      {allCaptured && (
        <div
          className="glass-panel"
          style={{
            marginBottom: 24,
            padding: '20px 24px',
            backgroundColor: 'var(--color-success-bg)',
            border: '1.5px solid var(--color-success-border)',
            borderRadius: 'var(--radius-lg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 16,
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{
              width: 44,
              height: 44,
              borderRadius: '50%',
              backgroundColor: 'var(--color-sage-light)',
              color: 'var(--color-sage-dark)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <CheckCircleIcon size={24} />
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-charcoal)' }}>
                All required views are ready
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 4, fontSize: 13, color: 'var(--color-success-text)', fontWeight: 600 }}>
                <span>Front ✓</span>
                <span>Left Profile ✓</span>
                <span>Right Profile ✓</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onComplete(viewFiles as Record<'front' | 'left' | 'right', File>, captureModes)}
            className="btn-primary"
            style={{
              padding: '11px 24px',
              fontSize: 14,
              fontWeight: 600,
              backgroundColor: 'var(--color-sage)',
              borderColor: 'var(--color-sage)',
              boxShadow: '0 4px 12px rgba(95, 130, 109, 0.25)',
            }}
          >
            Review &amp; Analyze All Views &rarr;
          </button>
        </div>
      )}

      {/* View Selector Tabs with live thumbnails */}
      <div className="capture-tabs-bar">
        {(['front', 'left', 'right'] as const).map((view) => {
          const isUploaded = Boolean(viewFiles[view]);
          const isActive = activeView === view;
          const thumbUrl = viewPreviews[view];

          return (
            <button
              key={view}
              onClick={() => setActiveView(view)}
              className="capture-tab-btn"
              style={{
                backgroundColor: isActive ? 'var(--color-terracotta)' : 'var(--color-surface)',
                color: isActive ? '#FFFFFF' : 'var(--color-charcoal)',
                border: `1.5px solid ${isActive ? 'var(--color-terracotta)' : isUploaded ? 'var(--color-sage)' : 'var(--color-border)'}`,
                boxShadow: isActive ? '0 4px 14px rgba(200, 109, 81, 0.25)' : 'var(--shadow-sm)',
              }}
            >
              {thumbUrl ? (
                <img
                  src={thumbUrl}
                  alt={`${view} thumb`}
                  style={{
                    width: 22,
                    height: 22,
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: '1.5px solid #FFFFFF',
                    flexShrink: 0,
                  }}
                />
              ) : isUploaded ? (
                <CheckCircleIcon size={16} color={isActive ? '#FFFFFF' : 'var(--color-sage)'} />
              ) : (
                <CameraIcon size={16} />
              )}
              <span style={{ textTransform: 'capitalize' }}>{view} View</span>
              {view === 'front' && !thumbUrl && <span className="tab-required" style={{ fontSize: 11, opacity: 0.8 }}>(Req)</span>}
              {thumbUrl && (
                <span style={{
                  fontSize: 10,
                  backgroundColor: isActive ? 'rgba(255,255,255,0.25)' : 'var(--color-sage-light)',
                  color: isActive ? '#FFFFFF' : 'var(--color-sage-dark)',
                  padding: '1px 5px',
                  borderRadius: 8,
                  fontWeight: 700,
                }}>
                  ✓
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Capture Panel */}
      <div className="glass-panel" style={{ padding: '36px 32px', backgroundColor: '#FFFFFF', marginBottom: 28 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h3 style={{ fontSize: 24, fontWeight: 700, marginBottom: 6 }}>
            {viewGuidance[activeView].title}
          </h3>
          <p style={{ fontSize: 14, color: 'var(--color-muted)', maxWidth: 500, margin: '0 auto' }}>
            {viewGuidance[activeView].instruction}
          </p>
        </div>

        {/* Feedback / Auto-advance Toast Notice */}
        {feedbackMsg && (
          <div style={{
            maxWidth: 600,
            margin: '0 auto 18px',
            padding: '10px 18px',
            backgroundColor: 'var(--color-success-bg)',
            border: '1px solid var(--color-success-border)',
            color: 'var(--color-success-text)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 13,
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            animation: 'fadeIn 0.25s ease-out',
          }}>
            <CheckCircleIcon size={18} color="var(--color-success-text)" />
            <span>{feedbackMsg}</span>
          </div>
        )}

        {/* Viewport: Live Camera or Upload Box */}
        <div style={{
          width: '100%',
          maxWidth: 600,
          aspectRatio: '4/3',
          margin: '0 auto 20px',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
          backgroundColor: '#1E1B18',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '2px dashed var(--color-border)',
        }}>
          {viewPreviews[activeView] ? (
            /* Uploaded Preview */
            <div style={{ width: '100%', height: '100%', position: 'relative' }}>
              <img
                src={viewPreviews[activeView]}
                alt={`${activeView} preview`}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              <div style={{
                position: 'absolute',
                top: 14,
                left: 14,
                backgroundColor: 'rgba(35, 32, 29, 0.78)',
                backdropFilter: 'blur(6px)',
                color: '#FFFFFF',
                padding: '6px 12px',
                borderRadius: 'var(--radius-full)',
                fontSize: 12,
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}>
                <CheckCircleIcon size={14} color="var(--color-sage)" />
                <span style={{ textTransform: 'capitalize' }}>{activeView} Captured</span>
              </div>

              <button
                onClick={() => handleRemoveView(activeView)}
                style={{
                  position: 'absolute',
                  top: 14,
                  right: 14,
                  backgroundColor: 'rgba(35, 32, 29, 0.78)',
                  backdropFilter: 'blur(6px)',
                  color: '#FFFFFF',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 12,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <XIcon size={14} /> Remove &amp; Retake
              </button>

              {/* Quick Resume Button if next view is pending */}
              {nextPendingView && (
                <div style={{
                  position: 'absolute',
                  bottom: 20,
                  left: 0,
                  right: 0,
                  display: 'flex',
                  justifyContent: 'center',
                }}>
                  <button
                    onClick={() => {
                      setActiveView(nextPendingView);
                      if (!useCamera) setUseCamera(true);
                    }}
                    className="btn-primary"
                    style={{ padding: '10px 22px', fontSize: 13 }}
                  >
                    <CameraIcon size={16} />
                    Continue to {nextPendingView.toUpperCase()} Capture &rarr;
                  </button>
                </div>
              )}
            </div>
          ) : useCamera ? (
            /* Camera Stream */
            <div style={{ width: '100%', height: '100%', position: 'relative' }}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }}
              />

              {/* Floating PIP Badge showing previous capture while taking other angles */}
              {Object.entries(viewPreviews).find(([v]) => v !== activeView) && (
                <div
                  onClick={() => {
                    const [prevAngle] = Object.entries(viewPreviews).find(([v]) => v !== activeView)!;
                    setActiveView(prevAngle as any);
                  }}
                  style={{
                    position: 'absolute',
                    top: 14,
                    left: 14,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    backgroundColor: 'rgba(28, 25, 23, 0.85)',
                    backdropFilter: 'blur(8px)',
                    color: '#FFFFFF',
                    padding: '5px 12px 5px 6px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 11.5,
                    fontWeight: 600,
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.35)',
                    border: '1px solid rgba(255,255,255,0.22)',
                    zIndex: 10,
                  }}
                  title="Click to view previously captured angle"
                >
                  {(() => {
                    const [prevAngle, previewSrc] = Object.entries(viewPreviews).find(([v]) => v !== activeView)!;
                    return (
                      <>
                        <img
                          src={previewSrc}
                          alt="Previous angle"
                          style={{
                            width: 24,
                            height: 24,
                            borderRadius: '50%',
                            objectFit: 'cover',
                            border: '1.5px solid var(--color-sage)',
                          }}
                        />
                        <span>Prev: <strong style={{ textTransform: 'capitalize' }}>{prevAngle}</strong> ✓ (Click to view)</span>
                      </>
                    );
                  })()}
                </div>
              )}

              <div style={{
                position: 'absolute',
                bottom: 20,
                left: 0,
                right: 0,
                display: 'flex',
                justifyContent: 'center',
              }}>
                <button
                  onClick={handleCaptureFromCamera}
                  className="btn-primary"
                  style={{ padding: '12px 28px' }}
                >
                  <CameraIcon size={18} /> Take {activeView.toUpperCase()} Snapshot
                </button>
              </div>
            </div>
          ) : (
            /* Dropzone / Upload Prompt */
            <div
              onClick={() => fileInputRef.current?.click()}
              style={{
                textAlign: 'center',
                padding: 40,
                cursor: 'pointer',
                color: '#FAF7F2',
              }}
            >
              <div style={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
                color: 'var(--color-blush)',
              }}>
                <UploadIcon size={28} />
              </div>
              <h4 style={{ fontSize: 18, color: '#FFFFFF', marginBottom: 6 }}>
                Click to select {activeView.toUpperCase()} image or drag and drop
              </h4>
              <p style={{ fontSize: 13, color: '#D4C7BA' }}>
                Supports JPEG, PNG, WebP (max 10MB)
              </p>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
        </div>

        {cameraError && (
          <div style={{
            maxWidth: 600,
            margin: '0 auto 18px',
            padding: '10px 16px',
            backgroundColor: 'var(--color-danger-bg)',
            color: 'var(--color-danger-text)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 13,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}>
            <AlertCircleIcon size={16} />
            {cameraError}
          </div>
        )}

        {/* Input Method Switcher */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 16,
          marginBottom: 24,
        }}>
          {!viewPreviews[activeView] && (
            <>
              <button
                onClick={() => setUseCamera(!useCamera)}
                className="btn-secondary"
                style={{ fontSize: 13, padding: '10px 20px' }}
              >
                <CameraIcon size={16} />
                {useCamera ? 'Switch to File Upload' : 'Use Live Webcam'}
              </button>

              {!useCamera && (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="btn-primary"
                  style={{ fontSize: 13, padding: '10px 20px' }}
                >
                  <UploadIcon size={16} />
                  Choose File
                </button>
              )}
            </>
          )}
        </div>

        {/* PERSISTENT MULTI-ANGLE CAPTURE REEL (Shows all previous shots at all times) */}
        <div style={{
          padding: '16px 20px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--color-surface-subtle)',
          border: '1px solid var(--color-border-light)',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 12,
          }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--color-charcoal)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>Multi-Angle Capture Reel</span>
              <span className="pill-badge pill-neutral" style={{ fontSize: 10.5, padding: '2px 8px' }}>
                {Object.keys(viewFiles).length}/3 Captured
              </span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>
              Click any angle to inspect or retake
            </div>
          </div>

          <div className="capture-reel-grid">
            {(['front', 'left', 'right'] as const).map((view) => {
              const isCaptured = Boolean(viewPreviews[view]);
              const isActive = activeView === view;

              return (
                <div
                  key={view}
                  onClick={() => setActiveView(view)}
                  className="capture-reel-card"
                  style={{
                    backgroundColor: isActive ? 'var(--color-surface)' : 'rgba(255, 255, 255, 0.65)',
                    border: `1.5px solid ${isActive ? 'var(--color-terracotta)' : isCaptured ? 'var(--color-sage)' : 'var(--color-border)'}`,
                    boxShadow: isActive ? '0 4px 14px rgba(200, 109, 81, 0.16)' : 'none',
                    position: 'relative',
                  }}
                >
                  {isCaptured ? (
                    <div style={{ position: 'relative', width: 44, height: 44, flexShrink: 0 }}>
                      <img
                        src={viewPreviews[view]}
                        alt={`${view} photo`}
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          borderRadius: 8,
                          border: '1px solid var(--color-border)',
                        }}
                      />
                      <div style={{
                        position: 'absolute',
                        bottom: -3,
                        right: -3,
                        width: 16,
                        height: 16,
                        borderRadius: '50%',
                        backgroundColor: 'var(--color-sage)',
                        color: '#FFFFFF',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 9.5,
                        fontWeight: 700,
                        border: '1.5px solid #FFFFFF',
                      }}>
                        ✓
                      </div>
                    </div>
                  ) : (
                    <div style={{
                      width: 44,
                      height: 44,
                      borderRadius: 8,
                      backgroundColor: isActive ? 'var(--color-terracotta-subtle)' : 'var(--color-sand)',
                      color: isActive ? 'var(--color-terracotta-dark)' : 'var(--color-muted)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}>
                      <CameraIcon size={20} />
                    </div>
                  )}

                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{
                      fontSize: 12.5,
                      fontWeight: 700,
                      textTransform: 'capitalize',
                      color: isActive ? 'var(--color-terracotta-dark)' : 'var(--color-charcoal)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                    }}>
                      <span>{view} View</span>
                      {isActive && (
                        <span style={{
                          width: 6,
                          height: 6,
                          borderRadius: '50%',
                          backgroundColor: 'var(--color-terracotta)',
                          display: 'inline-block',
                        }} />
                      )}
                    </div>
                    <div className="reel-text-desc" style={{
                      fontSize: 11,
                      color: isCaptured ? 'var(--color-sage-dark)' : isActive ? 'var(--color-terracotta)' : 'var(--color-muted)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}>
                      {isCaptured ? '✓ Captured (Tap to view)' : isActive ? '🔴 Active View' : 'Pending'}
                    </div>
                  </div>

                  {isCaptured && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveView(view);
                      }}
                      title="Retake this view"
                      style={{
                        padding: 4,
                        color: 'var(--color-muted)',
                        borderRadius: 4,
                        flexShrink: 0,
                      }}
                    >
                      <RefreshIcon size={13} />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Uploaded Views Summary Bar */}
      <div className="glass-panel" style={{
        padding: '18px 22px',
        backgroundColor: '#FFFFFF',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 14,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
          {(['front', 'left', 'right'] as const).map((view) => {
            const hasThumb = Boolean(viewPreviews[view]);

            return (
              <div
                key={view}
                onClick={() => setActiveView(view)}
                style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}
              >
                {hasThumb ? (
                  <img
                    src={viewPreviews[view]}
                    alt={`${view} thumb`}
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: 6,
                      objectFit: 'cover',
                      border: activeView === view ? '2px solid var(--color-terracotta)' : '1px solid var(--color-border)',
                    }}
                  />
                ) : (
                  <div style={{
                    width: 28,
                    height: 28,
                    borderRadius: 6,
                    backgroundColor: activeView === view ? 'var(--color-terracotta-subtle)' : 'var(--color-sand)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: activeView === view ? 'var(--color-terracotta-dark)' : 'var(--color-muted)',
                  }}>
                    <CameraIcon size={14} />
                  </div>
                )}
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, textTransform: 'capitalize', color: 'var(--color-charcoal)' }}>
                    {view}
                  </div>
                  <div style={{ fontSize: 10.5, color: hasThumb ? 'var(--color-sage-dark)' : 'var(--color-muted)' }}>
                    {hasThumb ? '✓ Captured' : (activeView === view ? 'Active' : 'Pending')}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', maxWidth: 360, justifyContent: 'flex-end', marginLeft: 'auto' }}>
          <button onClick={onBack} className="btn-ghost" style={{ padding: '8px 14px' }}>
            Back
          </button>

          <button
            onClick={() => onComplete(viewFiles as Record<'front' | 'left' | 'right', File>, captureModes)}
            disabled={!isReadyToProceed}
            className="btn-primary"
            style={{ padding: '11px 20px', flex: 1, justifyContent: 'center' }}
          >
            Process &amp; Analyze {Boolean(viewFiles.front) && `(${Object.keys(viewFiles).length} View${Object.keys(viewFiles).length > 1 ? 's' : ''})`}
          </button>
        </div>
      </div>
    </div>
  );
};

