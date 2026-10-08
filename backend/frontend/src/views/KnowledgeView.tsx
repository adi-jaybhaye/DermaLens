import React, { useEffect, useState } from 'react';
import { api, type ConcernKnowledge } from '../api/client';
import { BookOpenIcon, ExternalLinkIcon, ShieldCheckIcon } from '../components/Icons';

export const KnowledgeView: React.FC = () => {
  const [concerns, setConcerns] = useState<ConcernKnowledge[]>([]);
  const [selectedConcept, setSelectedConcept] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getKnowledge()
      .then((data) => {
        setConcerns(data);
        if (data.length > 0) setSelectedConcept(data[0].concept);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const activeConcern = concerns.find((c) => c.concept === selectedConcept);

  return (
    <div style={{ maxWidth: 1140, margin: '0 auto', padding: '40px 20px 80px' }}>
      <div style={{ textAlign: 'center', marginBottom: 36 }}>
        <div className="pill-badge pill-terracotta" style={{ marginBottom: 12 }}>
          <BookOpenIcon size={14} /> Curated Medical Literature
        </div>
        <h2 style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>
          Skin Concern Knowledge Base
        </h2>
        <p style={{ fontSize: 15, color: 'var(--color-muted)', maxWidth: 640, margin: '0 auto' }}>
          Explore evidence-based summaries for each of the 8 concern classes recognized by our EfficientNet-B0 visual classifier.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}>Loading curated dermatological knowledge...</div>
      ) : (
        <div className="knowledge-grid">
          {/* Sidebar Concern List / Mobile Scrollable Chips */}
          <div className="knowledge-selector-list" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {concerns.map((c) => {
              const isSelected = c.concept === selectedConcept;
              return (
                <button
                  key={c.concept}
                  onClick={() => setSelectedConcept(c.concept)}
                  className="knowledge-selector-btn"
                  style={{
                    padding: '14px 18px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: isSelected ? 'var(--color-terracotta)' : 'var(--color-surface)',
                    color: isSelected ? '#FFFFFF' : 'var(--color-charcoal)',
                    border: `1px solid ${isSelected ? 'var(--color-terracotta)' : 'var(--color-border)'}`,
                    textAlign: 'left',
                    fontWeight: 600,
                    fontSize: 14,
                    boxShadow: isSelected ? '0 4px 12px rgba(200, 109, 81, 0.25)' : 'var(--shadow-sm)',
                    transition: 'all var(--transition-fast)',
                  }}
                >
                  {c.display_name}
                </button>
              );
            })}
          </div>

          {/* Detailed Concern Card */}
          {activeConcern && (
            <div className="glass-panel" style={{ padding: '34px 32px', backgroundColor: '#FFFFFF', minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <h3 style={{ fontSize: 26, fontWeight: 700 }}>
                  {activeConcern.display_name}
                </h3>
                <span className="pill-badge pill-sage" style={{ fontSize: 11 }}>
                  Dataset A Class
                </span>
              </div>

              <p style={{ fontSize: 15, color: 'var(--color-mocha)', lineHeight: 1.6, marginBottom: 24 }}>
                {activeConcern.description}
              </p>

              {/* Scientific Mechanism */}
              <div style={{
                padding: '20px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1px solid var(--color-border-light)',
                marginBottom: 24,
              }}>
                <h5 style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-terracotta-dark)', marginBottom: 6 }}>
                  Why This Visible Pattern Can Occur Scientifically
                </h5>
                <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.6 }}>
                  {activeConcern.why_it_can_occur}
                </p>
              </div>

              {/* Contributing factors */}
              <div style={{ marginBottom: 24 }}>
                <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 10 }}>
                  Common Contributing Factors
                </h5>
                <ul style={{ paddingLeft: 20, fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.7 }}>
                  {activeConcern.common_contributing_factors.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>

              {/* When to consult */}
              <div style={{
                padding: '16px 20px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-warning-bg)',
                border: '1px solid var(--color-warning-border)',
                marginBottom: 24,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <ShieldCheckIcon size={18} color="var(--color-warning-text)" />
                  <h6 style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--color-warning-text)' }}>
                    When to Consult a Dermatologist
                  </h6>
                </div>
                <p style={{ fontSize: 13, color: 'var(--color-warning-text)', lineHeight: 1.55 }}>
                  {activeConcern.when_to_consult}
                </p>
              </div>

              {/* Evidence references */}
              <div>
                <h5 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.6px', color: 'var(--color-muted)', marginBottom: 10 }}>
                  Curated Clinical Evidence Sources
                </h5>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                  {activeConcern.evidence_references.map((ref, idx) => (
                    <a
                      key={idx}
                      href={ref.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        padding: '6px 14px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: 'var(--color-blush)',
                        color: 'var(--color-terracotta-dark)',
                        fontSize: 12,
                        fontWeight: 600,
                      }}
                    >
                      <span>{ref.title} ({ref.source})</span>
                      <ExternalLinkIcon size={12} />
                    </a>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
