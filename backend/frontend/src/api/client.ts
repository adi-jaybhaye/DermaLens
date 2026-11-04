/**
 * API client for Face Skin Assessment System backend.
 */

const API_BASE = (import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE || '/api/v1';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ConcernKnowledge {
  concept: string;
  display_name: string;
  description: string;
  visual_characteristics: string[];
  common_contributing_factors: string[];
  why_it_can_occur: string;
  safety_notes: string;
  when_to_consult: string;
  evidence_references: Array<{
    title: string;
    source: string;
    url: string;
  }>;
}

export interface XaiSource {
  id: string;
  title: string;
  authors: string;
  year: string;
  authority: string;
  identifier: string;
  url?: string;
  key_findings: string;
  limitations: string;
}

export interface XaiLearnMore {
  scientific_explanation: string;
  contributing_factors: string[];
  limitations: string;
  safety_guidance: string;
  sources: XaiSource[];
}

export interface RegionXaiDetails {
  what_we_noticed: string;
  where_we_noticed_it: string;
  why_ai_identified_it: string;
  why_it_can_occur: string;
  heatmap_explanation?: string;
  learn_more?: XaiLearnMore;
}

export interface RegionConcern {
  concept: string;
  display_name: string;
  confidence: number;
  model_confidence?: number;
  is_confident?: boolean;
  confidence_status?: string;
  why_identified?: string;
  why_it_can_occur?: string;
  visual_evidence?: string[];
  sources?: Array<{
    title: string;
    source: string;
    url: string;
  }>;
  xai?: RegionXaiDetails;
  region?: { name: string; display_name: string };
}

export interface RegionData {
  valid: boolean;
  detected?: boolean;
  reason?: string;
  concern?: RegionConcern | null;
  xai_explanation?: {
    concept: string;
    display_name: string;
    model_confidence: number;
    confidence_status: string;
    region: { name: string; display_name: string };
    xai: RegionXaiDetails;
  };
  all_probabilities?: Record<string, number>;
  texture_metrics?: {
    mean_brightness?: number;
    brightness_std?: number;
    texture_variance?: number;
  };
}

export interface XaiData {
  predicted_concern: string;
  confidence: number;
  heatmap_base64?: string;
  overlay_base64?: string;
  all_probabilities?: Record<string, number>;
  note?: string;
}

export interface ViewResult {
  analysis_completed: boolean;
  quality?: {
    valid: boolean;
    blur?: { is_blurry: boolean; variance: number };
    brightness?: { is_good: boolean; mean_brightness: number };
    resolution?: { is_valid: boolean; width: number; height: number };
  };
  regions: Record<string, RegionData>;
  xai?: Record<string, XaiData>;
}

export interface AssessmentHistoryItem {
  id: string;
  assessment_number?: number;
  name?: string;
  status: string;
  capture_type: string;
  capture_modes?: Record<string, string>;
  views: string[];
  created_at: string;
  updated_at?: string;
}

export interface AssessmentResults {
  assessment_id: string;
  assessment_number?: number;
  name?: string;
  created_at?: string;
  updated_at?: string;
  status: string;
  capture_type: string;
  capture_modes?: Record<string, string>;
  skin_type: {
    status: string;
    note: string;
    scientific_rationale?: string;
    supporting_sources?: string[];
  };
  views: Record<string, ViewResult>;
  safety: {
    disclaimer: string;
    model_info: {
      name: string;
      dataset: string;
      validation_accuracy: number;
      accuracy_note: string;
      region_note: string;
    };
    recommendation: string;
  };
}

export interface SourceItem {
  id: string;
  title: string;
  source: string;
  url: string;
  related_concerns: string[];
}

let inMemoryToken: string | null = null;

export function setInMemoryToken(token: string | null): void {
  inMemoryToken = token;
}

function getAuthHeader(): Record<string, string> {
  return inMemoryToken ? { Authorization: `Bearer ${inMemoryToken}` } : {};
}

function parseErrorMessage(errDetail: unknown, fallback: string): string {
  if (!errDetail) return fallback;
  if (typeof errDetail === 'string') return errDetail;
  if (typeof errDetail === 'object') {
    const obj = errDetail as Record<string, unknown>;
    const quality = obj.quality as { issues?: string[] } | undefined;
    if (quality?.issues?.length) {
      return `Image quality notice: ${quality.issues.join(', ')}`;
    }
    if (typeof obj.message === 'string') return obj.message;
    if (typeof obj.reason === 'string') return obj.reason;
    if (Array.isArray(errDetail)) {
      return errDetail.map((e) => (typeof e === 'object' && e && 'msg' in e ? String((e as Record<string, unknown>).msg) : JSON.stringify(e))).join('; ');
    }
    return JSON.stringify(errDetail);
  }
  return fallback;
}

export const api = {
  // Auth
  async register(email: string, password: string, full_name?: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(parseErrorMessage(err.detail, 'Registration failed'));
    }
    const data = await res.json();
    inMemoryToken = data.access_token || null;
    return data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
      throw new Error(parseErrorMessage(err.detail, 'Login failed'));
    }
    const data = await res.json();
    inMemoryToken = data.access_token || null;
    return data;
  },

  async logout(): Promise<void> {
    inMemoryToken = null;
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch {
      // Ignore network errors during logout
    }
  },

  async getMe(): Promise<User | null> {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        credentials: 'include',
        headers: getAuthHeader(),
      });
      if (!res.ok) {
        inMemoryToken = null;
        return null;
      }
      return await res.json();
    } catch {
      return null;
    }
  },

  // Assessments
  async createAssessment(capture_type = 'upload', views: string[] = ['front', 'left', 'right'], capture_modes?: Record<string, string>) {
    const res = await fetch(`${API_BASE}/assessments`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ capture_type, views, capture_modes }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to create assessment' }));
      throw new Error(err.detail || 'Assessment creation failed');
    }
    return res.json();
  },

  async uploadViewImage(assessmentId: string, view: 'front' | 'left' | 'right', file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/images?view=${view}`, {
      method: 'POST',
      credentials: 'include',
      headers: getAuthHeader(),
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Image upload failed' }));
      throw new Error(parseErrorMessage(err.detail, 'Image upload failed'));
    }
    return res.json();
  },

  async triggerAnalysis(assessmentId: string) {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/analyze`, {
      method: 'POST',
      credentials: 'include',
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(parseErrorMessage(err.detail, 'Analysis failed'));
    }
    return res.json();
  },

  async abandonAssessment(assessmentId: string): Promise<{ message: string; assessment_id: string; status: string }> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/abandon`, {
      method: 'POST',
      credentials: 'include',
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to abandon assessment' }));
      throw new Error(err.detail || 'Failed to abandon assessment');
    }
    return res.json();
  },

  async getResults(assessmentId: string): Promise<AssessmentResults> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/results`, {
      credentials: 'include',
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Could not fetch results' }));
      throw new Error(err.detail || 'Failed to fetch assessment results');
    }
    return res.json();
  },

  async getAssessmentHistory(): Promise<AssessmentHistoryItem[]> {
    const res = await fetch(`${API_BASE}/assessments/history`, {
      credentials: 'include',
      headers: getAuthHeader(),
    });
    if (!res.ok) return [];
    return res.json();
  },

  async renameAssessment(assessmentId: string, name: string): Promise<{ message: string; assessment_id: string; name: string }> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/rename`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ name }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to rename assessment' }));
      throw new Error(err.detail || 'Failed to rename assessment');
    }
    return res.json();
  },

  async deleteAssessment(assessmentId: string): Promise<{ message: string; assessment_id: string }> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to delete assessment' }));
      throw new Error(err.detail || 'Failed to delete assessment');
    }
    return res.json();
  },

  // Knowledge & Sources
  async getKnowledge(): Promise<ConcernKnowledge[]> {
    const res = await fetch(`${API_BASE}/knowledge`, {
      credentials: 'include',
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.concerns || [];
  },

  async getSources(): Promise<SourceItem[]> {
    const res = await fetch(`${API_BASE}/sources`, {
      credentials: 'include',
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.sources || [];
  },

  async getSafety() {
    const res = await fetch(`${API_BASE}/safety`, {
      credentials: 'include',
    });
    if (!res.ok) return null;
    return res.json();
  },

  async runGradcamDirect(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/xai/gradcam`, {
      method: 'POST',
      credentials: 'include',
      headers: getAuthHeader(),
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Visual analysis heatmap generation failed' }));
      throw new Error(err.detail || 'Visual analysis heatmap generation failed');
    }
    return res.json();
  },
};
