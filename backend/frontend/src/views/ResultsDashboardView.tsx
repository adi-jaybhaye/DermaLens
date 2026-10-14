import React, { useState } from 'react';
import type { AssessmentResults, RegionXaiDetails, XaiSource } from '../api/client';
import {
  SparklesIcon,
  EyeIcon,
  ShieldCheckIcon,
  ExternalLinkIcon,
  InfoIcon,
  RefreshIcon,
  CameraIcon,
} from '../components/Icons';
import {
  formatAssessmentDateTime,
  formatAssessmentStatus,
  getStatusBadgeClass,
  formatCaptureBadge,
  getViewCaptureBadge,
} from '../utils/formatters';

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
  const [showLearnMore, setShowLearnMore] = useState<boolean>(false);
  const [showSkinTypeRationale, setShowSkinTypeRationale] = useState<boolean>(false);

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

  const xaiDetails: RegionXaiDetails | undefined =
    activeRegionData?.xai_explanation?.xai || concern?.xai;

  return (
    <div style={{ maxWidth: 1180, margin: '0 auto', padding: '30px 20px 90px' }}>
      {/* Result Header with Assessment Identity (Loop 10) */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16,
        marginBottom: 24,
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4, flexWrap: 'wrap' }}>
            <span className={`pill-badge ${getStatusBadgeClass(results.status)}`} style={{ fontSize: 11.5 }}>
              {formatAssessmentStatus(results.status)}
            </span>
            <span style={{ fontSize: 13, color: 'var(--color-muted)' }}>
              Completed &bull; {formatAssessmentDateTime(results.created_at)}
            </span>
          </div>

          <h1 style={{
            fontSize: 'clamp(24px, 4vw, 32px)',
            fontWeight: 700,
            color: 'var(--color-charcoal)',
            letterSpacing: '-0.5px',
          }}>
            {results.name || (results.assessment_number ? `Assessment ${results.assessment_number}` : 'Facial Skin Assessment')}
          </h1>

          <div style={{ fontSize: 14, color: 'var(--color-muted)', marginTop: 2 }}>
            Objective Multi-View Surface Evaluation with Explainable AI
          </div>
        </div>

        <button
          onClick={onNewAssessment}
          className="btn-secondary"
          style={{ padding: '9px 18px', fontSize: 13, display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600 }}
        >
          <RefreshIcon size={14} /> Start New Assessment
        </button>
      </div>

      {/* Assessment Overview (Loop 9) */}
      <div
        className="glass-panel"
        style={{
          padding: '18px 24px',
          backgroundColor: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          marginBottom: 24,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 16,
          border: '1px solid var(--color-border-light)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-muted)', letterSpacing: '0.6px' }}>
            Multi-View Coverage
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-charcoal)', marginTop: 2 }}>
            {availableViews.length} {availableViews.length === 1 ? 'View' : 'Views'} Analyzed
          </div>
          <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 2 }}>
            {availableViews.map(v => v.charAt(0).toUpperCase() + v.slice(1)).join(', ')}
          </div>
        </div>

        <div>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-muted)', letterSpacing: '0.6px' }}>
            Facial Mesh Mapping
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-charcoal)', marginTop: 2 }}>
            5 Facial Zones
          </div>
          <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 2 }}>
            Forehead, Cheeks, Nose, Chin
          </div>
        </div>

        <div>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-muted)', letterSpacing: '0.6px' }}>
            Capture Method
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-charcoal)', marginTop: 2 }}>
            {formatCaptureBadge(results.capture_type, results.capture_modes)}
          </div>
          <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 2 }}>
            Standardized optical capture
          </div>
        </div>

        <div>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-muted)', letterSpacing: '0.6px' }}>
            Analysis Status
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
            <span className={`pill-badge ${getStatusBadgeClass(results.status)}`} style={{ fontSize: 11.5 }}>
              {formatAssessmentStatus(results.status)}
            </span>
          </div>
          <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 2 }}>
            Deep XAI &amp; surface synthesis ready
          </div>
        </div>
      </div>

      {/* Multi-View Visual Summary (Loop 8) */}
      <div style={{ marginBottom: 26 }}>
        <div style={{
          fontSize: 12,
          fontWeight: 700,
          color: 'var(--color-muted)',
          marginBottom: 10,
          textTransform: 'uppercase',
          letterSpacing: '0.6px',
        }}>
          Facial Perspective Summary (Select view to inspect)
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 14,
        }}>
          {availableViews.map((view) => {
            const isSelected = selectedView === view;
            const viewData = results.views[view];
            const sampleThumb = Object.values(viewData?.xai || {}).find(x => x.overlay_base64)?.overlay_base64;
            const captureMethod = getViewCaptureBadge(view, results.capture_modes);
            const viewTitle = view === 'front' ? 'Frontal View' : view === 'left' ? 'Left Profile' : 'Right Profile';

            return (
              <div
                key={view}
                onClick={() => setSelectedView(view)}
                className="glass-panel"
                style={{
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: isSelected ? 'var(--color-blush-light)' : '#FFFFFF',
                  border: `2px solid ${isSelected ? 'var(--color-terracotta)' : 'var(--color-border-light)'}`,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 14,
                  transition: 'all var(--transition-fast)',
                  boxShadow: isSelected ? 'var(--shadow-sm)' : 'none',
                }}
              >
                {/* Thumbnail / Visual Indicator */}
                <div style={{
                  width: 48,
                  height: 48,
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-sand)',
                  overflow: 'hidden',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  border: '1px solid var(--color-border)',
                }}>
                  {sampleThumb ? (
                    <img
                      src={`data:image/jpeg;base64,${sampleThumb}`}
                      alt={`${view} assessment thumbnail`}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <CameraIcon size={20} color="var(--color-terracotta)" />
                  )}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6 }}>
                    <div style={{ fontWeight: 700, fontSize: 13.5, color: 'var(--color-charcoal)' }}>
                      {viewTitle}
                    </div>
                    {isSelected && (
                      <span style={{ fontSize: 9.5, fontWeight: 700, color: 'var(--color-terracotta)', textTransform: 'uppercase' }}>
                        Active
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 3, flexWrap: 'wrap' }}>
                    <span style={{
                      fontSize: 10.5,
                      padding: '1px 7px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: 'var(--color-surface-subtle)',
                      border: '1px solid var(--color-border-light)',
                      color: 'var(--color-mocha)',
                      fontWeight: 600,
                    }}>
                      {captureMethod}
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--color-muted)' }}>
                      &bull; 5 Zones
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Grid: Left Column (Skin Type + Regions) & Right Column (XAI Visuals) */}
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

            {results.skin_type?.scientific_rationale && (
              <div style={{ marginTop: 12 }}>
                <button
                  onClick={() => setShowSkinTypeRationale(!showSkinTypeRationale)}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: 0,
                    color: 'var(--color-terracotta)',
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: 'pointer',
                    textDecoration: 'underline',
                  }}
                >
                  {showSkinTypeRationale ? 'Hide scientific reason' : 'Why is camera skin typing unavailable?'}
                </button>

                {showSkinTypeRationale && (
                  <div style={{
                    marginTop: 10,
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--color-surface-subtle)',
                    fontSize: 12,
                    color: 'var(--color-mocha)',
                    lineHeight: 1.55,
                    border: '1px solid var(--color-border-light)',
                  }}>
                    {results.skin_type.scientific_rationale}
                  </div>
                )}
              </div>
            )}
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
                          <span>Possible visible pattern: <strong>{regConcern.display_name}</strong></span>
                        ) : (
                          'No dominant pattern detected'
                        )}
                      </div>
                    </div>

                    {confidence !== null && (
                      <div style={{ textAlign: 'right' }}>
                        <span className="pill-badge pill-terracotta" style={{ fontSize: 11 }}>
                          Model confidence: {confidence}%
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Explainable AI & Visual Focus Analysis */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Visual Focus / Grad-CAM Card */}
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
                  Visual focus analysis for {regionDisplayNames[selectedRegion]} is generated during scan.
                </div>
              )}
            </div>

            {/* Visual Focus Scientific Grounding Note */}
            <div style={{
              fontSize: 12,
              color: 'var(--color-muted)',
              lineHeight: 1.55,
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <div style={{ fontWeight: 600, color: 'var(--color-mocha)', marginBottom: 2 }}>
                Visual Focus Explanation:
              </div>
              <div>
                The highlighted area shows image features that influenced the model's prediction. It does not show medical cause or diagnosis.
              </div>
              {xaiDetails?.heatmap_explanation && (
                <div style={{ marginTop: 4, color: 'var(--color-muted)' }}>
                  {xaiDetails.heatmap_explanation}
                </div>
              )}
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

      {/* Main Two-Level XAI Explanation Section */}
      {concern && (
        <section className="glass-panel" style={{ padding: '34px 32px', backgroundColor: '#FFFFFF', marginTop: 24, marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, marginBottom: 10 }}>
            <div className="pill-badge pill-terracotta">
              Explainable AI Assessment &bull; {regionDisplayNames[selectedRegion]}
            </div>
            <div style={{ fontSize: 12, color: 'var(--color-muted)' }}>
              Model confidence: <strong>{Math.round(concern.confidence * 100)}%</strong>
            </div>
          </div>

          <h3 style={{ fontSize: 24, fontWeight: 700, marginBottom: 18 }}>
            Understanding the Visible Pattern: {concern.display_name}
          </h3>

          {/* LEVEL 1 — Everyday Easy Language (4 Core Pillars) */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 250px), 1fr))',
            gap: 16,
          }}>
            {/* 1. What did we notice? */}
            <div style={{
              padding: '18px 20px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 6, color: 'var(--color-terracotta-dark)' }}>
                1. What did we notice?
              </h5>
              <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.55 }}>
                {xaiDetails?.what_we_noticed || (
                  `We observed visual surface characteristics consistent with ${concern.display_name.toLowerCase()}.`
                )}
              </p>
            </div>

            {/* 2. Where did we notice it? */}
            <div style={{
              padding: '18px 20px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 6, color: 'var(--color-terracotta-dark)' }}>
                2. Where did we notice it?
              </h5>
              <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.55 }}>
                {xaiDetails?.where_we_noticed_it || (
                  `In the ${regionDisplayNames[selectedRegion].toLowerCase()} region of the face.`
                )}
              </p>
            </div>

            {/* 3. Why did the AI identify it? */}
            <div style={{
              padding: '18px 20px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 6, color: 'var(--color-terracotta-dark)' }}>
                3. Why did the AI identify it?
              </h5>
              <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.55 }}>
                {xaiDetails?.why_ai_identified_it || concern.why_identified}
              </p>
            </div>

            {/* 4. Why can this occur? */}
            <div style={{
              padding: '18px 20px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-surface-subtle)',
              border: '1px solid var(--color-border-light)',
            }}>
              <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 6, color: 'var(--color-terracotta-dark)' }}>
                4. Why can this visual pattern occur?
              </h5>
              <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.55 }}>
                {xaiDetails?.why_it_can_occur || concern.why_it_can_occur}
              </p>
            </div>
          </div>

          {/* Visual Evidence / Surface Traits */}
          {concern.visual_evidence && concern.visual_evidence.length > 0 && (
            <div style={{ marginTop: 22 }}>
              <div style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--color-muted)', marginBottom: 8 }}>
                Associated surface visual traits:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {concern.visual_evidence.map((trait, i) => (
                  <span
                    key={i}
                    style={{
                      padding: '4px 12px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: 'var(--color-sand)',
                      fontSize: 12,
                      color: 'var(--color-charcoal)',
                    }}
                  >
                    &bull; {trait}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* LEVEL 2 — Interactive "Learn More" Expandable Section */}
          <div style={{ marginTop: 28, paddingTop: 20, borderTop: '1px solid var(--color-border-light)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
              <div>
                <h4 style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-charcoal)' }}>
                  Deep Scientific Background &amp; Research Evidence
                </h4>
                <p style={{ fontSize: 12.5, color: 'var(--color-muted)', marginTop: 2 }}>
                  Explore biological mechanisms, contributing factors, study limitations, and verified citations.
                </p>
              </div>

              <button
                onClick={() => setShowLearnMore(!showLearnMore)}
                className="btn-secondary"
                style={{ padding: '8px 18px', fontSize: 13, fontWeight: 600 }}
              >
                {showLearnMore ? 'Collapse Scientific Details' : 'Learn More (Scientific Evidence)'}
              </button>
            </div>

            {showLearnMore && (
              <div style={{
                marginTop: 20,
                padding: '24px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1.5px solid var(--color-border)',
                display: 'flex',
                flexDirection: 'column',
                gap: 20,
              }}>
                {/* Scientific Explanation */}
                {xaiDetails?.learn_more?.scientific_explanation && (
                  <div>
                    <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: 'var(--color-terracotta-dark)' }}>
                      Biological &amp; Physiological Background
                    </h5>
                    <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.65 }}>
                      {xaiDetails.learn_more.scientific_explanation}
                    </p>
                  </div>
                )}

                {/* Common Contributing Factors */}
                {xaiDetails?.learn_more?.contributing_factors && xaiDetails.learn_more.contributing_factors.length > 0 && (
                  <div>
                    <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: 'var(--color-terracotta-dark)' }}>
                      Research-Documented Contributing Factors
                    </h5>
                    <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13, color: 'var(--color-mocha)', lineHeight: 1.6 }}>
                      {xaiDetails.learn_more.contributing_factors.map((factor, idx) => (
                        <li key={idx} style={{ marginBottom: 4 }}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Important Research & Imaging Limitations */}
                {xaiDetails?.learn_more?.limitations && (
                  <div>
                    <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: 'var(--color-terracotta-dark)' }}>
                      Important Methodological &amp; Imaging Limitations
                    </h5>
                    <p style={{ fontSize: 13, color: 'var(--color-muted)', lineHeight: 1.6, backgroundColor: '#FFFFFF', padding: '12px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border-light)' }}>
                      {xaiDetails.learn_more.limitations}
                    </p>
                  </div>
                )}

                {/* Safety Guidance */}
                {xaiDetails?.learn_more?.safety_guidance && (
                  <div>
                    <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 6, color: 'var(--color-terracotta-dark)' }}>
                      Dermatological Safety Advice
                    </h5>
                    <p style={{ fontSize: 13, color: 'var(--color-mocha)', lineHeight: 1.55 }}>
                      {xaiDetails.learn_more.safety_guidance}
                    </p>
                  </div>
                )}

                {/* Traceable Evidence Sources */}
                {xaiDetails?.learn_more?.sources && xaiDetails.learn_more.sources.length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.6px', color: 'var(--color-muted)', marginBottom: 12 }}>
                      Verified Supporting Research Documents (backend/data/research/)
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 300px), 1fr))', gap: 12 }}>
                      {xaiDetails.learn_more.sources.map((src: XaiSource) => (
                        <div
                          key={src.id}
                          style={{
                            padding: '14px 16px',
                            borderRadius: 'var(--radius-sm)',
                            backgroundColor: '#FFFFFF',
                            border: '1px solid var(--color-border-light)',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            gap: 8,
                          }}
                        >
                          <div>
                            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-terracotta)' }}>
                              [{src.id}] &bull; {src.authority} ({src.year})
                            </div>
                            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-charcoal)', marginTop: 3 }}>
                              {src.title}
                            </div>
                            <div style={{ fontSize: 11.5, color: 'var(--color-muted)', marginTop: 2 }}>
                              {src.authors}
                            </div>
                            <div style={{ fontSize: 12, color: 'var(--color-mocha)', marginTop: 6, lineHeight: 1.45 }}>
                              {src.key_findings}
                            </div>
                          </div>

                          {src.url && (
                            <a
                              href={src.url}
                              target="_blank"
                              rel="noreferrer"
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: 5,
                                fontSize: 11.5,
                                fontWeight: 600,
                                color: 'var(--color-terracotta)',
                                marginTop: 6,
                              }}
                            >
                              <span>View Reference</span>
                              <ExternalLinkIcon size={11} />
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
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
