import React, { useState, useRef, useEffect } from 'react';
import type { User } from '../api/client';
import {
  SparklesIcon,
  UserIcon,
  BookOpenIcon,
  ShieldCheckIcon,
  MenuIcon,
  XIcon,
  ChevronDownIcon,
  CalendarIcon,
} from './Icons';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  user: User | null;
  onOpenAuth: () => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  user,
  onOpenAuth,
  onLogout,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [accountModalOpen, setAccountModalOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setProfileDropdownOpen(false);
      }
    };
    if (profileDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [profileDropdownOpen]);

  // Close dropdown on ESC
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setProfileDropdownOpen(false);
        setAccountModalOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleNavClick = (tab: string) => {
    setCurrentTab(tab);
    setMobileMenuOpen(false);
    setProfileDropdownOpen(false);
  };

  const handleAuthClick = () => {
    onOpenAuth();
    setMobileMenuOpen(false);
  };

  const handleLogoutClick = () => {
    onLogout();
    setMobileMenuOpen(false);
    setProfileDropdownOpen(false);
  };

  return (
    <header className="nav-header">
      <div className="nav-container">
        {/* Brand */}
        <div
          onClick={() => handleNavClick('home')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            cursor: 'pointer',
          }}
        >
          <div style={{
            width: 36,
            height: 36,
            borderRadius: 12,
            background: 'linear-gradient(135deg, var(--color-terracotta) 0%, #E28C73 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            boxShadow: '0 4px 12px rgba(200, 109, 81, 0.25)',
            flexShrink: 0,
          }}>
            <SparklesIcon size={20} />
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-heading)',
              fontSize: 18,
              fontWeight: 700,
              letterSpacing: '-0.3px',
              color: 'var(--color-charcoal)',
            }}>
              Derma<span style={{ color: 'var(--color-terracotta)' }}>Lens</span>
            </div>
            <div style={{
              fontSize: 9.5,
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.8px',
              color: 'var(--color-muted)',
              marginTop: -2,
            }}>
              Intelligent Skin Assessment
            </div>
          </div>
        </div>

        {/* Desktop Navigation Tabs */}
        <nav className="nav-desktop-group">
          <button
            onClick={() => handleNavClick('home')}
            style={{
              padding: '8px 16px',
              borderRadius: 'var(--radius-full)',
              fontSize: 14,
              fontWeight: currentTab === 'home' || currentTab === 'preparation' || currentTab === 'capture' || currentTab === 'processing' || currentTab === 'results' ? 600 : 500,
              color: currentTab === 'home' || currentTab === 'preparation' || currentTab === 'capture' || currentTab === 'processing' || currentTab === 'results' ? 'var(--color-terracotta-dark)' : 'var(--color-mocha)',
              backgroundColor: currentTab === 'home' || currentTab === 'preparation' || currentTab === 'capture' || currentTab === 'processing' || currentTab === 'results' ? 'var(--color-terracotta-subtle)' : 'transparent',
            }}
          >
            Assessment
          </button>

          <button
            onClick={() => handleNavClick('my-assessments')}
            style={{
              padding: '8px 16px',
              borderRadius: 'var(--radius-full)',
              fontSize: 14,
              fontWeight: currentTab === 'my-assessments' ? 600 : 500,
              color: currentTab === 'my-assessments' ? 'var(--color-terracotta-dark)' : 'var(--color-mocha)',
              backgroundColor: currentTab === 'my-assessments' ? 'var(--color-terracotta-subtle)' : 'transparent',
            }}
          >
            My Assessments
          </button>

          <button
            onClick={() => handleNavClick('knowledge')}
            style={{
              padding: '8px 16px',
              borderRadius: 'var(--radius-full)',
              fontSize: 14,
              fontWeight: currentTab === 'knowledge' ? 600 : 500,
              color: currentTab === 'knowledge' ? 'var(--color-terracotta-dark)' : 'var(--color-mocha)',
              backgroundColor: currentTab === 'knowledge' ? 'var(--color-terracotta-subtle)' : 'transparent',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <BookOpenIcon size={16} />
            Knowledge Base
          </button>

          <button
            onClick={() => handleNavClick('sources')}
            style={{
              padding: '8px 16px',
              borderRadius: 'var(--radius-full)',
              fontSize: 14,
              fontWeight: currentTab === 'sources' ? 600 : 500,
              color: currentTab === 'sources' ? 'var(--color-terracotta-dark)' : 'var(--color-mocha)',
              backgroundColor: currentTab === 'sources' ? 'var(--color-terracotta-subtle)' : 'transparent',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <ShieldCheckIcon size={16} />
            Evidence &amp; Sources
          </button>
        </nav>

        {/* Desktop User Identity & Profile Dropdown */}
        <div className="nav-desktop-group">
          {user ? (
            <div style={{ position: 'relative' }} ref={dropdownRef}>
              <button
                onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                aria-haspopup="true"
                aria-expanded={profileDropdownOpen}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '7px 14px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'var(--color-surface)',
                  border: '1.5px solid var(--color-border)',
                  fontSize: 13,
                  fontWeight: 600,
                  color: 'var(--color-charcoal)',
                  cursor: 'pointer',
                  transition: 'border-color var(--transition-fast)',
                }}
              >
                <UserIcon size={16} color="var(--color-terracotta)" />
                <span>{user.full_name || user.email.split('@')[0]}</span>
                <ChevronDownIcon size={14} color="var(--color-muted)" />
              </button>

              {/* Profile Popover / Dropdown Menu (Loop 19) */}
              {profileDropdownOpen && (
                <div
                  role="menu"
                  style={{
                    position: 'absolute',
                    top: 'calc(100% + 8px)',
                    right: 0,
                    width: 240,
                    backgroundColor: '#FFFFFF',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border)',
                    boxShadow: 'var(--shadow-lg)',
                    padding: '8px',
                    zIndex: 100,
                    animation: 'fadeSlideUp 0.18s cubic-bezier(0.16, 1, 0.3, 1)',
                  }}
                >
                  <div style={{
                    padding: '10px 12px 8px',
                    borderBottom: '1px solid var(--color-border-light)',
                    marginBottom: 4,
                  }}>
                    <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--color-charcoal)' }}>
                      {user.full_name || 'DermaLens User'}
                    </div>
                    <div style={{ fontSize: 11.5, color: 'var(--color-muted)', wordBreak: 'break-all', marginTop: 2 }}>
                      {user.email}
                    </div>
                  </div>

                  <button
                    role="menuitem"
                    onClick={() => handleNavClick('my-assessments')}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: '8px 12px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'none',
                      border: 'none',
                      fontSize: 13,
                      fontWeight: 500,
                      color: 'var(--color-charcoal)',
                      cursor: 'pointer',
                      textAlign: 'left',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-subtle)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <CalendarIcon size={15} color="var(--color-terracotta)" />
                    <span>My Assessments</span>
                  </button>

                  <button
                    role="menuitem"
                    onClick={() => {
                      setProfileDropdownOpen(false);
                      setAccountModalOpen(true);
                    }}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: '8px 12px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'none',
                      border: 'none',
                      fontSize: 13,
                      fontWeight: 500,
                      color: 'var(--color-charcoal)',
                      cursor: 'pointer',
                      textAlign: 'left',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-subtle)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <ShieldCheckIcon size={15} color="var(--color-sage)" />
                    <span>Account &amp; Consent</span>
                  </button>

                  <div style={{ height: 1, backgroundColor: 'var(--color-border-light)', margin: '4px 0' }} />

                  <button
                    role="menuitem"
                    onClick={handleLogoutClick}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: '8px 12px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'none',
                      border: 'none',
                      fontSize: 13,
                      fontWeight: 500,
                      color: 'var(--color-danger-text)',
                      cursor: 'pointer',
                      textAlign: 'left',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-danger-bg)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <XIcon size={15} />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={handleAuthClick}
              className="btn-secondary"
              style={{ padding: '8px 18px', fontSize: 13 }}
            >
              <UserIcon size={16} />
              Sign In
            </button>
          )}
        </div>

        {/* Mobile Hamburger Toggle Button */}
        <button
          className="nav-mobile-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? 'Close Menu' : 'Open Menu'}
        >
          {mobileMenuOpen ? <XIcon size={22} /> : <MenuIcon size={22} />}
        </button>
      </div>

      {/* Mobile Collapsible Navigation Menu */}
      <div className={`nav-mobile-menu ${mobileMenuOpen ? 'open' : ''}`}>
        <button
          onClick={() => handleNavClick('home')}
          className={`nav-mobile-item ${currentTab === 'home' || currentTab === 'preparation' || currentTab === 'capture' || currentTab === 'processing' || currentTab === 'results' ? 'active' : ''}`}
        >
          <SparklesIcon size={18} color="var(--color-terracotta)" />
          <span>Skin Assessment</span>
        </button>

        <button
          onClick={() => handleNavClick('my-assessments')}
          className={`nav-mobile-item ${currentTab === 'my-assessments' ? 'active' : ''}`}
        >
          <CalendarIcon size={18} color="var(--color-terracotta)" />
          <span>My Assessments</span>
        </button>

        <button
          onClick={() => handleNavClick('knowledge')}
          className={`nav-mobile-item ${currentTab === 'knowledge' ? 'active' : ''}`}
        >
          <BookOpenIcon size={18} color="var(--color-terracotta)" />
          <span>Knowledge Base</span>
        </button>

        <button
          onClick={() => handleNavClick('sources')}
          className={`nav-mobile-item ${currentTab === 'sources' ? 'active' : ''}`}
        >
          <ShieldCheckIcon size={18} color="var(--color-terracotta)" />
          <span>Evidence &amp; Sources</span>
        </button>

        <div style={{ height: 1, backgroundColor: 'var(--color-border-light)', margin: '4px 0' }} />

        {user ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: '4px 8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontWeight: 600 }}>
              <UserIcon size={16} color="var(--color-terracotta)" />
              <span>{user.full_name || user.email}</span>
            </div>
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                setAccountModalOpen(true);
              }}
              className="btn-ghost"
              style={{ width: '100%', justifyContent: 'flex-start', fontSize: 13, padding: '8px' }}
            >
              Account &amp; Consent
            </button>
            <button
              onClick={handleLogoutClick}
              className="btn-secondary"
              style={{ width: '100%', justifyContent: 'center', fontSize: 13, padding: '10px' }}
            >
              Sign Out
            </button>
          </div>
        ) : (
          <button
            onClick={handleAuthClick}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', fontSize: 14, padding: '11px' }}
          >
            <UserIcon size={17} />
            Sign In / Register
          </button>
        )}
      </div>

      {/* Account & Consent Information Dialog */}
      {accountModalOpen && user && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="account-modal-title"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(35, 32, 29, 0.45)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: 20,
          }}
          onClick={() => setAccountModalOpen(false)}
        >
          <div
            className="glass-panel"
            style={{
              maxWidth: 480,
              width: '100%',
              backgroundColor: '#FFFFFF',
              borderRadius: 'var(--radius-xl)',
              padding: '28px 24px',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
              <h3 id="account-modal-title" style={{ fontSize: 19, fontWeight: 700 }}>
                Account &amp; Consent
              </h3>
              <button
                onClick={() => setAccountModalOpen(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-muted)' }}
                aria-label="Close"
              >
                <XIcon size={18} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1px solid var(--color-border-light)',
              }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-muted)' }}>Registered Email</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-charcoal)', marginTop: 2 }}>{user.email}</div>
              </div>

              {user.full_name && (
                <div style={{
                  padding: '14px 16px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-surface-subtle)',
                  border: '1px solid var(--color-border-light)',
                }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-muted)' }}>Full Name</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--color-charcoal)', marginTop: 2 }}>{user.full_name}</div>
                </div>
              )}

              <div style={{
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-surface-subtle)',
                border: '1px solid var(--color-border-light)',
              }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-muted)' }}>Assessment Consent Agreement</div>
                <div style={{ fontSize: 13, color: 'var(--color-mocha)', marginTop: 4, lineHeight: 1.5 }}>
                  Active agreement: Non-diagnostic informational wellness scan (Consent version 1.0). All image data is private and encrypted in isolation.
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 22 }}>
              <button
                onClick={() => setAccountModalOpen(false)}
                className="btn-secondary"
                style={{ padding: '8px 20px', fontSize: 13 }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
