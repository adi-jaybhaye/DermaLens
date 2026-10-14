import React, { useEffect, useState, useMemo } from 'react';
import { api, type ConcernKnowledge } from '../api/client';
import { BookOpenIcon, ExternalLinkIcon, ShieldCheckIcon, SearchIcon, XIcon } from '../components/Icons';

export const KnowledgeView: React.FC = () => {
  const [concerns, setConcerns] = useState<ConcernKnowledge[]>([]);
  const [selectedConcept, setSelectedConcept] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
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

  const filteredConcerns = useMemo(() => {
    if (!searchQuery.trim()) return concerns;
    const q = searchQuery.toLowerCase();
    return concerns.filter(
      (c) =>
        c.display_name.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q) ||
        c.why_it_can_occur.toLowerCase().includes(q)
    );
  }, [concerns, searchQuery]);

  // Keep selected concept valid when filtering
  useEffect(() => {
    if (filteredConcerns.length > 0) {
      if (!filteredConcerns.some((c) => c.concept === selectedConcept)) {
        setSelectedConcept(filteredConcerns[0].concept);
      }
    }
  }, [filteredConcerns, selectedConcept]);

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
          Explore evidence-based dermatological summaries for each of the 8 facial skin characteristics evaluated by DermaLens.
        </p>

        {/* Search Bar */}
        <div style={{
          maxWidth: 440,
          margin: '22px auto 0',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '8px 16px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-sm)',
        }}>
          <SearchIcon size={16} color="var(--color-muted)" />
          <input
            type="text"
            placeholder="Search skin concerns or characteristics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              border: 'none',
              outline: 'none',
              width: '100%',
              fontSize: 13.5,
              fontFamily: 'var(--font-body)',
              color: 'var(--color-charcoal)',
              backgroundColor: 'transparent',
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-muted)', padding: 4 }}
              aria-label="Clear search"
            >
              <XIcon size={14} />
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(220px, 300px) 1fr',
          gap: 24,
          opacity: 0.7,
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div key={n} style={{ height: 48, borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-sand)' }} />
            ))}
          </div>
          <div style={{ height: 420, borderRadius: 'var(--radius-lg)', backgroundColor: 'var(--color-sand)' }} />
        </div>
      ) : (
        <div className="knowledge-grid">
          {/* Sidebar Concern List */}
          <div className="knowledge-selector-list" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {filteredConcerns.map((c) => {
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
                    border: `1.5px solid ${isSelected ? 'var(--color-terracotta)' : 'var(--color-border)'}`,
                    textAlign: 'left',
                    fontWeight: 600,
                    fontSize: 14,
                    boxShadow: isSelected ? '0 4px 12px rgba(200, 109, 81, 0.25)' : 'var(--shadow-sm)',
                    transition: 'all var(--transition-fast)',
                    cursor: 'pointer',
                  }}
                >
                  {c.display_name}
                </button>
              );
            })}

            {filteredConcerns.length === 0 && (
              <div style={{ padding: 18, fontSize: 13, color: 'var(--color-muted)', textAlign: 'center' }}>
                No concerns match "{searchQuery}".
              </div>
            )}
          </div>

          {/* Detailed Concern Card */}
          {activeConcern && (
            <div className="glass-panel" style={{ padding: '34px 32px', backgroundColor: '#FFFFFF', minWidth: 0, boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
                <h3 style={{ fontSize: 26, fontWeight: 700, color: 'var(--color-charcoal)' }}>
                  {activeConcern.display_name}
                </h3>
                <span className="pill-badge pill-sage" style={{ fontSize: 11.5 }}>
                  Evaluated Facial Characteristic
                </span>
              </div>

              <p style={{ fontSize: 15, color: 'var(--color-mocha)', lineHeight: 1.6, marginBottom: 22 }}>
                {activeConcern.description}
              </p>

              {/* Visual Characteristics */}
              {activeConcern.visual_characteristics && activeConcern.visual_characteristics.length > 0 && (
                <div style={{ marginBottom: 22 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-muted)', letterSpacing: '0.5px', marginBottom: 8 }}>
                    Observable Visual Characteristics
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {activeConcern.visual_characteristics.map((vc, i) => (
                      <span
                        key={i}
                        style={{
                          padding: '4px 12px',
                          borderRadius: 'var(--radius-full)',
                          backgroundColor: 'var(--color-blush)',
                          color: 'var(--color-terracotta-dark)',
                          fontSize: 12.5,
                          fontWeight: 600,
                        }}
                      >
                        &bull; {vc}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Scientific Mechanism */}
              <div style={{
                padding: '20px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1px solid var(--color-border-light)',
                marginBottom: 24,
              }}>
                <h5 style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--color-terracotta-dark)', marginBottom: 6 }}>
                  Why This Visible Pattern Can Occur Scientifically
                </h5>
                <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.6 }}>
                  {activeConcern.why_it_can_occur}
                </p>
              </div>

              {/* Contributing Factors */}
              {activeConcern.common_contributing_factors && activeConcern.common_contributing_factors.length > 0 && (
                <div style={{ marginBottom: 24 }}>
                  <h5 style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: 'var(--color-charcoal)' }}>
                    Common Contributing Factors
                  </h5>
                  <ul style={{ paddingLeft: 20, fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.65 }}>
                    {activeConcern.common_contributing_factors.map((f, i) => (
                      <li key={i} style={{ marginBottom: 3 }}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* When to consult a professional */}
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
              {activeConcern.evidence_references && activeConcern.evidence_references.length > 0 && (
                <div>
                  <h5 style={{ fontSize: 12.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.6px', color: 'var(--color-muted)', marginBottom: 10 }}>
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
                          backgroundColor: 'var(--color-surface-subtle)',
                          border: '1px solid var(--color-border)',
                          color: 'var(--color-charcoal)',
                          fontSize: 12,
                          fontWeight: 600,
                          transition: 'border-color var(--transition-fast)',
                        }}
                      >
                        <span>{ref.title} ({ref.source})</span>
                        <ExternalLinkIcon size={12} color="var(--color-terracotta)" />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
