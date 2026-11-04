import React, { useState } from 'react';
import type { User } from '../api/client';
import { 
  ChevronRightIcon, 
  BookOpenIcon, 
  InfoIcon, 
  ShieldCheckIcon,
  MenuIcon,
  XIcon,
  UserIcon,
  SparklesIcon,
  CameraIcon,
  EyeIcon,
} from '../components/Icons';

interface CoverViewProps {
  onStartAssessment: () => void;
  onExploreKnowledge: () => void;
  onViewSources?: () => void;
  onOpenAuth: () => void;
  user: User | null;
  onLogout?: () => void;
}

/* ============================================================
   1. COVER NAVBAR COMPONENT (Loop 3, Loop 25)
   Seamless, transparent header matching reference layout:
   - Left: Monogram Elegance Logo + "DermaLens"
   - Right: About, Knowledge, Sign In + [Start Assessment →]
   - Mobile: Responsive compact layout with hamburger drawer
   ============================================================ */
export const CoverNavbar: React.FC<{
  onStartAssessment: () => void;
  onExploreKnowledge: () => void;
  onOpenAbout: () => void;
  onOpenAuth: () => void;
  user: User | null;
  onLogout?: () => void;
}> = ({
  onStartAssessment,
  onExploreKnowledge,
  onOpenAbout,
  onOpenAuth,
  user,
  onLogout,
}) => {
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="cover-navbar" style={{
      width: '100%',
      padding: '28px 48px',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      zIndex: 30,
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
      }}>
        {/* Brand: Monogram Elegance + Wordmark */}
        <div 
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            cursor: 'pointer',
            textDecoration: 'none',
          }}
        >
          <div style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            backgroundColor: '#BD725C',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 6,
            boxShadow: '0 2px 8px rgba(189, 114, 92, 0.28)',
            flexShrink: 0,
          }}>
            <img 
              src="/brand/logo/dermalens-monogram-small.svg" 
              alt="DermaLens" 
              style={{ 
                width: '100%', 
                height: '100%', 
                objectFit: 'contain',
                filter: 'brightness(0) invert(1)' 
              }}
            />
          </div>
          <div style={{
            fontFamily: "'Cormorant Garamond', 'Playfair Display', Georgia, serif",
            fontSize: 23,
            fontWeight: 700,
            letterSpacing: '-0.3px',
            color: '#2F2A27',
            lineHeight: 1,
          }}>
            Derma<span style={{ color: '#BD725C' }}>Lens</span>
          </div>
        </div>

        {/* Desktop Navigation Group: About, Knowledge, Sign In, CTA */}
        <nav className="cover-desktop-nav" style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'clamp(16px, 2.5vw, 32px)',
        }}>
          <button
            onClick={onOpenAbout}
            style={{
              background: 'transparent',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 14.5,
              fontWeight: 500,
              color: '#4A423D',
              cursor: 'pointer',
              padding: '6px 4px',
              transition: 'color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#BD725C')}
            onMouseLeave={(e) => (e.currentTarget.style.color = '#4A423D')}
          >
            About
          </button>

          <button
            onClick={onExploreKnowledge}
            style={{
              background: 'transparent',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 14.5,
              fontWeight: 500,
              color: '#4A423D',
              cursor: 'pointer',
              padding: '6px 4px',
              transition: 'color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#BD725C')}
            onMouseLeave={(e) => (e.currentTarget.style.color = '#4A423D')}
          >
            Knowledge
          </button>

          {user ? (
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                style={{
                  background: 'rgba(255, 255, 255, 0.7)',
                  border: '1px solid rgba(220, 210, 198, 0.8)',
                  borderRadius: 9999,
                  padding: '6px 14px',
                  fontFamily: 'var(--font-body)',
                  fontSize: 13.5,
                  fontWeight: 600,
                  color: '#2F2A27',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <UserIcon size={14} color="#BD725C" />
                <span>{user.full_name || user.email.split('@')[0]}</span>
              </button>
              {userDropdownOpen && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: 8,
                  backgroundColor: '#FFFFFF',
                  borderRadius: 12,
                  boxShadow: '0 8px 24px rgba(47, 42, 39, 0.12)',
                  border: '1px solid #EAE0D5',
                  padding: '6px',
                  minWidth: 140,
                  zIndex: 40,
                }}>
                  <button
                    onClick={() => {
                      setUserDropdownOpen(false);
                      onLogout?.();
                    }}
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      background: 'transparent',
                      border: 'none',
                      padding: '8px 12px',
                      fontSize: 13,
                      color: '#BD725C',
                      fontWeight: 600,
                      cursor: 'pointer',
                      borderRadius: 6,
                    }}
                  >
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              style={{
                background: 'transparent',
                border: 'none',
                fontFamily: 'var(--font-body)',
                fontSize: 14.5,
                fontWeight: 500,
                color: '#4A423D',
                cursor: 'pointer',
                padding: '6px 4px',
                transition: 'color 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = '#BD725C')}
              onMouseLeave={(e) => (e.currentTarget.style.color = '#4A423D')}
            >
              Sign In
            </button>
          )}

          {/* Small Top-Right CTA Pill Button */}
          <button
            onClick={onStartAssessment}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '9px 18px',
              borderRadius: 9999,
              backgroundColor: '#BD725C',
              color: '#FFFFFF',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 13.5,
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background-color 0.15s ease',
              boxShadow: '0 4px 14px rgba(189, 114, 92, 0.22)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#A85E49')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#BD725C')}
          >
            <span>Start Assessment</span>
            <ChevronRightIcon size={14} />
          </button>
        </nav>

        {/* Mobile Navigation Controls */}
        <div className="cover-mobile-nav" style={{ display: 'none', alignItems: 'center', gap: 10 }}>
          <button
            onClick={onStartAssessment}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
              padding: '7px 14px',
              borderRadius: 9999,
              backgroundColor: '#BD725C',
              color: '#FFFFFF',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 12.5,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <span>Start</span>
            <ChevronRightIcon size={13} />
          </button>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle Navigation Menu"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 38,
              height: 38,
              borderRadius: '50%',
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              border: '1px solid rgba(220, 210, 198, 0.8)',
              color: '#2F2A27',
              cursor: 'pointer',
            }}
          >
            {mobileMenuOpen ? <XIcon size={20} /> : <MenuIcon size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown Menu Drawer */}
      {mobileMenuOpen && (
        <div style={{
          marginTop: 14,
          backgroundColor: '#FFFFFF',
          borderRadius: 16,
          boxShadow: '0 12px 32px rgba(47, 42, 39, 0.15)',
          border: '1px solid #EAE0D5',
          padding: '12px',
          display: 'flex',
          flexDirection: 'column',
          gap: 6,
          animation: 'fadeIn 0.2s ease-out',
        }}>
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenAbout();
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '10px 14px',
              borderRadius: 10,
              background: 'transparent',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 14,
              fontWeight: 500,
              color: '#2F2A27',
              textAlign: 'left',
              cursor: 'pointer',
            }}
          >
            <InfoIcon size={16} color="#BD725C" />
            <span>About DermaLens</span>
          </button>

          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onExploreKnowledge();
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '10px 14px',
              borderRadius: 10,
              background: 'transparent',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 14,
              fontWeight: 500,
              color: '#2F2A27',
              textAlign: 'left',
              cursor: 'pointer',
            }}
          >
            <BookOpenIcon size={16} color="#BD725C" />
            <span>Knowledge Base</span>
          </button>

          <div style={{ height: 1, backgroundColor: '#EAE0D5', margin: '4px 0' }} />

          {user ? (
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onLogout?.();
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 14px',
                borderRadius: 10,
                background: 'transparent',
                border: 'none',
                fontFamily: 'var(--font-body)',
                fontSize: 14,
                fontWeight: 600,
                color: '#BD725C',
                textAlign: 'left',
                cursor: 'pointer',
              }}
            >
              <UserIcon size={16} color="#BD725C" />
              <span>Sign Out ({user.full_name || user.email.split('@')[0]})</span>
            </button>
          ) : (
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenAuth();
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 14px',
                borderRadius: 10,
                background: 'transparent',
                border: 'none',
                fontFamily: 'var(--font-body)',
                fontSize: 14,
                fontWeight: 600,
                color: '#2F2A27',
                textAlign: 'left',
                cursor: 'pointer',
              }}
            >
              <UserIcon size={16} color="#BD725C" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      )}
    </header>
  );
};

/* ============================================================
   2. COVER COPY COMPONENT (Loop 4, Loop 5, Loop 6, Loop 11)
   Left-hand editorial content:
   - Eyebrow: INSIGHTS GROW WITH KNOWLEDGE
   - Headline: Understand what your skin reveals.
   - Supporting copy: AI-assisted visual analysis...
   - Primary dominant CTA button: Start Assessment →
   ============================================================ */
export const CoverCopy: React.FC<{
  onStartAssessment: () => void;
}> = ({ onStartAssessment }) => {
  return (
    <div className="cover-copy-container" style={{
      maxWidth: 620,
      position: 'relative',
      zIndex: 10,
    }}>
      {/* Uppercase Eyebrow (Clean, unboxed, matching reference) */}
      <div 
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: 12.5,
          fontWeight: 600,
          letterSpacing: '2.4px',
          textTransform: 'uppercase',
          color: '#8D7B6D',
          marginBottom: 20,
        }}
      >
        INSIGHTS GROW WITH KNOWLEDGE
      </div>

      {/* Main Editorial Headline (Exact wording & line breaks from reference) */}
      <h1 
        style={{
          fontFamily: "'Cormorant Garamond', 'Playfair Display', Georgia, serif",
          fontSize: 'clamp(40px, 4.6vw, 62px)',
          fontWeight: 700,
          lineHeight: 1.1,
          letterSpacing: '-0.8px',
          color: '#2F2A27',
          margin: '0 0 22px 0',
        }}
      >
        Understand<br />
        <span className="cover-headline-line2">what your skin reveals.</span>
      </h1>

      {/* Supporting Paragraph (Exact wording from reference) */}
      <p 
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: 'clamp(15px, 1.25vw, 17px)',
          lineHeight: 1.62,
          color: '#5A524C',
          margin: '0 0 34px 0',
          maxWidth: 460,
        }}
      >
        AI-assisted visual analysis with explainable<br />
        results and trusted information.
      </p>

      {/* Primary Dominant CTA Button (Loop 11) */}
      <div>
        <button
          onClick={onStartAssessment}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 10,
            padding: '15px 36px',
            borderRadius: 9999,
            backgroundColor: '#BD725C',
            color: '#FFFFFF',
            border: 'none',
            fontFamily: 'var(--font-body)',
            fontSize: 16,
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: '0 8px 26px rgba(189, 114, 92, 0.32)',
            transition: 'background-color 0.2s ease, box-shadow 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#A85E49';
            e.currentTarget.style.boxShadow = '0 12px 30px rgba(189, 114, 92, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#BD725C';
            e.currentTarget.style.boxShadow = '0 8px 26px rgba(189, 114, 92, 0.32)';
          }}
        >
          <span>Start Assessment</span>
          <ChevronRightIcon size={18} />
        </button>
      </div>

      {/* Editorial Protocol & Capabilities Strip */}
      <div className="cover-trust-group" style={{
        marginTop: 32,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          flexWrap: 'wrap',
        }}>
          <span className="cover-trust-tag">
            <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#556E58' }} />
            3-Perspective Capture
          </span>
          <span className="cover-trust-tag">
            <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#BD725C' }} />
            5-Zone Facial Mapping
          </span>
          <span className="cover-trust-tag">
            <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#556E58' }} />
            Explainable AI Insights
          </span>
        </div>

        <div style={{
          fontSize: 12.5,
          color: '#8A7E74',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          fontFamily: 'var(--font-body)',
        }}>
          <span>✦ Non-diagnostic wellness assessment &bull; Peer-reviewed dermatological grounding</span>
        </div>
      </div>
    </div>
  );
};

/* ============================================================
   3. COVER FEATURE TEXT COMPONENT (Loop 12)
   Bottom-right restrained microcopy matching reference:
   VISIBLE PATTERNS
   CLEAR INSIGHTS
   BETTER UNDERSTANDING
   ============================================================ */
export const CoverFeatureText: React.FC = () => {
  return (
    <div className="cover-feature-text" style={{
      position: 'absolute',
      right: 48,
      bottom: 40,
      textAlign: 'right',
      fontFamily: 'var(--font-body)',
      fontSize: 12,
      fontWeight: 600,
      letterSpacing: '2.4px',
      lineHeight: 2.2,
      color: '#6F7A6E',
      textTransform: 'uppercase',
      zIndex: 10,
      userSelect: 'none',
    }}>
      <div>VISIBLE PATTERNS</div>
      <div>CLEAR INSIGHTS</div>
      <div>BETTER UNDERSTANDING</div>
    </div>
  );
};

/* ============================================================
   3B. COVER DISCOVERY & OVERVIEW SECTION
   Eliminates "no-element spaces" below the hero fold.
   Provides rich, beautiful, editorial guidance on how DermaLens works.
   ============================================================ */
export const CoverDiscoverySection: React.FC<{
  onStartAssessment: () => void;
  onExploreKnowledge: () => void;
}> = ({ onStartAssessment, onExploreKnowledge }) => {
  const steps = [
    {
      num: '01',
      title: 'Optimal Preparation',
      desc: 'Position facing soft, even natural light with a cleansed, makeup-free skin surface and relaxed expression.',
      icon: <SparklesIcon size={22} color="#556E58" />,
    },
    {
      num: '02',
      title: '3-Perspective Multi-View',
      desc: 'Capture 3 distinct angles: Frontal direct gaze, Left profile (45°), and Right profile (45°) for complete contour coverage.',
      icon: <CameraIcon size={22} color="#BD725C" />,
    },
    {
      num: '03',
      title: 'Explainable AI Analysis',
      desc: '468 facial landmark mesh isolates 5 anatomical zones with interactive focus heatmaps grounded in peer-reviewed dermatology.',
      icon: <EyeIcon size={22} color="#556E58" />,
    },
  ];

  const evaluatedConcerns = [
    { name: 'Redness (Erythema)', tag: 'Vascular' },
    { name: 'Dark Spots', tag: 'Melanin' },
    { name: 'Inflammatory Acne', tag: 'Lesions' },
    { name: 'Blackheads', tag: 'Open Comedones' },
    { name: 'Whiteheads', tag: 'Closed Comedones' },
    { name: 'Pigmentation', tag: 'Evenness' },
    { name: 'Enlarged Pores', tag: 'Texture' },
    { name: 'Fine Lines', tag: 'Structural' },
  ];

  return (
    <section className="cover-discovery-section" style={{
      backgroundColor: '#FAF7F2',
      borderTop: '1px solid #EAE0D5',
      padding: '70px 24px 60px',
      position: 'relative',
      zIndex: 10,
    }}>
      <div style={{ maxWidth: 1160, margin: '0 auto' }}>
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: 50 }}>
          <div style={{
            fontFamily: 'var(--font-body)',
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: '2.2px',
            textTransform: 'uppercase',
            color: '#8D7B6D',
            marginBottom: 10,
          }}>
            SYSTEM METHODOLOGY
          </div>
          <h2 style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: 'clamp(28px, 3.8vw, 44px)',
            fontWeight: 700,
            color: '#2F2A27',
            margin: '0 0 14px 0',
            lineHeight: 1.15,
          }}>
            How DermaLens Evaluates Visible Skin Patterns
          </h2>
          <p style={{
            fontFamily: 'var(--font-body)',
            fontSize: 15.5,
            color: '#6A625B',
            maxWidth: 600,
            margin: '0 auto',
            lineHeight: 1.6,
          }}>
            A non-invasive, privacy-first computer vision pipeline combining high-resolution landmarking with explainable AI focus heatmaps.
          </p>
        </div>

        {/* 3 Step Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 300px), 1fr))',
          gap: 24,
          marginBottom: 60,
        }}>
          {steps.map((s, idx) => (
            <div key={idx} style={{
              backgroundColor: '#FFFFFF',
              borderRadius: 20,
              padding: '32px 28px',
              border: '1.5px solid #EAE0D5',
              boxShadow: '0 6px 20px rgba(47, 42, 39, 0.04)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                  <div style={{
                    width: 46,
                    height: 46,
                    borderRadius: 14,
                    backgroundColor: '#F5EFE6',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    {s.icon}
                  </div>
                  <span style={{
                    fontFamily: "'Cormorant Garamond', Georgia, serif",
                    fontSize: 28,
                    fontWeight: 700,
                    color: '#CBBBAE',
                  }}>
                    {s.num}
                  </span>
                </div>
                <h3 style={{
                  fontFamily: "'Cormorant Garamond', Georgia, serif",
                  fontSize: 22,
                  fontWeight: 700,
                  color: '#2F2A27',
                  marginBottom: 10,
                }}>
                  {s.title}
                </h3>
                <p style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: 14,
                  lineHeight: 1.6,
                  color: '#6A625B',
                  margin: 0,
                }}>
                  {s.desc}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* 8 Characteristics Bar */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: 24,
          padding: '36px 32px',
          border: '1.5px solid #EAE0D5',
          boxShadow: '0 8px 24px rgba(47, 42, 39, 0.04)',
          marginBottom: 60,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 16,
            marginBottom: 24,
          }}>
            <div>
              <div style={{
                fontFamily: 'var(--font-body)',
                fontSize: 11.5,
                fontWeight: 700,
                letterSpacing: '1.8px',
                textTransform: 'uppercase',
                color: '#8D7B6D',
                marginBottom: 4,
              }}>
                EVALUATION MATRIX
              </div>
              <h3 style={{
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: 26,
                fontWeight: 700,
                color: '#2F2A27',
                margin: 0,
              }}>
                8 Evaluated Visible Skin Characteristics
              </h3>
            </div>

            <button
              onClick={onExploreKnowledge}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                padding: '9px 18px',
                borderRadius: 9999,
                backgroundColor: 'transparent',
                border: '1px solid #BD725C',
                color: '#BD725C',
                fontFamily: 'var(--font-body)',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <BookOpenIcon size={15} />
              <span>Explore Knowledge Base</span>
            </button>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))',
            gap: 12,
          }}>
            {evaluatedConcerns.map((c, i) => (
              <div key={i} style={{
                padding: '12px 16px',
                borderRadius: 14,
                backgroundColor: '#FAF7F2',
                border: '1px solid #ECE3D7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}>
                <span style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: 13.5,
                  fontWeight: 600,
                  color: '#3A332F',
                }}>
                  {c.name}
                </span>
                <span style={{
                  fontSize: 11,
                  fontWeight: 600,
                  color: '#8D7B6D',
                  backgroundColor: '#EFE8DE',
                  padding: '2px 8px',
                  borderRadius: 9999,
                }}>
                  {c.tag}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Clinical Disclaimer & Quick Start Banner */}
        <div style={{
          backgroundColor: '#EFF3EF',
          borderRadius: 20,
          padding: '24px 28px',
          border: '1px solid #D2DED4',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 20,
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, maxWidth: 680 }}>
            <div style={{ color: '#556E58', flexShrink: 0, marginTop: 2 }}>
              <ShieldCheckIcon size={24} />
            </div>
            <div>
              <h4 style={{ fontSize: 15, fontWeight: 700, color: '#2F3D31', margin: '0 0 4px 0' }}>
                Wellness &amp; Educational Notice
              </h4>
              <p style={{ fontSize: 13, color: '#4B5E4F', margin: 0, lineHeight: 1.55 }}>
                DermaLens is an informational educational tool grounded in dermatological literature from Mayo Clinic, AAD, and DermNet NZ. It does not provide medical diagnoses or replace clinical consultations.
              </p>
            </div>
          </div>

          <button
            onClick={onStartAssessment}
            style={{
              padding: '12px 28px',
              borderRadius: 9999,
              backgroundColor: '#BD725C',
              color: '#FFFFFF',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 14.5,
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(189, 114, 92, 0.28)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <span>Start Assessment</span>
            <ChevronRightIcon size={16} />
          </button>
        </div>

        {/* Minimal Footer */}
        <div style={{
          textAlign: 'center',
          marginTop: 50,
          paddingTop: 24,
          borderTop: '1px solid #EAE0D5',
          fontFamily: 'var(--font-body)',
          fontSize: 12.5,
          color: '#9E9287',
        }}>
          DermaLens &bull; Advanced Facial Skin Assessment Platform &bull; Privacy-First &bull; 2026
        </div>
      </div>
    </section>
  );
};

/* ============================================================
   4. ABOUT INFORMATION MODAL
   Clean, quiet educational overlay triggered by the About link.
   ============================================================ */
const AboutModal: React.FC<{ isOpen: boolean; onClose: () => void; onExploreKnowledge: () => void }> = ({
  isOpen,
  onClose,
  onExploreKnowledge,
}) => {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(47, 42, 39, 0.45)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: 20,
    }} onClick={onClose}>
      <div 
        style={{
          backgroundColor: '#FAF7F2',
          borderRadius: 24,
          padding: '36px 32px',
          maxWidth: 520,
          width: '100%',
          boxShadow: '0 20px 40px rgba(47, 42, 39, 0.16)',
          border: '1px solid #EAE0D5',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            backgroundColor: '#FAF1ED',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <InfoIcon size={18} color="#BD725C" />
          </div>
          <h2 style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: 26,
            fontWeight: 700,
            margin: 0,
            color: '#2F2A27',
          }}>
            About DermaLens
          </h2>
        </div>

        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: 14.5,
          lineHeight: 1.65,
          color: '#5A524C',
          margin: '0 0 16px 0',
        }}>
          DermaLens is an intelligent facial skin wellness assessment platform. Using multi-angle computer vision and explainable AI algorithms, it analyzes visible patterns such as skin hydration, oil distribution, redness, and textural harmony.
        </p>

        <p style={{
          fontFamily: 'var(--font-body)',
          fontSize: 13,
          lineHeight: 1.6,
          color: '#7A726A',
          backgroundColor: '#EFF3EF',
          padding: '12px 16px',
          borderRadius: 12,
          margin: '0 0 24px 0',
        }}>
          <ShieldCheckIcon size={14} color="#556E58" style={{ display: 'inline', marginRight: 6 }} />
          <strong>Wellness Notice:</strong> DermaLens is an informational educational tool, not a medical device or clinical diagnostic replacement.
        </p>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button
            onClick={() => {
              onClose();
              onExploreKnowledge();
            }}
            style={{
              padding: '10px 18px',
              borderRadius: 9999,
              backgroundColor: 'transparent',
              border: '1px solid #D5C8B8',
              fontFamily: 'var(--font-body)',
              fontSize: 13.5,
              fontWeight: 600,
              color: '#4A423D',
              cursor: 'pointer',
            }}
          >
            Explore Knowledge Base
          </button>
          <button
            onClick={onClose}
            style={{
              padding: '10px 22px',
              borderRadius: 9999,
              backgroundColor: '#BD725C',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: 13.5,
              fontWeight: 600,
              color: '#FFFFFF',
              cursor: 'pointer',
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

/* ============================================================
   5. MAIN COVER VIEW (Loop 2, Loop 25)
   Full-screen static hero orchestrator matching the exact reference.
   ============================================================ */
export const CoverView: React.FC<CoverViewProps> = ({
  onStartAssessment,
  onExploreKnowledge,
  onOpenAuth,
  user,
  onLogout,
}) => {
  const [aboutOpen, setAboutOpen] = useState(false);

  return (
    <div 
      className="cover-page-root"
      style={{
        width: '100%',
        minHeight: '100vh',
        backgroundColor: '#F7F4ED',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        overflowX: 'hidden',
        overflowY: 'auto',
      }}
    >
      {/* 1. Hero Fold: 100vh Reference Accurate Hero */}
      <div 
        className="cover-hero-fold"
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          position: 'relative',
          width: '100%',
        }}
      >
        {/* Seamless Reference Top Navigation */}
        <CoverNavbar
          onStartAssessment={onStartAssessment}
          onExploreKnowledge={onExploreKnowledge}
          onOpenAbout={() => setAboutOpen(true)}
          onOpenAuth={onOpenAuth}
          user={user}
          onLogout={onLogout}
        />

        {/* Main Hero Area */}
        <main 
          className="cover-hero-main"
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            padding: '0 48px',
            maxWidth: 1400,
            width: '100%',
            margin: '0 auto',
            position: 'relative',
          }}
        >
          <CoverCopy onStartAssessment={onStartAssessment} />
        </main>

        {/* Bottom-Right Reference Microcopy */}
        <CoverFeatureText />
      </div>

      {/* 2. Below-the-Fold Overview & Science Section (Eliminates dead space) */}
      <CoverDiscoverySection
        onStartAssessment={onStartAssessment}
        onExploreKnowledge={onExploreKnowledge}
      />

      {/* 3. Educational Informational Modal */}
      <AboutModal
        isOpen={aboutOpen}
        onClose={() => setAboutOpen(false)}
        onExploreKnowledge={onExploreKnowledge}
      />
    </div>
  );
};
