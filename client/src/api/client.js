const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export class ApiClient {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Personal Analytics
  async getYearActivity(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/year-activity?${params}`);
  }

  async getLanguageStats(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/language-stats?${params}`);
  }

  async getContributionTrend(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/contribution-trend?${params}`);
  }

  async getTopProjects(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/top-projects?${params}`);
  }

  async getTeamCollaborators(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/team-collaborators?${params}`);
  }

  async getProductivityInsights(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/productivity-insights?${params}`);
  }

  async getWorkPatterns(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/work-patterns?${params}`);
  }

  async getCodeQualityMetrics(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/code-quality?${params}`);
  }

  async getPersonalRecommendations(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/recommendations?${params}`);
  }

  async getAchievements(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/achievements?${params}`);
  }

  async getMentorshipStats(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/mentorship-stats?${params}`);
  }

  async getSkillsGrowth(email) {
    const params = new URLSearchParams({ email });
    return this.request(`/personal/skills-growth?${params}`);
  }
}

export default new ApiClient();
