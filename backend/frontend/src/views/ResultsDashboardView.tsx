import React, { useState } from 'react';
import type { AssessmentResults } from '../api/client';
import { SparklesIcon, EyeIcon, ShieldCheckIcon, ExternalLinkIcon, InfoIcon, RefreshIcon } from '../components/Icons';

interface ResultsDashboardViewProps {
  results: AssessmentResults;
  onNewAssessment: () => void;
}

export const ResultsDashboardView: React.FC<ResultsDashboardViewProps> = ({ results, onNewAssessment }) => {
  const availableViews = Object.keys(results.views) as Array<'front' | 'left' | 'right'>;
  const [selectedView, setSelectedView] = useState<'front' | 'left' | 'right'>(
    availableViews.includes('front') ? 'front' : availableViews[0] || 'front'
  );
  const [selectedRegion, setSelectedRegion] = useState<string>('forehead');
  const [xaiMode, setXaiMode] = useState<'overlay' | 'heatmap'>('overlay');

  const currentViewData = results.views[selectedView];
  const regions = currentViewData?.regions || {};
  const activeRegionData = regions[selectedRegion];
  const concern = activeRegionData?.concern;
  const xaiMap = currentViewData?.xai || {};
  const activeXai = xaiMap[selectedRegion];

  const regionDisplayNames: Record<string, string> = {
    forehead: 'Forehead',
    left_cheek: 'Left Cheek',
    right_cheek: 'Right Cheek',
    nose: 'Nose & Midface',
    chin: 'Chin & Jawline',
  };

  return (
    <div style={{ maxWidth: 1180, margin: '0 auto', padding: '30px 20px 90px' }}>
      {/* Top Banner & Multi-View Switcher */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16,
        marginBottom: 28,
      }}>
        <div>
          <div className="pill-badge pill-sage" style={{ marginBottom: 6 }}>
            Assessment Complete &bull; Session #{results.assessment_id.slice(-6)}
          </div>
          <h2 style={{ fontSize: 28, fontWeight: 700 }}>
            Facial Skin Assessment Dashboard
          </h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            display: 'flex',
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-full)',
            padding: 4,
          }}>
            {availableViews.map((view) => (
              <button
                key={view}
                onClick={() => setSelectedView(view)}
                style={{
                  padding: '7px 18px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 13,
                  fontWeight: selectedView === view ? 600 : 500,
                  backgroundColor: selectedView === view ? 'var(--color-terracotta)' : 'transparent',
                  color: selectedView === view ? '#FFFFFF' : 'var(--color-charcoal)',
                  textTransform: 'capitalize',
                  transition: 'all var(--transition-fast)',
                }}
              >
                {view} View
              </button>
            ))}
          </div>

          <button onClick={onNewAssessment} className="btn-secondary" style={{ padding: '8px 16px', fontSize: 13 }}>
            <RefreshIcon size={14} /> New
          </button>
        </div>
      </div>

      {/* Grid: Left Column (Skin Type + Regions) & Right Column (XAI & Evidence) */}
      <div className="results-grid-layout">
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Skin Type Module Card */}
          <div className="glass-panel" style={{ padding: '24px 26px', backgroundColor: '#FFFFFF' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <SparklesIcon size={18} color="var(--color-terracotta)" />
                <h4 style={{ fontSize: 17, fontWeight: 700 }}>Skin Type Status</h4>
              </div>
              <span className="pill-badge pill-neutral" style={{ fontSize: 11 }}>
                {results.skin_type?.status || 'Unavailable'}
              </span>
            </div>

            <p style={{ fontSize: 13, color: 'var(--color-muted)', lineHeight: 1.55 }}>
              {results.skin_type?.note || (
                'Skin type determination requires physical sebum measurement and barrier evaluation. DermaLens focuses on 8 visible surface skin patterns.'
              )}
            </p>
          </div>

          {/* Facial Regions Selector & Overview */}
          <div className="glass-panel" style={{ padding: '24px 26px', backgroundColor: '#FFFFFF' }}>
            <h4 style={{ fontSize: 17, fontWeight: 700, marginBottom: 14 }}>
              Facial Regions ({selectedView.toUpperCase()} VIEW)
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {Object.keys(regionDisplayNames).map((regionKey) => {
                const regData = regions[regionKey];
                const isSelected = selectedRegion === regionKey;
                const regConcern = regData?.concern;
                const confidence = regConcern ? Math.round(regConcern.confidence * 100) : null;

                return (
                  <div
                    key={regionKey}
                    onClick={() => setSelectedRegion(regionKey)}
                    style={{
                      padding: '14px 18px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: isSelected ? 'var(--color-blush-light)' : 'var(--color-surface-subtle)',
                      border: `1.5px solid ${isSelected ? 'var(--color-terracotta)' : 'var(--color-border-light)'}`,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'all var(--transition-fast)',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>
                        {regionDisplayNames[regionKey]}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 2 }}>
                        {regConcern ? (
                          <span>Detected pattern: <strong>{regConcern.display_name}</strong></span>
                        ) : (
                          'No dominant concern detected'
                        )}
                      </div>
                    </div>

                    {confidence !== null && (
                      <div style={{ textAlign: 'right' }}>
                        <span className="pill-badge pill-terracotta" style={{ fontSize: 11 }}>
                          {confidence}% Match
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Explainable AI & Detailed Evidence */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Grad-CAM Visualizer Card */}
          <div className="glass-panel" style={{ padding: '24px 26px', backgroundColor: '#FFFFFF' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <EyeIcon size={18} color="var(--color-terracotta)" />
                <h4 style={{ fontSize: 17, fontWeight: 700 }}>
                  Visual Focus Analysis
                </h4>
              </div>

              {activeXai && (
                <div style={{ display: 'flex', gap: 6 }}>
                  <button
                    onClick={() => setXaiMode('overlay')}
                    style={{
                      padding: '4px 12px',
                      borderRadius: 'var(--radius-full)',
                      fontSize: 11,
                      fontWeight: 600,
                      backgroundColor: xaiMode === 'overlay' ? 'var(--color-terracotta)' : 'var(--color-sand)',
                      color: xaiMode === 'overlay' ? '#FFFFFF' : 'var(--color-charcoal)',
                    }}
                  >
                    Overlay
                  </button>
                  <button
                    onClick={() => setXaiMode('heatmap')}
                    style={{
                      padding: '4px 12px',
                      borderRadius: 'var(--radius-full)',
                      fontSize: 11,
                      fontWeight: 600,
                      backgroundColor: xaiMode === 'heatmap' ? 'var(--color-terracotta)' : 'var(--color-sand)',
                      color: xaiMode === 'heatmap' ? '#FFFFFF' : 'var(--color-charcoal)',
                    }}
                  >
                    Heatmap
                  </button>
                </div>
              )}
            </div>

            {/* XAI Visualization Image Box */}
            <div style={{
              width: '100%',
              aspectRatio: '1/1',
              maxHeight: 320,
              backgroundColor: '#1E1B18',
              borderRadius: 'var(--radius-md)',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 14,
              border: '1px solid var(--color-border)',
            }}>
              {activeXai?.overlay_base64 ? (
                <img
                  src={`data:image/png;base64,${xaiMode === 'overlay' ? activeXai.overlay_base64 : activeXai.heatmap_base64}`}
                  alt="Visual focus heatmap"
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              ) : (
                <div style={{ textAlign: 'center', padding: 20, color: '#D4C7BA', fontSize: 13 }}>
                  <InfoIcon size={24} style={{ margin: '0 auto 8px', opacity: 0.7 }} />
                  Visual focus heatmap for {regionDisplayNames[selectedRegion]} is generated during analysis.
                </div>
              )}
            </div>

            {/* Visual Focus Clinical Disclaimer Note */}
            <div style={{
              fontSize: 12,
              color: 'var(--color-muted)',
              lineHeight: 1.5,
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <strong>Visual Guide Only:</strong> Highlighted regions (red/yellow) indicate key focal areas identified during visual assessment. This does not indicate medical diagnosis or causality.
            </div>
          </div>

          {/* Probabilities Distribution */}
          {activeRegionData?.all_probabilities && (
            <div className="glass-panel" style={{ padding: '20px 24px', backgroundColor: '#FFFFFF' }}>
              <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>
                Evaluated Pattern Likelihood ({regionDisplayNames[selectedRegion]})
              </h5>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {Object.entries(activeRegionData.all_probabilities)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 4)
                  .map(([name, prob]) => (
                    <div key={name}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 3 }}>
                        <span style={{ textTransform: 'capitalize' }}>{name}</span>
                        <span style={{ fontWeight: 600 }}>{Math.round(prob * 100)}%</span>
                      </div>
                      <div style={{ height: 6, borderRadius: 3, backgroundColor: 'var(--color-sand)', overflow: 'hidden' }}>
                        <div style={{
                          height: '100%',
                          width: `${Math.round(prob * 100)}%`,
                          backgroundColor: name === concern?.concept ? 'var(--color-terracotta)' : 'var(--color-muted)',
                        }} />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Scientific Knowledge & Evidence Synthesis Box */}
      {concern && (
        <section className="glass-panel" style={{ padding: '34px 32px', backgroundColor: '#FFFFFF', marginBottom: 32 }}>
          <div className="pill-badge pill-terracotta" style={{ marginBottom: 10 }}>
            Curated Dermatological Knowledge
          </div>

          <h3 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
            Understanding {concern.display_name}
          </h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 260px), 1fr))',
            gap: 16,
            marginTop: 20,
          }}>
            {/* Why Identified */}
            <div style={{
              padding: '20px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <h5 style={{ fontSize: 15, fontWeight: 700, marginBottom: 6, color: 'var(--color-terracotta-dark)' }}>
                1. Why Was This Identified?
              </h5>
              <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.55 }}>
                {concern.why_identified}
              </p>
            </div>

            {/* Why It Can Occur Scientifically */}
            <div style={{
              padding: '20px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <h5 style={{ fontSize: 15, fontWeight: 700, marginBottom: 6, color: 'var(--color-terracotta-dark)' }}>
                2. Why It Can Occur Scientifically
              </h5>
              <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.55 }}>
                {concern.why_it_can_occur}
              </p>
            </div>
          </div>

          {/* Visual Evidence / Characteristics */}
          {concern.visual_evidence && concern.visual_evidence.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 10 }}>
                Visual Pattern Characteristics
              </h5>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {concern.visual_evidence.map((trait, i) => (
                  <span
                    key={i}
                    style={{
                      padding: '5px 12px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: 'var(--color-sand)',
                      fontSize: 12.5,
                      color: 'var(--color-charcoal)',
                    }}
                  >
                    &bull; {trait}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Curated Sourced References */}
          {concern.sources && concern.sources.length > 0 && (
            <div style={{ marginTop: 26, paddingTop: 20, borderTop: '1px solid var(--color-border-light)' }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.6px', color: 'var(--color-muted)', marginBottom: 12 }}>
                Evidence &amp; Clinical Citations
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                {concern.sources.map((src, i) => (
                  <a
                    key={i}
                    href={src.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 6,
                      padding: '6px 14px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: 'var(--color-blush)',
                      fontSize: 12,
                      fontWeight: 600,
                      color: 'var(--color-terracotta-dark)',
                    }}
                  >
                    <span>{src.title} — {src.source}</span>
                    <ExternalLinkIcon size={12} />
                  </a>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {/* Safety & Consultation Guidance Box */}
      <section style={{
        padding: '24px 28px',
        borderRadius: 'var(--radius-lg)',
        backgroundColor: 'var(--color-warning-bg)',
        border: '1px solid var(--color-warning-border)',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <ShieldCheckIcon size={22} color="var(--color-warning-text)" />
          <h4 style={{ fontSize: 17, fontWeight: 700, color: 'var(--color-warning-text)' }}>
            Professional Consultation &amp; Non-Diagnostic Notice
          </h4>
        </div>

        <p style={{ fontSize: 13.5, color: 'var(--color-warning-text)', lineHeight: 1.6 }}>
          {results.safety?.disclaimer}
        </p>

        <div style={{
          fontSize: 12.5,
          color: 'var(--color-mocha)',
          borderTop: '1px dashed var(--color-warning-border)',
          paddingTop: 10,
        }}>
          <strong>Important Clinical Notice:</strong> DermaLens is an informational wellness tool and not an FDA-cleared medical diagnostic device. If you experience discomfort, persistent or spreading redness, changing lesions, or pain, please schedule an in-person appointment with a board-certified dermatologist.
        </div>
      </section>
    </div>
  );
};
