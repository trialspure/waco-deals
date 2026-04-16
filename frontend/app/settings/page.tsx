"use client";
import { useEffect, useState } from "react";
import { api, AppSettings } from "@/lib/api";
import { Settings, Save, RotateCcw } from "lucide-react";

type SettingField = {
  key: keyof AppSettings;
  label: string;
  description: string;
  unit: string;
  min: number;
  max: number;
  step: number;
};

const SETTING_GROUPS: { title: string; fields: SettingField[] }[] = [
  {
    title: "Repair Costs",
    fields: [
      { key: "repair_cost_per_sqft", label: "Repair Cost / sqft", description: "Used to estimate renovation costs for wholesale and flip scoring", unit: "$/sqft", min: 5, max: 150, step: 5 },
    ],
  },
  {
    title: "Wholesale Thresholds",
    fields: [
      { key: "wholesale_good_equity_pct", label: "Good equity %", description: "Equity % threshold for a score of 8–10", unit: "%", min: 10, max: 60, step: 5 },
      { key: "wholesale_ok_equity_pct", label: "OK equity %", description: "Equity % threshold for a score of 5–7", unit: "%", min: 5, max: 40, step: 5 },
    ],
  },
  {
    title: "Fix & Flip Thresholds",
    fields: [
      { key: "flip_good_margin_pct", label: "Good margin %", description: "Profit margin % for a score of 8–10", unit: "%", min: 10, max: 40, step: 5 },
      { key: "flip_ok_margin_pct", label: "OK margin %", description: "Profit margin % for a score of 5–7", unit: "%", min: 5, max: 25, step: 5 },
      { key: "flip_min_profit_dollars", label: "Minimum profit ($)", description: "Absolute minimum profit to score 8+", unit: "$", min: 5000, max: 50000, step: 1000 },
    ],
  },
  {
    title: "Long-Term Rental Thresholds",
    fields: [
      { key: "rental_good_cap_rate", label: "Good cap rate %", description: "Cap rate for a score of 8–10", unit: "%", min: 4, max: 15, step: 0.5 },
      { key: "rental_ok_cap_rate", label: "OK cap rate %", description: "Cap rate for a score of 5–7", unit: "%", min: 2, max: 10, step: 0.5 },
      { key: "rental_expense_ratio", label: "Expense ratio", description: "Fraction of annual rent allocated to expenses (0.5 = 50%)", unit: "ratio", min: 0.3, max: 0.7, step: 0.05 },
      { key: "rent_per_sqft_fallback", label: "Rent fallback ($/sqft)", description: "Used when RentCast data isn't available", unit: "$/sqft", min: 0.5, max: 3, step: 0.1 },
    ],
  },
  {
    title: "Airbnb / STR Thresholds",
    fields: [
      { key: "airbnb_occupancy_rate", label: "Occupancy rate", description: "Estimated occupancy fraction for Waco STRs", unit: "ratio", min: 0.2, max: 0.9, step: 0.05 },
      { key: "airbnb_nightly_rate_multiplier", label: "STR rate multiplier", description: "Nightly rate = (Monthly LTR rent × multiplier) / 30", unit: "×", min: 1, max: 3, step: 0.1 },
      { key: "airbnb_good_yield", label: "Good gross yield %", description: "Annual STR yield for a score of 8–10", unit: "%", min: 6, max: 25, step: 1 },
      { key: "airbnb_ok_yield", label: "OK gross yield %", description: "Annual STR yield for a score of 5–7", unit: "%", min: 4, max: 15, step: 1 },
    ],
  },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [draft, setDraft] = useState<AppSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getSettings()
      .then((s) => { setSettings(s); setDraft(s); })
      .catch(() => setError("Could not load settings. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  function handleChange(key: keyof AppSettings, value: string) {
    setDraft((d) => d ? { ...d, [key]: parseFloat(value) } : d);
  }

  async function handleSave() {
    if (!draft) return;
    setSaving(true);
    setError(null);
    try {
      await api.updateSettings(draft);
      setSettings(draft);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      setError("Failed to save settings.");
    } finally {
      setSaving(false);
    }
  }

  function handleReset() {
    if (settings) setDraft({ ...settings });
  }

  if (loading) return <div className="max-w-3xl mx-auto px-4 py-8 text-gray-500">Loading…</div>;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Settings size={24} className="text-gray-600" />
          <h1 className="text-2xl font-bold">Scoring Settings</h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 transition-colors"
          >
            <RotateCcw size={14} /> Reset
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Save size={14} />
            {saving ? "Saving…" : saved ? "Saved!" : "Save Changes"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700 mb-6">
          {error}
        </div>
      )}

      <p className="text-sm text-gray-500 mb-6">
        Adjust scoring thresholds to match your investment criteria. After saving, click{" "}
        <strong>Re-score</strong> on the dashboard to recalculate all property scores.
      </p>

      {draft && SETTING_GROUPS.map((group) => (
        <div key={group.title} className="bg-white rounded-xl border border-gray-200 p-5 mb-4">
          <h2 className="font-semibold text-base mb-4">{group.title}</h2>
          <div className="space-y-4">
            {group.fields.map((field) => {
              const val = draft[field.key] as number;
              return (
                <div key={field.key}>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-sm font-medium text-gray-700">{field.label}</label>
                    <div className="flex items-center gap-1">
                      <input
                        type="number"
                        step={field.step}
                        min={field.min}
                        max={field.max}
                        className="w-20 border border-gray-200 rounded-md px-2 py-1 text-sm text-right"
                        value={val}
                        onChange={(e) => handleChange(field.key, e.target.value)}
                      />
                      <span className="text-xs text-gray-400 w-10">{field.unit}</span>
                    </div>
                  </div>
                  <input
                    type="range"
                    min={field.min}
                    max={field.max}
                    step={field.step}
                    value={val}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <p className="text-xs text-gray-400 mt-1">{field.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
