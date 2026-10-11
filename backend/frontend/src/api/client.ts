/**
 * API client for Face Skin Assessment System backend.
 */

const API_BASE = '/api/v1';

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

export interface RegionConcern {
  concept: string;
  display_name: string;
  confidence: number;
  why_identified: string;
  why_it_can_occur: string;
  visual_evidence: string[];
  sources: Array<{
    title: string;
    source: string;
    url: string;
  }>;
}

export interface RegionData {
  valid: boolean;
  reason?: string;
  concern?: RegionConcern | null;
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

export interface AssessmentResults {
  assessment_id: string;
  status: string;
  capture_type: string;
  skin_type: {
    status: string;
    note: string;
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

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('derma_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function parseErrorMessage(errDetail: any, fallback: string): string {
  if (!errDetail) return fallback;
  if (typeof errDetail === 'string') return errDetail;
  if (typeof errDetail === 'object') {
    if (errDetail.quality?.issues?.length) {
      return `Image quality notice: ${errDetail.quality.issues.join(', ')}`;
    }
    if (errDetail.message) return errDetail.message;
    if (errDetail.reason) return errDetail.reason;
    if (Array.isArray(errDetail)) {
      return errDetail.map((e: any) => e.msg || JSON.stringify(e)).join('; ');
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(err.detail || 'Registration failed');
    }
    const data = await res.json();
    localStorage.setItem('derma_token', data.access_token);
    return data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    localStorage.setItem('derma_token', data.access_token);
    return data;
  },

  logout(): void {
    localStorage.removeItem('derma_token');
  },

  async getMe(): Promise<User | null> {
    const token = localStorage.getItem('derma_token');
    if (!token) return null;
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      localStorage.removeItem('derma_token');
      return null;
    }
    return res.json();
  },

  // Assessments
  async createAssessment(capture_type = 'upload', views = ['front', 'left', 'right']) {
    const res = await fetch(`${API_BASE}/assessments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ capture_type, views }),
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
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(parseErrorMessage(err.detail, 'Analysis failed'));
    }
    return res.json();
  },

  async getResults(assessmentId: string): Promise<AssessmentResults> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/results`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Could not fetch results' }));
      throw new Error(err.detail || 'Failed to fetch assessment results');
    }
    return res.json();
  },

  async getAssessmentHistory() {
    const res = await fetch(`${API_BASE}/assessments/history`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) return [];
    return res.json();
  },

  // Knowledge & Sources
  async getKnowledge(): Promise<ConcernKnowledge[]> {
    const res = await fetch(`${API_BASE}/knowledge`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.concerns || [];
  },

  async getSources(): Promise<SourceItem[]> {
    const res = await fetch(`${API_BASE}/sources`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.sources || [];
  },

  async getSafety() {
    const res = await fetch(`${API_BASE}/safety`);
    if (!res.ok) return null;
    return res.json();
  },

  async runGradcamDirect(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/xai/gradcam`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Visual analysis heatmap generation failed' }));
      throw new Error(err.detail || 'Visual analysis heatmap generation failed');
    }
    return res.json();
  },
};
