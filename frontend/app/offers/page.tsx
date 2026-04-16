"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { api, Property } from "@/lib/api";
import { formatCurrency, STRATEGY_CONFIG } from "@/lib/utils";
import { Download, FileText } from "lucide-react";

const STRATEGY_OPTIONS = [
  { value: "wholesale", label: "Wholesale / Cash Assignment" },
  { value: "flip", label: "Fix & Flip" },
  { value: "rental", label: "Long-Term Rental" },
  { value: "airbnb", label: "Airbnb / Short-Term Rental" },
];

function OfferForm() {
  const searchParams = useSearchParams();
  const preselectedId = searchParams.get("property_id");

  const [properties, setProperties] = useState<Property[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    property_id: preselectedId || "",
    buyer_name: "",
    buyer_address: "",
    buyer_phone: "",
    buyer_email: "",
    strategy: "wholesale",
    offer_price: "",
    earnest_money: "1000",
    closing_days: "21",
    inspection_days: "10",
    notes: "",
  });

  // Load property list
  useEffect(() => {
    setLoading(true);
    api.getProperties({ limit: 200, sort_by: "best_score" })
      .then(setProperties)
      .catch(() => setError("Failed to load properties"))
      .finally(() => setLoading(false));
  }, []);

  // Load preselected property
  useEffect(() => {
    if (preselectedId && properties.length > 0) {
      const p = properties.find((p) => String(p.id) === preselectedId);
      if (p) {
        setSelectedProperty(p);
        setForm((f) => ({
          ...f,
          property_id: preselectedId,
          strategy: p.scores?.best_strategy || "wholesale",
          offer_price: p.scores?.wholesale_max_offer
            ? String(Math.round(p.scores.wholesale_max_offer))
            : p.asking_price ? String(Math.round(p.asking_price * 0.85)) : "",
        }));
      }
    }
  }, [preselectedId, properties]);

  function handlePropertyChange(id: string) {
    const p = properties.find((p) => String(p.id) === id);
    setSelectedProperty(p || null);
    const strategy = p?.scores?.best_strategy || "wholesale";
    const maxOffer = strategy === "wholesale"
      ? p?.scores?.wholesale_max_offer
      : strategy === "flip"
      ? p?.scores?.flip_max_offer
      : p?.asking_price ? p.asking_price * 0.9 : undefined;
    setForm((f) => ({
      ...f,
      property_id: id,
      strategy,
      offer_price: maxOffer ? String(Math.round(maxOffer)) : "",
    }));
  }

  function handleStrategyChange(strategy: string) {
    const p = selectedProperty;
    const maxOffer = strategy === "wholesale"
      ? p?.scores?.wholesale_max_offer
      : strategy === "flip"
      ? p?.scores?.flip_max_offer
      : p?.asking_price ? p.asking_price * 0.9 : undefined;
    setForm((f) => ({
      ...f,
      strategy,
      offer_price: maxOffer ? String(Math.round(maxOffer)) : f.offer_price,
    }));
  }

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.property_id || !form.buyer_name || !form.offer_price) {
      setError("Please fill in all required fields.");
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      const payload = {
        property_id: parseInt(form.property_id),
        buyer_name: form.buyer_name,
        buyer_address: form.buyer_address,
        buyer_phone: form.buyer_phone,
        buyer_email: form.buyer_email,
        strategy: form.strategy,
        offer_price: parseFloat(form.offer_price),
        earnest_money: parseFloat(form.earnest_money) || 1000,
        closing_days: parseInt(form.closing_days) || 21,
        inspection_days: parseInt(form.inspection_days) || 10,
        notes: form.notes,
      };
      const blob = await api.generateOffer(payload);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `offer_${form.property_id}_${form.strategy}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Failed to generate offer letter. Make sure the backend is running.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center gap-3 mb-6">
        <FileText size={24} className="text-blue-600" />
        <h1 className="text-2xl font-bold">Generate Offer Letter</h1>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700 mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleGenerate} className="space-y-6">
        {/* Property selection */}
        <section className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold mb-4">Property</h2>
          <select
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm bg-white"
            value={form.property_id}
            onChange={(e) => handlePropertyChange(e.target.value)}
            disabled={loading}
          >
            <option value="">— Select a property —</option>
            {properties.map((p) => (
              <option key={p.id} value={p.id}>
                {p.address} — {formatCurrency(p.asking_price)}
              </option>
            ))}
          </select>

          {selectedProperty && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg text-sm">
              <div className="font-medium">{selectedProperty.address}</div>
              <div className="text-gray-500 mt-1 flex flex-wrap gap-3">
                <span>Asking: {formatCurrency(selectedProperty.asking_price)}</span>
                {selectedProperty.scores?.best_strategy && (
                  <span>Best: <span className={`font-medium ${STRATEGY_CONFIG[selectedProperty.scores.best_strategy as keyof typeof STRATEGY_CONFIG]?.color?.split(" ")[1]}`}>
                    {STRATEGY_CONFIG[selectedProperty.scores.best_strategy as keyof typeof STRATEGY_CONFIG]?.label}
                  </span></span>
                )}
                {selectedProperty.scores?.best_score && (
                  <span>Score: <strong>{selectedProperty.scores.best_score.toFixed(1)}</strong></span>
                )}
              </div>
            </div>
          )}
        </section>

        {/* Buyer info */}
        <section className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold mb-4">Buyer Information</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
              <input
                required
                type="text"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.buyer_name}
                onChange={(e) => setForm((f) => ({ ...f, buyer_name: e.target.value }))}
                placeholder="John Smith"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Mailing Address</label>
              <input
                type="text"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.buyer_address}
                onChange={(e) => setForm((f) => ({ ...f, buyer_address: e.target.value }))}
                placeholder="123 Main St, Waco, TX 76701"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                type="tel"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.buyer_phone}
                onChange={(e) => setForm((f) => ({ ...f, buyer_phone: e.target.value }))}
                placeholder="(254) 555-0100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.buyer_email}
                onChange={(e) => setForm((f) => ({ ...f, buyer_email: e.target.value }))}
                placeholder="john@example.com"
              />
            </div>
          </div>
        </section>

        {/* Offer terms */}
        <section className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold mb-4">Offer Terms</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Investment Strategy</label>
              <select
                className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm bg-white"
                value={form.strategy}
                onChange={(e) => handleStrategyChange(e.target.value)}
              >
                {STRATEGY_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Offer Price ($) *</label>
              <input
                required
                type="number"
                step="1000"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.offer_price}
                onChange={(e) => setForm((f) => ({ ...f, offer_price: e.target.value }))}
                placeholder="150000"
              />
              {selectedProperty?.scores?.wholesale_max_offer && form.strategy === "wholesale" && (
                <p className="text-xs text-gray-400 mt-1">
                  Suggested max (70% rule): {formatCurrency(selectedProperty.scores.wholesale_max_offer)}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Earnest Money ($)</label>
              <input
                type="number"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.earnest_money}
                onChange={(e) => setForm((f) => ({ ...f, earnest_money: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Close in (days)</label>
              <input
                type="number"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.closing_days}
                onChange={(e) => setForm((f) => ({ ...f, closing_days: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Inspection period (days)</label>
              <input
                type="number"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.inspection_days}
                onChange={(e) => setForm((f) => ({ ...f, inspection_days: e.target.value }))}
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Additional Notes</label>
              <textarea
                rows={3}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none"
                value={form.notes}
                onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
                placeholder="As-is condition, seller to provide clear title…"
              />
            </div>
          </div>
        </section>

        <button
          type="submit"
          disabled={generating}
          className="w-full flex items-center justify-center gap-2 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Download size={18} />
          {generating ? "Generating PDF…" : "Download Offer Letter PDF"}
        </button>
      </form>
    </div>
  );
}

export default function OffersPage() {
  return (
    <Suspense fallback={<div className="max-w-3xl mx-auto px-4 py-8 text-gray-500">Loading…</div>}>
      <OfferForm />
    </Suspense>
  );
}
