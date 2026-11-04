import React, { useEffect, useState } from 'react';
import { api, type SourceItem } from '../api/client';
import { ShieldCheckIcon, ExternalLinkIcon } from '../components/Icons';

export const SourcesView: React.FC = () => {
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSources()
      .then(setSources)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '40px 20px 80px' }}>
      <div style={{ textAlign: 'center', marginBottom: 36 }}>
        <div className="pill-badge pill-terracotta" style={{ marginBottom: 12 }}>
          <ShieldCheckIcon size={14} /> Authoritative Scientific Literature
        </div>
        <h2 style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>
          Evidence &amp; Clinical Sources
        </h2>
        <p style={{ fontSize: 15, color: 'var(--color-muted)', maxWidth: 640, margin: '0 auto' }}>
          All physiological explanations in DermaLens are curated directly from peer-reviewed dermatological bodies and clinical manuals.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}>Loading references...</div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 280px), 1fr))',
          gap: 18,
        }}>
          {sources.map((src) => (
            <div
              key={src.id}
              className="glass-panel"
              style={{
                padding: '24px 22px',
                backgroundColor: '#FFFFFF',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{
                  fontSize: 11,
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.6px',
                  color: 'var(--color-terracotta)',
                  marginBottom: 6,
                }}>
                  {src.source}
                </div>
                <h4 style={{ fontSize: 17, fontWeight: 700, marginBottom: 10, lineHeight: 1.35 }}>
                  {src.title}
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
                  {src.related_concerns.map((c, i) => (
                    <span
                      key={i}
                      style={{
                        fontSize: 11,
                        padding: '3px 10px',
                        borderRadius: 'var(--radius-full)',
                        backgroundColor: 'var(--color-sand)',
                        color: 'var(--color-mocha)',
                      }}
                    >
                      {c}
                    </span>
                  ))}
                </div>
              </div>

              <a
                href={src.url}
                target="_blank"
                rel="noreferrer"
                className="btn-secondary"
                style={{
                  fontSize: 12,
                  padding: '8px 16px',
                  justifyContent: 'center',
                }}
              >
                <span>Read Publication</span>
                <ExternalLinkIcon size={13} />
              </a>
            </div>
          ))}
        </div>
      )}

      {/* Evidence-Based Methodology Statement (Eliminates bottom dead space) */}
      <div
        className="glass-panel"
        style={{
          marginTop: 40,
          padding: '24px 28px',
          backgroundColor: '#FFFFFF',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          flexWrap: 'wrap',
        }}
      >
        <div style={{ color: 'var(--color-sage-dark)', flexShrink: 0 }}>
          <ShieldCheckIcon size={26} />
        </div>
        <div style={{ flex: 1, minWidth: 260 }}>
          <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-charcoal)', marginBottom: 4 }}>
            Evidence Mapping Methodology
          </h4>
          <p style={{ fontSize: 13, color: 'var(--color-muted)', margin: 0, lineHeight: 1.55 }}>
            DermaLens visual algorithms map visible pixel clusters and surface texture features to published dermatological literature. These publications provide physiological context on why surface features manifest, strictly avoiding diagnostic claims.
          </p>
        </div>
      </div>
    </div>
  );
};
