/**
 * Standard formatters for DermaLens frontend.
 * Provides consistent date/time, status, and capture method representations.
 */

export function formatAssessmentDateTime(isoString?: string | null): string {
  if (!isoString) return 'Date unknown';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return 'Date unknown';
    
    // e.g. "October 11, 2026 · 7:14 PM"
    const datePart = d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    const timePart = d.toLocaleTimeString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    });
    return `${datePart} · ${timePart}`;
  } catch {
    return 'Date unknown';
  }
}

export function formatAssessmentDate(isoString?: string | null): string {
  if (!isoString) return 'Date unknown';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return 'Date unknown';
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return 'Date unknown';
  }
}

export function formatAssessmentTime(isoString?: string | null): string {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleTimeString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    });
  } catch {
    return '';
  }
}

/**
 * Human-readable status mapping:
 * - created -> Preparing
 * - processing -> Processing
 * - processed -> Analysis Complete
 * - analyzed -> Results Ready
 * - error -> Needs Attention
 */
export function formatAssessmentStatus(status?: string | null): string {
  if (!status) return 'In Progress';
  const s = status.toLowerCase();
  switch (s) {
    case 'created':
      return 'Preparing';
    case 'processing':
      return 'Processing';
    case 'processed':
      return 'Analysis Complete';
    case 'analyzed':
      return 'Results Ready';
    case 'error':
    case 'failed':
      return 'Needs Attention';
    default:
      return status.charAt(0).toUpperCase() + status.slice(1);
  }
}

export function getStatusBadgeClass(status?: string | null): string {
  if (!status) return 'pill-neutral';
  const s = status.toLowerCase();
  switch (s) {
    case 'analyzed':
    case 'processed':
      return 'pill-sage';
    case 'processing':
    case 'created':
      return 'pill-terracotta';
    case 'error':
    case 'failed':
      return 'pill-danger';
    default:
      return 'pill-neutral';
  }
}

/**
 * Capture method badges:
 * Camera, Upload, or Camera + Upload
 */
export function formatCaptureBadge(
  captureType?: string | null,
  captureModes?: Record<string, string> | null
): string {
  if (captureModes && Object.keys(captureModes).length > 0) {
    const modes = Object.values(captureModes).map(m => m.toLowerCase());
    const hasCamera = modes.some(m => m === 'camera');
    const hasUpload = modes.some(m => m === 'upload');
    if (hasCamera && hasUpload) return 'Camera + Upload';
    if (hasCamera) return 'Camera';
    if (hasUpload) return 'Upload';
  }

  const type = (captureType || '').toLowerCase();
  if (type === 'hybrid' || type === 'camera + upload' || type === 'mixed') {
    return 'Camera + Upload';
  }
  if (type === 'camera') return 'Camera';
  return 'Upload';
}

export function getViewCaptureBadge(view: string, captureModes?: Record<string, string> | null): string {
  if (captureModes && captureModes[view]) {
    const mode = captureModes[view].toLowerCase();
    return mode === 'camera' ? 'Camera' : 'Upload';
  }
  return 'Upload';
}
