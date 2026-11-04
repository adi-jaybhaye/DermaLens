import React, { useEffect, useState } from 'react';
import { DownloadIcon, SmartphoneIcon, ShareIcon, XIcon } from './Icons';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
}

export const PwaInstallPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [isIos] = useState(() => {
    if (typeof window === 'undefined') return false;
    const ua = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test(ua) && !(window as unknown as { MSStream?: unknown }).MSStream;
  });
  const [isStandalone] = useState(() => {
    if (typeof window === 'undefined') return false;
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as unknown as { standalone?: boolean }).standalone === true
    );
  });

  useEffect(() => {
    if (isStandalone) {
      return;
    }

    // Check if user has already dismissed prompt in this session
    const dismissed = sessionStorage.getItem('dermalens_pwa_dismissed');
    if (dismissed === 'true') {
      return;
    }

    // Handler for Chromium / Android / Desktop Chrome / Edge
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setIsVisible(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Notify user on web entry after a gentle 1.5s delay if not already in standalone mode
    const entryTimer = setTimeout(() => {
      if (!isStandalone) {
        setIsVisible(true);
      }
    }, 1500);

    // Manual trigger listener from menu
    const handleManualOpen = () => {
      setIsVisible(true);
    };
    window.addEventListener('open-pwa-install', handleManualOpen);

    // Also listen for appinstalled event
    const handleAppInstalled = () => {
      setIsVisible(false);
      setDeferredPrompt(null);
    };
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      clearTimeout(entryTimer);
      window.removeEventListener('open-pwa-install', handleManualOpen);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, [isStandalone]);

  const [installTip, setInstallTip] = useState(false);

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      try {
        await deferredPrompt.prompt();
        const choice = await deferredPrompt.userChoice;
        if (choice.outcome === 'accepted') {
          setIsVisible(false);
        }
        setDeferredPrompt(null);
      } catch (err) {
        console.warn('PWA install prompt error:', err);
      }
    } else {
      setInstallTip(true);
      setTimeout(() => setInstallTip(false), 5000);
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
    sessionStorage.setItem('dermalens_pwa_dismissed', 'true');
  };

  if (!isVisible || isStandalone) {
    return null;
  }

  return (
    <aside
      className="pwa-install-banner"
      role="banner"
      aria-label="Install DermaLens Progressive Web App"
    >
      <div className="pwa-banner-content">
        <div className="pwa-banner-icon-wrap" aria-hidden="true">
          <img
            src="/icons/icon-192.png"
            alt="DermaLens App Icon"
            className="pwa-banner-icon"
            width={44}
            height={44}
          />
        </div>

        <div className="pwa-banner-text">
          <div className="pwa-banner-header">
            <span className="pwa-banner-eyebrow">Progressive Web App</span>
            <span className="pwa-banner-badge">Fast & Offline-Ready</span>
          </div>
          <h3 className="pwa-banner-title">Install DermaLens on Your Device</h3>
          <p className="pwa-banner-description">
            {isIos ? (
              <span>
                Tap the <strong>Share</strong> button <ShareIcon size={13} style={{ display: 'inline', verticalAlign: 'middle' }} /> and select <strong>&quot;Add to Home Screen&quot;</strong> for full-screen camera and assessment experience.
              </span>
            ) : installTip ? (
              <span style={{ color: 'var(--color-terracotta)', fontWeight: 600 }}>
                Click the <strong>Install</strong> icon (⊕) in your browser&apos;s address bar or menu to add DermaLens to your apps.
              </span>
            ) : (
              <span>
                Add DermaLens to your home screen or desktop for rapid camera launch, smooth multi-view capture, and immersive analysis.
              </span>
            )}
          </p>
        </div>

        <div className="pwa-banner-actions">
          {!isIos && (
            <button
              type="button"
              className="pwa-btn-primary"
              onClick={handleInstallClick}
              aria-label="Install App"
            >
              <DownloadIcon size={15} />
              <span>Install App</span>
            </button>
          )}

          {isIos && (
            <div className="pwa-ios-instructions">
              <SmartphoneIcon size={15} />
              <span>Share &rarr; Add to Home Screen</span>
            </div>
          )}

          <button
            type="button"
            className="pwa-btn-dismiss"
            onClick={handleDismiss}
            aria-label="Dismiss install notification"
          >
            <XIcon size={16} />
            <span>Later</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
