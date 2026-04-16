"use client";
import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import { api, Property } from "@/lib/api";
import { STRATEGY_CONFIG } from "@/lib/utils";
import "leaflet/dist/leaflet.css";

// Import map client-side only to avoid SSR issues with window
const PropertyMap = dynamic(() => import("@/components/PropertyMap"), { ssr: false });

const STRATEGIES = Object.entries(STRATEGY_CONFIG).map(([value, cfg]) => ({
  value,
  label: cfg.label,
  color: cfg.mapColor,
}));

export default function MapPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [mapKey, setMapKey] = useState(0);

  useEffect(() => {
    api.getProperties({ limit: 200, sort_by: "best_score" })
      .then(setProperties)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter
    ? properties.filter((p) => p.scores?.best_strategy === filter)
    : properties;

  function handleFilterChange(value: string) {
    setFilter(value);
    setMapKey((k) => k + 1); // remount map to refresh markers
  }

  return (
    <div className="flex flex-col h-[calc(100vh-56px)]">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center gap-4 shrink-0">
        <span className="text-sm font-medium text-gray-700">
          {filtered.length} properties
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleFilterChange("")}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filter === "" ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            All
          </button>
          {STRATEGIES.map(({ value, label, color }) => (
            <button
              key={value}
              onClick={() => handleFilterChange(value)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors`}
              style={
                filter === value
                  ? { backgroundColor: color, color: "white" }
                  : { backgroundColor: "#f3f4f6", color: "#4b5563" }
              }
            >
              {label}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div className="ml-auto flex items-center gap-3 text-xs text-gray-500">
          {STRATEGIES.map(({ value, label, color }) => (
            <span key={value} className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: color }} />
              {label}
            </span>
          ))}
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500 bg-gray-50">
            Loading properties…
          </div>
        ) : (
          <PropertyMap key={mapKey} properties={filtered} />
        )}
      </div>
    </div>
  );
}
