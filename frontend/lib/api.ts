const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface PropertyScore {
  wholesale_score: number | null;
  wholesale_equity_pct: number | null;
  wholesale_max_offer: number | null;
  wholesale_est_repairs: number | null;
  flip_score: number | null;
  flip_profit: number | null;
  flip_margin_pct: number | null;
  flip_max_offer: number | null;
  rental_score: number | null;
  rental_cap_rate: number | null;
  rental_monthly_rent: number | null;
  rental_annual_cashflow: number | null;
  airbnb_score: number | null;
  airbnb_nightly_rate: number | null;
  airbnb_monthly_revenue: number | null;
  airbnb_annual_yield: number | null;
  best_strategy: "wholesale" | "flip" | "rental" | "airbnb" | null;
  best_score: number | null;
}

export interface Property {
  id: number;
  zpid: string | null;
  address: string;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  latitude: number | null;
  longitude: number | null;
  beds: number | null;
  baths: number | null;
  sqft: number | null;
  year_built: number | null;
  property_type: string | null;
  asking_price: number | null;
  zestimate: number | null;
  price_per_sqft: number | null;
  days_on_market: number | null;
  estimated_rent: number | null;
  listing_url: string | null;
  photo_url: string | null;
  description: string | null;
  scores: PropertyScore | null;
}

export interface PropertyFilters {
  strategy?: string;
  min_score?: number;
  min_price?: number;
  max_price?: number;
  zip_code?: string;
  min_beds?: number;
  sort_by?: string;
  limit?: number;
  offset?: number;
}

export interface AdminStats {
  total_properties: number;
  scored: number;
  by_strategy: Record<string, number>;
}

export interface AppSettings {
  repair_cost_per_sqft: number;
  wholesale_good_equity_pct: number;
  wholesale_ok_equity_pct: number;
  flip_good_margin_pct: number;
  flip_ok_margin_pct: number;
  flip_min_profit_dollars: number;
  rental_good_cap_rate: number;
  rental_ok_cap_rate: number;
  rental_expense_ratio: number;
  airbnb_occupancy_rate: number;
  airbnb_nightly_rate_multiplier: number;
  airbnb_good_yield: number;
  airbnb_ok_yield: number;
  rent_per_sqft_fallback: number;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  getProperties: (filters: PropertyFilters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") params.set(k, String(v));
    });
    return apiFetch<Property[]>(`/properties/?${params}`);
  },

  getProperty: (id: number) => apiFetch<Property>(`/properties/${id}`),

  getStats: () => apiFetch<AdminStats>("/admin/stats"),

  triggerScrape: () =>
    apiFetch<{ status: string }>("/admin/scrape", { method: "POST" }),

  triggerScore: () =>
    apiFetch<{ status: string; scored: number }>("/admin/score", { method: "POST" }),

  getSettings: () => apiFetch<AppSettings>("/settings/"),

  updateSettings: (data: Partial<AppSettings>) =>
    apiFetch<{ status: string }>("/settings/", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  generateOffer: async (payload: object): Promise<Blob> => {
    const res = await fetch(`${API_BASE}/offers/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Offer error ${res.status}`);
    return res.blob();
  },
};
