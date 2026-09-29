import {
  VerificationRequest,
  VerificationResponse,
  ParsedAddress,
  NormalizedAddress,
  StructuredAddressRequest,
} from '../types';

const API_BASE = '/api';

export const api = {
  async verifyAddress(request: VerificationRequest): Promise<VerificationResponse> {
    const res = await fetch(`${API_BASE}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Verification failed' }));
      throw new Error(err.detail || 'Failed to verify address');
    }
    return res.json();
  },

  async parseAddress(address: string): Promise<ParsedAddress> {
    const res = await fetch(`${API_BASE}/address/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address }),
    });
    if (!res.ok) throw new Error('Failed to parse address');
    return res.json();
  },

  async normalizeAddress(structured: StructuredAddressRequest): Promise<NormalizedAddress> {
    const res = await fetch(`${API_BASE}/address/normalize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(structured),
    });
    if (!res.ok) throw new Error('Failed to normalize address');
    return res.json();
  },

  async getHistory(limit = 20): Promise<VerificationResponse[]> {
    const res = await fetch(`${API_BASE}/address/history?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch verification history');
    return res.json();
  },

  async getVerificationById(id: string): Promise<VerificationResponse> {
    const res = await fetch(`${API_BASE}/address/${id}`);
    if (!res.ok) throw new Error('Failed to fetch verification details');
    return res.json();
  },

  async getHealth(): Promise<{ status: string; app_name: string; version: string; geocoder_provider: string }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  },
};
