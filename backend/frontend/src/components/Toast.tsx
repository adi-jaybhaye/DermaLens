import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircleIcon, ShieldCheckIcon, XIcon, InfoIcon } from './Icons';

export type ToastType = 'success' | 'error' | 'info';

interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
      removeToast(id);
    }, 4000);
  }, [removeToast]);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast Container */}
      <div
        aria-live="polite"
        aria-atomic="true"
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          zIndex: 9999,
          maxWidth: 380,
          width: 'calc(100vw - 48px)',
          pointerEvents: 'none',
        }}
      >
        {toasts.map((toast) => {
          const isSuccess = toast.type === 'success';
          const isError = toast.type === 'error';

          const accentColor = isSuccess
            ? 'var(--color-sage)'
            : isError
            ? 'var(--color-danger-text)'
            : 'var(--color-terracotta)';

          const bgColor = isSuccess
            ? 'var(--color-success-bg)'
            : isError
            ? 'var(--color-danger-bg)'
            : 'var(--color-surface)';

          const borderColor = isSuccess
            ? 'var(--color-success-border)'
            : isError
            ? 'var(--color-danger-border)'
            : 'var(--color-border)';

          return (
            <div
              key={toast.id}
              role={isError ? 'alert' : 'status'}
              style={{
                pointerEvents: 'auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 12,
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: bgColor,
                border: `1.5px solid ${borderColor}`,
                boxShadow: 'var(--shadow-md)',
                fontSize: 13.5,
                fontWeight: 500,
                color: 'var(--color-charcoal)',
                animation: 'fadeSlideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1 }}>
                <div style={{ color: accentColor, flexShrink: 0, display: 'flex' }}>
                  {isSuccess && <CheckCircleIcon size={18} />}
                  {isError && <ShieldCheckIcon size={18} />}
                  {!isSuccess && !isError && <InfoIcon size={18} />}
                </div>
                <span style={{ lineHeight: 1.4 }}>{toast.message}</span>
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                aria-label="Dismiss notification"
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 4,
                  cursor: 'pointer',
                  color: 'var(--color-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  borderRadius: 4,
                  flexShrink: 0,
                }}
              >
                <XIcon size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextValue => {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return ctx;
};
