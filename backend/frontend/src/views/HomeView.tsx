import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { SparklesIcon, CameraIcon, ShieldCheckIcon, EyeIcon, BookOpenIcon, ChevronRightIcon } from '../components/Icons';

interface HomeViewProps {
  onStartAssessment: () => void;
  onOpenHistoryItem: (id: string) => void;
  onExploreKnowledge: () => void;
}

export const HomeView: React.FC<HomeViewProps> = ({
  onStartAssessment,
  onOpenHistoryItem,
  onExploreKnowledge,
}) => {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    api.getAssessmentHistory().then(setHistory).catch(() => {});
  }, []);

  const concernsList = [
    { name: 'Redness (Erythema)', desc: 'Surface vascular dilation and flushing patterns' },
    { name: 'Dark Spots', desc: 'Melanin concentrations and post-inflammatory pigmentation' },
    { name: 'Inflammatory Acne', desc: 'Erythematous papules and inflammatory lesions' },
    { name: 'Blackheads', desc: 'Open comedones with oxidised surface keratin' },
    { name: 'Whiteheads', desc: 'Closed follicular comedones with trapped sebum' },
    { name: 'Pigmentation', desc: 'Uneven tone, sun spots, and melasma distribution' },
    { name: 'Enlarged Pores', desc: 'Prominent follicular openings with visible texture' },
    { name: 'Fine Lines & Wrinkles', desc: 'Surface folds, dynamic expression lines, and collagen depletion' },
  ];

  return (
    <div style={{ maxWidth: 1140, margin: '0 auto', padding: '40px 20px 80px' }}>
      {/* Hero Section */}
      <section style={{
        textAlign: 'center',
        padding: '50px 20px 60px',
        position: 'relative',
      }}>
        <div className="pill-badge pill-terracotta" style={{ marginBottom: 18 }}>
          <SparklesIcon size={14} />
          Evidence-Based Visual Analysis &bull; Precision Facial Mapping
        </div>

        <h1 className="hero-h1" style={{
          fontSize: 'clamp(28px, 5vw, 54px)',
          fontWeight: 700,
          color: 'var(--color-charcoal)',
          lineHeight: 1.18,
          letterSpacing: '-0.8px',
          maxWidth: 820,
          margin: '0 auto 20px',
        }}>
          Objective Facial Skin Pattern Analysis with <span style={{
            background: 'linear-gradient(135deg, var(--color-terracotta) 0%, #D96A4A 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>Explainable AI</span>
        </h1>

        <p style={{
          fontSize: 17,
          color: 'var(--color-muted)',
          maxWidth: 680,
          margin: '0 auto 34px',
          lineHeight: 1.6,
        }}>
          DermaLens couples high-resolution multi-view facial landmarking with deep visual pattern recognition and interactive focus heatmaps, grounded in curated dermatological literature.
        </p>

        <div className="hero-cta-group" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 14,
          flexWrap: 'wrap',
        }}>
          <button
            onClick={onStartAssessment}
            className="btn-primary"
            style={{ fontSize: 15, padding: '14px 30px' }}
          >
            <CameraIcon size={20} />
            Start Skin Assessment
          </button>
          
          <button
            onClick={onExploreKnowledge}
            className="btn-secondary"
            style={{ fontSize: 15, padding: '14px 26px' }}
          >
            <BookOpenIcon size={18} />
            Explore Scientific Knowledge
          </button>
        </div>

        {/* Clinical Disclaimer Banner */}
        <div style={{
          marginTop: 40,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 10,
          padding: '10px 20px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: 'var(--color-warning-bg)',
          border: '1px solid var(--color-warning-border)',
          color: 'var(--color-warning-text)',
          fontSize: 13,
          fontWeight: 500,
        }}>
          <ShieldCheckIcon size={17} />
          <span>
            <strong>Informational &amp; Educational Tool:</strong> Not a medical diagnostic system. Never claim an image proves etiology.
          </span>
        </div>
      </section>

      {/* System Pipeline Highlights */}
      <section style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 20,
        marginBottom: 60,
      }}>
        <div className="glass-panel" style={{ padding: '26px 24px' }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 14,
            backgroundColor: 'var(--color-blush)',
            color: 'var(--color-terracotta)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 16,
          }}>
            <CameraIcon size={22} />
          </div>
          <h4 style={{ fontSize: 17, marginBottom: 8 }}>Multi-View Capture</h4>
          <p style={{ fontSize: 13.5, color: 'var(--color-muted)', lineHeight: 1.55 }}>
            Front, Left, and Right facial perspectives evaluated independently without fabricated cross-view aggregation.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '26px 24px' }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 14,
            backgroundColor: 'var(--color-sage-light)',
            color: 'var(--color-sage-dark)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 16,
          }}>
            <SparklesIcon size={22} />
          </div>
          <h4 style={{ fontSize: 17, marginBottom: 8 }}>5-Region Facial Mapping</h4>
          <p style={{ fontSize: 13.5, color: 'var(--color-muted)', lineHeight: 1.55 }}>
            Precision facial mesh mapping isolates Forehead, Cheeks, Nose, and Chin regions for targeted surface evaluation.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '26px 24px' }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 14,
            backgroundColor: 'var(--color-sand)',
            color: 'var(--color-mocha)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 16,
          }}>
            <EyeIcon size={22} />
          </div>
          <h4 style={{ fontSize: 17, marginBottom: 8 }}>Visual Focus Heatmaps</h4>
          <p style={{ fontSize: 13.5, color: 'var(--color-muted)', lineHeight: 1.55 }}>
            Interactive focus heatmaps highlight the specific skin areas evaluated during your assessment.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '26px 24px' }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 14,
            backgroundColor: 'rgba(42, 60, 77, 0.08)',
            color: 'var(--color-navy)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 16,
          }}>
            <ShieldCheckIcon size={22} />
          </div>
          <h4 style={{ fontSize: 17, marginBottom: 8 }}>Curated Medical Evidence</h4>
          <p style={{ fontSize: 13.5, color: 'var(--color-muted)', lineHeight: 1.55 }}>
            Curated dermatological facts from the Mayo Clinic, AAD, and DermNet NZ explain why features can occur.
          </p>
        </div>
      </section>

      {/* 8 Visible Concerns Detected */}
      <section style={{ marginBottom: 60 }}>
        <div style={{ textAlign: 'center', marginBottom: 30 }}>
          <h3 style={{ fontSize: 28, marginBottom: 8 }}>8 Evaluated Concern Patterns</h3>
          <p style={{ fontSize: 15, color: 'var(--color-muted)' }}>
            Comprehensive dermatological analysis across 8 visible facial skin characteristics
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: 16,
        }}>
          {concernsList.map((item, idx) => (
            <div
              key={idx}
              className="glass-panel"
              style={{
                padding: '18px 20px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: 14,
              }}
            >
              <div style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                backgroundColor: 'var(--color-terracotta-subtle)',
                color: 'var(--color-terracotta)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 12,
                fontWeight: 700,
                flexShrink: 0,
              }}>
                {idx + 1}
              </div>
              <div>
                <h5 style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>{item.name}</h5>
                <p style={{ fontSize: 12.5, color: 'var(--color-muted)', lineHeight: 1.45 }}>{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Recent Assessment Sessions */}
      {history.length > 0 && (
        <section className="glass-panel" style={{ padding: '30px 28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <h4 style={{ fontSize: 20 }}>Recent Assessments</h4>
              <p style={{ fontSize: 13, color: 'var(--color-muted)' }}>Your previously generated multi-view assessment sessions</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {history.slice(0, 5).map((item) => (
              <div
                key={item.id}
                onClick={() => onOpenHistoryItem(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 18px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border-light)',
                  cursor: 'pointer',
                  transition: 'transform var(--transition-fast), border-color var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateX(4px)';
                  e.currentTarget.style.borderColor = 'var(--color-terracotta)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.borderColor = 'var(--color-border-light)';
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>
                    Session #{item.id.slice(-6)}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 2 }}>
                    Views: {item.views?.join(', ') || 'front'} &bull; {new Date(item.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="pill-badge pill-sage" style={{ fontSize: 11 }}>
                    {item.status}
                  </span>
                  <ChevronRightIcon size={18} color="var(--color-muted)" />
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
