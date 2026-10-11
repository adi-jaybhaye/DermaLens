import React, { useState } from 'react';
import type { User } from '../api/client';
import { SparklesIcon, UserIcon, BookOpenIcon, ShieldCheckIcon, MenuIcon, XIcon } from './Icons';

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

  const handleNavClick = (tab: string) => {
    setCurrentTab(tab);
    setMobileMenuOpen(false);
  };

  const handleAuthClick = () => {
    onOpenAuth();
    setMobileMenuOpen(false);
  };

  const handleLogoutClick = () => {
    onLogout();
    setMobileMenuOpen(false);
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
              fontWeight: currentTab === 'home' ? 600 : 500,
              color: currentTab === 'home' ? 'var(--color-terracotta-dark)' : 'var(--color-mocha)',
              backgroundColor: currentTab === 'home' ? 'var(--color-terracotta-subtle)' : 'transparent',
            }}
          >
            Assessment
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

        {/* Desktop User Identity */}
        <div className="nav-desktop-group">
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '6px 14px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                fontSize: 13,
                fontWeight: 600,
                color: 'var(--color-charcoal)',
              }}>
                <UserIcon size={16} color="var(--color-terracotta)" />
                <span>{user.full_name || user.email.split('@')[0]}</span>
              </div>
              <button
                onClick={handleLogoutClick}
                style={{
                  fontSize: 13,
                  color: 'var(--color-muted)',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-full)',
                }}
              >
                Sign Out
              </button>
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
          className={`nav-mobile-item ${currentTab === 'home' || currentTab === 'preparation' || currentTab === 'capture' || currentTab === 'results' ? 'active' : ''}`}
        >
          <SparklesIcon size={18} color="var(--color-terracotta)" />
          <span>Skin Assessment</span>
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
    </header>
  );
};

