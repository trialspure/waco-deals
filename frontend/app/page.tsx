"use client";
import { useEffect, useState, useCallback } from "react";
import { api, Property, PropertyFilters } from "@/lib/api";
import PropertyCard from "@/components/PropertyCard";
import { Search, SlidersHorizontal, Bookmark } from "lucide-react";

const STRATEGIES = [
  { value: "", label: "All Strategies" },
  { value: "wholesale", label: "Wholesale" },
  { value: "flip", label: "Fix & Flip" },
  { value: "rental", label: "Long-Term Rental" },
  { value: "airbnb", label: "Airbnb / STR" },
];

const SORT_OPTIONS = [
  { value: "best_score", label: "Best Score" },
  { value: "asking_price", label: "Price: Low to High" },
  { value: "days_on_market", label: "Newest Listings" },
];

const WACO_ZIPS = ["", "76701", "76702", "76703", "76704", "76705", "76706", "76707", "76708", "76710", "76711", "76712"];

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<{ total_properties: number; scored: number; by_strategy: Record<string, number> } | null>(null);
  const [tab, setTab] = useState<"all" | "saved">("all");

  const [filters, setFilters] = useState<PropertyFilters>({
    strategy: "",
    sort_by: "best_score",
    limit: 50,
  });
  const [maxPrice, setMaxPrice] = useState("");
  const [minBeds, setMinBeds] = useState("");
  const [zipCode, setZipCode] = useState("");
  const [minScore, setMinScore] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const f: PropertyFilters = { ...filters };
      if (maxPrice) f.max_price = parseFloat(maxPrice);
      if (minBeds) f.min_beds = parseFloat(minBeds);
      if (zipCode) f.zip_code = zipCode;
      if (minScore) f.min_score = parseFloat(minScore);
      if (tab === "saved") f.saved_only = true;
      const data = await api.getProperties(f);
      setProperties(data);
    } catch {
      setError("Could not connect to backend. Make sure the FastAPI server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }, [filters, maxPrice, minBeds, zipCode, minScore, tab]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    api.getStats().then(setStats).catch(() => {});
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Stats bar */}
      {stats && (
        <div className="flex flex-wrap gap-4 mb-6">
          <StatChip label="Total listings" value={stats.total_properties} />
          <StatChip label="Scored" value={stats.scored} />
          <StatChip label="Wholesale" value={stats.by_strategy.wholesale ?? 0} color="purple" />
          <StatChip label="Fix & Flip" value={stats.by_strategy.flip ?? 0} color="orange" />
          <StatChip label="Rental" value={stats.by_strategy.rental ?? 0} color="blue" />
          <StatChip label="Airbnb" value={stats.by_strategy.airbnb ?? 0} color="green" />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setTab("all")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "all"
              ? "bg-blue-600 text-white"
              : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
          }`}
        >
          All Properties
        </button>
        <button
          onClick={() => setTab("saved")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            tab === "saved"
              ? "bg-amber-500 text-white"
              : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
          }`}
        >
          <Bookmark size={14} className={tab === "saved" ? "fill-white" : ""} />
          Saved
        </button>
      </div>

      {/* Filter bar */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <SlidersHorizontal size={16} className="text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Filters</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <select
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
            value={filters.strategy}
            onChange={(e) => setFilters((f) => ({ ...f, strategy: e.target.value }))}
          >
            {STRATEGIES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>

          <select
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
            value={zipCode}
            onChange={(e) => setZipCode(e.target.value)}
          >
            {WACO_ZIPS.map((z) => (
              <option key={z} value={z}>{z || "All ZIPs"}</option>
            ))}
          </select>

          <input
            type="number"
            placeholder="Max price ($)"
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
          />

          <input
            type="number"
            placeholder="Min beds"
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
            value={minBeds}
            onChange={(e) => setMinBeds(e.target.value)}
          />

          <input
            type="number"
            placeholder="Min score (1-10)"
            step="0.5"
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
          />

          <select
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
            value={filters.sort_by}
            onChange={(e) => setFilters((f) => ({ ...f, sort_by: e.target.value }))}
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Results */}
      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700 mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 h-80 animate-pulse" />
          ))}
        </div>
      ) : properties.length === 0 ? (
        <EmptyState saved={tab === "saved"} />
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">{properties.length} {tab === "saved" ? "saved" : ""} properties</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {properties.map((p) => (
              <PropertyCard key={p.id} property={p} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function StatChip({ label, value, color }: { label: string; value: number; color?: string }) {
  const colorMap: Record<string, string> = {
    purple: "bg-purple-50 text-purple-700",
    orange: "bg-orange-50 text-orange-700",
    blue: "bg-blue-50 text-blue-700",
    green: "bg-green-50 text-green-700",
  };
  return (
    <div className={`rounded-lg px-3 py-2 text-center ${color ? colorMap[color] : "bg-gray-100 text-gray-700"}`}>
      <div className="text-xl font-bold">{value.toLocaleString()}</div>
      <div className="text-xs">{label}</div>
    </div>
  );
}

function EmptyState({ saved }: { saved?: boolean }) {
  return (
    <div className="text-center py-20">
      {saved ? (
        <Bookmark size={40} className="mx-auto text-gray-300 mb-4" />
      ) : (
        <Search size={40} className="mx-auto text-gray-300 mb-4" />
      )}
      <h3 className="text-lg font-medium text-gray-700 mb-2">
        {saved ? "No saved properties yet" : "No properties found"}
      </h3>
      <p className="text-sm text-gray-500 max-w-sm mx-auto">
        {saved
          ? "Click the bookmark icon on any property card to save it here."
          : <>Click <strong>Refresh Listings</strong> in the header to scrape Waco listings, or adjust your filters.</>}
      </p>
    </div>
  );
}
