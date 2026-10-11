import React, { useEffect, useState } from 'react';
import { api, type User, type AssessmentResults } from './api/client';
import { Navbar } from './components/Navbar';
import { AuthModal } from './components/AuthModal';
import { HomeView } from './views/HomeView';
import { PreparationView } from './views/PreparationView';
import { CaptureView } from './views/CaptureView';
import { ProcessingView } from './views/ProcessingView';
import { ResultsDashboardView } from './views/ResultsDashboardView';
import { KnowledgeView } from './views/KnowledgeView';
import { SourcesView } from './views/SourcesView';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'home' | 'preparation' | 'capture' | 'processing' | 'results' | 'knowledge' | 'sources'>('home');
  const [user, setUser] = useState<User | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [viewFiles, setViewFiles] = useState<Record<'front' | 'left' | 'right', File> | null>(null);
  const [results, setResults] = useState<AssessmentResults | null>(null);

  // Check auth status on load
  useEffect(() => {
    api.getMe()
      .then(setUser)
      .catch(() => {});
  }, []);

  const handleStartAssessment = () => {
    setCurrentTab('preparation');
  };

  const handleProceedToCapture = () => {
    setCurrentTab('capture');
  };

  const handleCaptureComplete = (files: Record<'front' | 'left' | 'right', File>) => {
    setViewFiles(files);
    setCurrentTab('processing');
  };

  const handleProcessingSuccess = (data: AssessmentResults) => {
    setResults(data);
    setCurrentTab('results');
  };

  const handleProcessingError = (_msg: string) => {
    setCurrentTab('capture');
  };

  const handleOpenHistoryItem = async (assessmentId: string) => {
    try {
      const data = await api.getResults(assessmentId);
      setResults(data);
      setCurrentTab('results');
    } catch (err) {
      alert('Could not load assessment details.');
    }
  };

  const handleLogout = () => {
    api.logout();
    setUser(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        currentTab={currentTab}
        setCurrentTab={(tab) => setCurrentTab(tab as any)}
        user={user}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onLogout={handleLogout}
      />

      <main style={{ flex: 1 }}>
        {currentTab === 'home' && (
          <HomeView
            onStartAssessment={handleStartAssessment}
            onOpenHistoryItem={handleOpenHistoryItem}
            onExploreKnowledge={() => setCurrentTab('knowledge')}
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

        {currentTab === 'processing' && viewFiles && (
          <ProcessingView
            viewFiles={viewFiles}
            onSuccess={handleProcessingSuccess}
            onError={handleProcessingError}
          />
        )}

        {currentTab === 'results' && results && (
          <ResultsDashboardView
            results={results}
            onNewAssessment={() => {
              setResults(null);
              setViewFiles(null);
              setCurrentTab('preparation');
            }}
          />
        )}

        {currentTab === 'knowledge' && <KnowledgeView />}

        {currentTab === 'sources' && <SourcesView />}
      </main>

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

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={(u) => setUser(u)}
      />
    </div>
  );
};

export default App;
