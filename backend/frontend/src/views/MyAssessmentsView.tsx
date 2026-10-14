import React, { useEffect, useState, useMemo } from 'react';
import { api, type AssessmentHistoryItem } from '../api/client';
import { useToast } from '../components/Toast';
import {
  SparklesIcon,
  CameraIcon,
  ChevronRightIcon,
  EditIcon,
  TrashIcon,
  SearchIcon,
  CalendarIcon,
  XIcon,
} from '../components/Icons';
import {
  formatAssessmentDateTime,
  formatAssessmentStatus,
  getStatusBadgeClass,
  formatCaptureBadge,
} from '../utils/formatters';

interface MyAssessmentsViewProps {
  onStartAssessment: () => void;
  onOpenAssessment: (id: string) => void;
}

export const MyAssessmentsView: React.FC<MyAssessmentsViewProps> = ({
  onStartAssessment,
  onOpenAssessment,
}) => {
  const { showToast } = useToast();
  const [assessments, setAssessments] = useState<AssessmentHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Rename modal state
  const [renameTarget, setRenameTarget] = useState<AssessmentHistoryItem | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [isRenaming, setIsRenaming] = useState(false);

  // Delete modal state
  const [deleteTarget, setDeleteTarget] = useState<AssessmentHistoryItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getAssessmentHistory()
      .then((data) => {
        if (isMounted) {
          setAssessments(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setLoading(false);
          showToast('Could not load assessment history.', 'error');
        }
      });

    return () => {
      isMounted = false;
    };
  }, [showToast]);

  const filteredAssessments = useMemo(() => {
    if (!searchQuery.trim()) return assessments;
    const q = searchQuery.toLowerCase();
    return assessments.filter((item) => {
      const name = (item.name || `Assessment ${item.assessment_number || ''}`).toLowerCase();
      const status = formatAssessmentStatus(item.status).toLowerCase();
      const date = formatAssessmentDateTime(item.created_at).toLowerCase();
      return name.includes(q) || status.includes(q) || date.includes(q);
    });
  }, [assessments, searchQuery]);

  const handleOpenRename = (item: AssessmentHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation();
    setRenameTarget(item);
    setRenameValue(item.name || `Assessment ${item.assessment_number || 1}`);
  };

  const handleConfirmRename = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!renameTarget) return;
    const trimmed = renameValue.trim();
    if (!trimmed) {
      showToast('Assessment name cannot be empty', 'error');
      return;
    }

    try {
      setIsRenaming(true);
      await api.renameAssessment(renameTarget.id, trimmed);
      setAssessments((prev) =>
        prev.map((a) => (a.id === renameTarget.id ? { ...a, name: trimmed } : a))
      );
      showToast('Assessment renamed successfully', 'success');
      setRenameTarget(null);
    } catch (err: any) {
      showToast(err.message || 'Failed to rename assessment', 'error');
    } finally {
      setIsRenaming(false);
    }
  };

  const handleOpenDelete = (item: AssessmentHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeleteTarget(item);
  };

  const handleConfirmDelete = async () => {
    if (!deleteTarget) return;

    try {
      setIsDeleting(true);
      await api.deleteAssessment(deleteTarget.id);
      setAssessments((prev) => prev.filter((a) => a.id !== deleteTarget.id));
      showToast('Assessment deleted successfully', 'success');
      setDeleteTarget(null);
    } catch (err: any) {
      showToast(err.message || 'Failed to delete assessment', 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '36px 20px 80px' }}>
      {/* Header & Action Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16,
        marginBottom: 28,
      }}>
        <div>
          <div className="pill-badge pill-terracotta" style={{ marginBottom: 6 }}>
            <SparklesIcon size={13} />
            Assessment Records
          </div>
          <h2 style={{ fontSize: 30, fontWeight: 700, color: 'var(--color-charcoal)' }}>
            My Assessments
          </h2>
          <p style={{ fontSize: 14, color: 'var(--color-muted)', marginTop: 4 }}>
            Your private chronological facial skin assessment sessions
          </p>
        </div>

        <button
          onClick={onStartAssessment}
          className="btn-primary"
          style={{ fontSize: 14, padding: '10px 22px' }}
        >
          <CameraIcon size={17} />
          Start New Assessment
        </button>
      </div>

      {/* Filter / Search Bar (if assessments exist or were existing) */}
      {(assessments.length > 0 || searchQuery) && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '10px 16px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          marginBottom: 24,
          boxShadow: 'var(--shadow-sm)',
        }}>
          <SearchIcon size={17} color="var(--color-muted)" />
          <input
            type="text"
            placeholder="Search assessments by name, date, or status..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              border: 'none',
              outline: 'none',
              width: '100%',
              fontSize: 14,
              fontFamily: 'var(--font-body)',
              color: 'var(--color-charcoal)',
              backgroundColor: 'transparent',
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'var(--color-muted)',
                padding: 4,
                display: 'flex',
              }}
              aria-label="Clear search"
            >
              <XIcon size={15} />
            </button>
          )}
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              className="glass-panel"
              style={{
                padding: '24px',
                borderRadius: 'var(--radius-lg)',
                backgroundColor: 'var(--color-surface)',
                display: 'flex',
                flexDirection: 'column',
                gap: 12,
                opacity: 0.7,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <div style={{ width: 140, height: 20, backgroundColor: 'var(--color-sand)', borderRadius: 6 }} />
                <div style={{ width: 90, height: 20, backgroundColor: 'var(--color-sand)', borderRadius: 12 }} />
              </div>
              <div style={{ width: 220, height: 14, backgroundColor: 'var(--color-sand-dark)', borderRadius: 4 }} />
            </div>
          ))}
        </div>
      )}

      {/* Empty State (Loop 4) */}
      {!loading && assessments.length === 0 && (
        <div
          className="glass-panel"
          style={{
            textAlign: 'center',
            padding: '60px 24px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: 'var(--color-surface)',
            border: '1.5px dashed var(--color-border)',
            maxWidth: 580,
            margin: '40px auto',
          }}
        >
          <div
            style={{
              width: 58,
              height: 58,
              borderRadius: '50%',
              backgroundColor: 'var(--color-blush)',
              color: 'var(--color-terracotta)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
            }}
          >
            <CameraIcon size={28} />
          </div>

          <h3 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8, color: 'var(--color-charcoal)' }}>
            Your Assessments
          </h3>

          <p style={{ fontSize: 14.5, color: 'var(--color-muted)', lineHeight: 1.55, maxWidth: 420, margin: '0 auto 24px' }}>
            You haven't completed an assessment yet. Start your first assessment to see your multi-view results and skin analysis history here.
          </p>

          <button
            onClick={onStartAssessment}
            className="btn-primary"
            style={{ fontSize: 14.5, padding: '12px 28px' }}
          >
            <SparklesIcon size={18} />
            Start Your First Assessment
          </button>
        </div>
      )}

      {/* No Search Matches */}
      {!loading && assessments.length > 0 && filteredAssessments.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          color: 'var(--color-muted)',
          fontSize: 14,
        }}>
          No assessments match your search for "{searchQuery}".
        </div>
      )}

      {/* Assessment List */}
      {!loading && filteredAssessments.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {filteredAssessments.map((item) => {
            const displayName = item.name || `Assessment ${item.assessment_number || 1}`;
            const formattedDate = formatAssessmentDateTime(item.created_at);
            const viewCount = item.views?.length || 1;
            const captureBadgeText = formatCaptureBadge(item.capture_type, item.capture_modes);
            const statusLabel = formatAssessmentStatus(item.status);
            const statusBadgeClass = getStatusBadgeClass(item.status);

            return (
              <div
                key={item.id}
                onClick={() => onOpenAssessment(item.id)}
                className="glass-panel"
                style={{
                  padding: '20px 24px',
                  borderRadius: 'var(--radius-lg)',
                  backgroundColor: 'var(--color-surface)',
                  border: '1.5px solid var(--color-border-light)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 16,
                  transition: 'transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.borderColor = 'var(--color-terracotta)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.borderColor = 'var(--color-border-light)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {/* Identity & Metadata */}
                <div style={{ minWidth: 240, flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                    <h4 style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-charcoal)' }}>
                      {displayName}
                    </h4>
                    <span className={`pill-badge ${statusBadgeClass}`} style={{ fontSize: 11 }}>
                      {statusLabel}
                    </span>
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 14,
                    fontSize: 12.5,
                    color: 'var(--color-muted)',
                    marginTop: 6,
                    flexWrap: 'wrap',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                      <CalendarIcon size={14} color="var(--color-subtle)" />
                      <span>{formattedDate}</span>
                    </div>

                    <span>&bull;</span>

                    <div>
                      <strong>{viewCount}</strong> {viewCount === 1 ? 'View' : 'Views'}
                    </div>

                    <span>&bull;</span>

                    <div style={{
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: 'var(--color-surface-subtle)',
                      border: '1px solid var(--color-border-light)',
                      fontSize: 11,
                      fontWeight: 600,
                      color: 'var(--color-mocha)',
                    }}>
                      {captureBadgeText}
                    </div>
                  </div>
                </div>

                {/* Actions Group */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }} onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={(e) => handleOpenRename(item, e)}
                    className="btn-ghost"
                    style={{
                      padding: '8px 12px',
                      fontSize: 12.5,
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 5,
                      color: 'var(--color-mocha)',
                    }}
                    title="Rename this assessment"
                    aria-label={`Rename ${displayName}`}
                  >
                    <EditIcon size={14} />
                    <span>Rename</span>
                  </button>

                  <button
                    onClick={(e) => handleOpenDelete(item, e)}
                    className="btn-ghost"
                    style={{
                      padding: '8px 12px',
                      fontSize: 12.5,
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 5,
                      color: 'var(--color-danger-text)',
                    }}
                    title="Delete this assessment"
                    aria-label={`Delete ${displayName}`}
                  >
                    <TrashIcon size={14} />
                    <span>Delete</span>
                  </button>

                  <button
                    onClick={() => onOpenAssessment(item.id)}
                    className="btn-secondary"
                    style={{
                      padding: '8px 16px',
                      fontSize: 13,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      fontWeight: 600,
                    }}
                  >
                    <span>View Results</span>
                    <ChevronRightIcon size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Rename Modal (Loop 20) */}
      {renameTarget && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="rename-modal-title"
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
          onClick={() => !isRenaming && setRenameTarget(null)}
        >
          <div
            className="glass-panel"
            style={{
              maxWidth: 440,
              width: '100%',
              backgroundColor: '#FFFFFF',
              borderRadius: 'var(--radius-xl)',
              padding: '28px 24px',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <h3 id="rename-modal-title" style={{ fontSize: 18, fontWeight: 700 }}>
                Rename Assessment
              </h3>
              <button
                onClick={() => setRenameTarget(null)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-muted)' }}
                aria-label="Close"
              >
                <XIcon size={18} />
              </button>
            </div>

            <form onSubmit={handleConfirmRename}>
              <p style={{ fontSize: 13, color: 'var(--color-muted)', marginBottom: 14 }}>
                Give this assessment a custom label (e.g. "Morning Routine Check" or "Pre-Treatment Baseline"):
              </p>

              <input
                type="text"
                autoFocus
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                maxLength={80}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1.5px solid var(--color-border)',
                  fontSize: 14,
                  fontFamily: 'var(--font-body)',
                  marginBottom: 20,
                  outline: 'none',
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                <button
                  type="button"
                  onClick={() => setRenameTarget(null)}
                  disabled={isRenaming}
                  className="btn-ghost"
                  style={{ padding: '8px 16px', fontSize: 13 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isRenaming}
                  className="btn-primary"
                  style={{ padding: '8px 18px', fontSize: 13 }}
                >
                  {isRenaming ? 'Saving...' : 'Save Name'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal (Loop 21) */}
      {deleteTarget && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-modal-title"
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
          onClick={() => !isDeleting && setDeleteTarget(null)}
        >
          <div
            className="glass-panel"
            style={{
              maxWidth: 440,
              width: '100%',
              backgroundColor: '#FFFFFF',
              borderRadius: 'var(--radius-xl)',
              padding: '28px 24px',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{
              width: 44,
              height: 44,
              borderRadius: '50%',
              backgroundColor: 'var(--color-danger-bg)',
              color: 'var(--color-danger-text)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16,
            }}>
              <TrashIcon size={22} />
            </div>

            <h3 id="delete-modal-title" style={{ fontSize: 19, fontWeight: 700, marginBottom: 8 }}>
              Delete {deleteTarget.name || `Assessment ${deleteTarget.assessment_number || 1}`}?
            </h3>

            <p style={{ fontSize: 13.5, color: 'var(--color-mocha)', lineHeight: 1.55, marginBottom: 20 }}>
              This will permanently remove this assessment, its facial zone mappings, and all associated stored images from the server. This action cannot be undone.
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button
                type="button"
                onClick={() => setDeleteTarget(null)}
                disabled={isDeleting}
                className="btn-ghost"
                style={{ padding: '8px 16px', fontSize: 13 }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                style={{
                  backgroundColor: 'var(--color-danger-text)',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: 'var(--radius-full)',
                  padding: '8px 18px',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: isDeleting ? 'not-allowed' : 'pointer',
                  opacity: isDeleting ? 0.7 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <TrashIcon size={14} />
                {isDeleting ? 'Deleting...' : 'Delete Assessment'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
