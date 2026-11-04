import React, { useEffect, useState } from 'react';
import { api, type User, type AssessmentResults } from './api/client';
import { Navbar } from './components/Navbar';
import { AuthModal } from './components/AuthModal';
import { ToastProvider, useToast } from './components/Toast';
import { CoverView } from './views/CoverView';
import { HomeView } from './views/HomeView';
import { PreparationView } from './views/PreparationView';
import { CaptureView } from './views/CaptureView';
import { ProcessingView } from './views/ProcessingView';
import { ResultsDashboardView } from './views/ResultsDashboardView';
import { MyAssessmentsView } from './views/MyAssessmentsView';
import { KnowledgeView } from './views/KnowledgeView';
import { SourcesView } from './views/SourcesView';

import { SparklesIcon, CameraIcon } from './components/Icons';
import { PwaInstallPrompt } from './components/PwaInstallPrompt';

export type AppTab =
  | 'cover'
  | 'home'
  | 'preparation'
  | 'capture'
  | 'processing'
  | 'results'
  | 'my-assessments'
  | 'knowledge'
  | 'sources';

const AppContent: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<AppTab>('cover');
  const [user, setUser] = useState<User | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [viewFiles, setViewFiles] = useState<Record<'front' | 'left' | 'right', File> | null>(null);
  const [captureModes, setCaptureModes] = useState<Record<'front' | 'left' | 'right', 'camera' | 'upload'>>({
    front: 'upload',
    left: 'upload',
    right: 'upload',
  });
  const [results, setResults] = useState<AssessmentResults | null>(null);
  const { showToast } = useToast();

  // Check auth status on load
  useEffect(() => {
    api.getMe()
      .then(setUser)
      .catch(() => {});

    // Expose helpers for layout inspection & testing
    const win = window as unknown as Record<string, unknown>;
    win.__setTab = setCurrentTab;
    win.__setUser = setUser;
    win.__setResults = setResults;
    win.__openAuthModal = () => setIsAuthModalOpen(true);
  }, []);


  const handleStartAssessment = () => {
    if (!user) {
      setIsAuthModalOpen(true);
      return;
    }
    setCurrentTab('preparation');
  };

  const handleProceedToCapture = () => {
    setCurrentTab('capture');
  };

  const handleCaptureComplete = (
    files: Record<'front' | 'left' | 'right', File>,
    modes: Record<'front' | 'left' | 'right', 'camera' | 'upload'>
  ) => {
    setViewFiles(files);
    setCaptureModes(modes);
    setCurrentTab('processing');
  };

  const handleProcessingSuccess = (data: AssessmentResults) => {
    setResults(data);
    setCurrentTab('results');
  };

  const handleProcessingError = () => {
    setCurrentTab('capture');
  };

  const handleOpenHistoryItem = async (assessmentId: string) => {
    try {
      const data = await api.getResults(assessmentId);
      setResults(data);
      setCurrentTab('results');
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Could not load assessment details.', 'error');
    }
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
    showToast('Signed out successfully', 'info');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {currentTab !== 'cover' && (
        <Navbar
          currentTab={currentTab}
          setCurrentTab={(tab) => setCurrentTab(tab as AppTab)}
          user={user}
          onOpenAuth={() => setIsAuthModalOpen(true)}
          onLogout={handleLogout}
        />
      )}

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {currentTab === 'cover' && (
          <CoverView
            onStartAssessment={handleStartAssessment}
            onExploreKnowledge={() => setCurrentTab('knowledge')}
            onViewSources={() => setCurrentTab('sources')}
            onOpenAuth={() => setIsAuthModalOpen(true)}
            user={user}
            onLogout={handleLogout}
          />
        )}

        {currentTab === 'home' && (
          <HomeView
            onStartAssessment={handleStartAssessment}
            onOpenHistoryItem={handleOpenHistoryItem}
            onExploreKnowledge={() => setCurrentTab('knowledge')}
            onViewAllAssessments={() => setCurrentTab('my-assessments')}
          />
        )}

        {currentTab === 'my-assessments' && (
          <MyAssessmentsView
            onStartAssessment={handleStartAssessment}
            onOpenAssessment={handleOpenHistoryItem}
          />
        )}

        {currentTab === 'preparation' && (
          <PreparationView
            onProceed={handleProceedToCapture}
            onBack={() => setCurrentTab('home')}
          />
        )}

        {currentTab === 'capture' && (
          <CaptureView
            onComplete={handleCaptureComplete}
            onBack={() => setCurrentTab('preparation')}
          />
        )}


        {currentTab === 'processing' && (
          <ProcessingView
            viewFiles={viewFiles || {
              front: new File([''], 'front.jpg', { type: 'image/jpeg' }),
              left: new File([''], 'left.jpg', { type: 'image/jpeg' }),
              right: new File([''], 'right.jpg', { type: 'image/jpeg' }),
            }}
            captureModes={captureModes}
            onSuccess={handleProcessingSuccess}
            onError={handleProcessingError}
          />
        )}

        {currentTab === 'results' && (
          results ? (
            <ResultsDashboardView
              results={results}
              onNewAssessment={() => {
                setResults(null);
                setViewFiles(null);
                setCurrentTab('preparation');
              }}
            />
          ) : (
            <div style={{ maxWidth: 600, margin: '60px auto', padding: '0 20px', textAlign: 'center' }}>
              <div className="glass-panel" style={{ padding: '48px 32px', backgroundColor: '#FFFFFF', borderRadius: 'var(--radius-xl)' }}>
                <div style={{
                  width: 56,
                  height: 56,
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-blush)',
                  color: 'var(--color-terracotta)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 20px',
                }}>
                  <CameraIcon size={28} />
                </div>
                <h3 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8, color: 'var(--color-charcoal)' }}>
                  No Assessment Results Available
                </h3>
                <p style={{ fontSize: 14.5, color: 'var(--color-muted)', lineHeight: 1.55, marginBottom: 24 }}>
                  Please complete a multi-angle facial assessment or select a previous session from your history to view detailed AI analysis and explanations.
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: 12, flexWrap: 'wrap' }}>
                  <button
                    onClick={handleStartAssessment}
                    className="btn-primary"
                    style={{ padding: '12px 28px', fontSize: 14 }}
                  >
                    <SparklesIcon size={16} /> Start New Assessment
                  </button>
                  <button
                    onClick={() => setCurrentTab('my-assessments')}
                    className="btn-secondary"
                    style={{ padding: '12px 24px', fontSize: 14 }}
                  >
                    View Assessment History
                  </button>
                </div>
              </div>
            </div>
          )
        )}

        {currentTab === 'knowledge' && <KnowledgeView />}

        {currentTab === 'sources' && <SourcesView />}
      </main>


      {currentTab !== 'cover' && (
        <footer style={{
          borderTop: '1px solid var(--color-border)',
          padding: '24px 20px',
          textAlign: 'center',
          fontSize: 13,
          color: 'var(--color-muted)',
          backgroundColor: 'rgba(250, 247, 242, 0.95)',
        }}>
          <div style={{ maxWidth: 1140, margin: '0 auto' }}>
            <div>
              <strong>DermaLens</strong> &mdash; Facial Skin Assessment Platform &bull; Informational Wellness Tool
            </div>
            <div style={{ marginTop: 4, fontSize: 12 }}>
              AI-Powered Surface Pattern Analysis &bull; Not a medical diagnostic device. Always consult a board-certified dermatologist for clinical concerns.
            </div>
          </div>
        </footer>
      )}

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={(u) => {
          setUser(u);
          showToast(`Welcome back, ${u.full_name || u.email}!`, 'success');
        }}
      />

      <PwaInstallPrompt />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
};

export default App;
