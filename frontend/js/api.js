/**
 * frontend/js/api.js - RetinaAI Client API Service
 */

const API = {
  baseUrl: '',

  async getScreenings() {
    const res = await fetch(`${this.baseUrl}/api/screenings`);
    if (!res.ok) throw new Error('Failed to fetch screenings');
    return await res.json();
  },

  async getScreeningDetail(id) {
    const res = await fetch(`${this.baseUrl}/api/screenings/${id}`);
    if (!res.ok) throw new Error('Failed to fetch screening detail');
    return await res.json();
  },

  async getSamples() {
    const res = await fetch(`${this.baseUrl}/api/samples`);
    if (!res.ok) throw new Error('Failed to fetch samples');
    return await res.json();
  },

  async screenImage(payload) {
    let options = {};
    if (payload instanceof FormData) {
      options = {
        method: 'POST',
        body: payload
      };
    } else {
      options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      };
    }
    const res = await fetch(`${this.baseUrl}/api/screen`, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Screening request failed');
    }
    return await res.json();
  },

  async submitDoctorReview(reviewData) {
    const res = await fetch(`${this.baseUrl}/api/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reviewData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to submit doctor review');
    }
    return await res.json();
  },

  async runSimulation(scenario = 'scenario_a', overrides = {}) {
    const res = await fetch(`${this.baseUrl}/api/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario, overrides })
    });
    if (!res.ok) throw new Error('Simulation run failed');
    return await res.json();
  },

  async getSimulationComparison() {
    const res = await fetch(`${this.baseUrl}/api/simulate/comparison`);
    if (!res.ok) throw new Error('Failed to fetch simulation comparison');
    return await res.json();
  }
};
