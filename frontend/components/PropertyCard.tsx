"use client";
import { useState } from "react";
import Link from "next/link";
import { api, Property } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import ScoreBadge from "./ScoreBadge";
import StrategyBadge from "./StrategyBadge";
import { Bed, Bath, Square, MapPin, ExternalLink, Bookmark, Phone } from "lucide-react";

interface Props {
  property: Property;
}

export default function PropertyCard({ property: p }: Props) {
  const s = p.scores;
  const [saved, setSaved] = useState(p.is_saved);
  const [saving, setSaving] = useState(false);

  const handleSave = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setSaving(true);
    try {
      const updated = await api.toggleSave(p.id);
      setSaved(updated.is_saved);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      {p.photo_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={p.photo_url}
          alt={p.address}
          className="w-full h-44 object-cover"
        />
      ) : (
        <div className="w-full h-44 bg-gray-100 flex items-center justify-center text-gray-400 text-sm">
          No photo
        </div>
      )}

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="min-w-0">
            <p className="font-semibold text-base leading-tight">{p.address}</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-0.5">
              <MapPin size={12} />
              {p.city}, {p.state} {p.zip_code}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            <ScoreBadge score={s?.best_score ?? null} />
            <StrategyBadge strategy={s?.best_strategy} size="sm" />
          </div>
        </div>

        {/* Price */}
        <p className="text-2xl font-bold text-gray-900 mb-3">
          {formatCurrency(p.asking_price)}
        </p>

        {/* Details row */}
        <div className="flex items-center gap-3 text-sm text-gray-500 mb-3">
          {p.beds != null && (
            <span className="flex items-center gap-1">
              <Bed size={14} />
              {p.beds}bd
            </span>
          )}
          {p.baths != null && (
            <span className="flex items-center gap-1">
              <Bath size={14} />
              {p.baths}ba
            </span>
          )}
          {p.sqft != null && (
            <span className="flex items-center gap-1">
              <Square size={14} />
              {p.sqft.toLocaleString()} sqft
            </span>
          )}
          {p.days_on_market != null && (
            <span className="ml-auto text-xs">{p.days_on_market}d on market</span>
          )}
        </div>

        {/* Agent contact */}
        {(p.agent_name || p.agent_phone) && (
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-3 bg-gray-50 rounded-lg px-2 py-1.5">
            <span className="truncate">{p.agent_name || "Agent"}</span>
            {p.agent_phone && (
              <a
                href={`tel:${p.agent_phone}`}
                onClick={(e) => e.stopPropagation()}
                className="flex items-center gap-1 text-blue-600 hover:underline ml-auto shrink-0"
              >
                <Phone size={11} />
                {p.agent_phone}
              </a>
            )}
          </div>
        )}

        {/* Mini score row */}
        {s && (
          <div className="grid grid-cols-4 gap-1 text-center mb-4">
            {(["wholesale", "flip", "rental", "airbnb"] as const).map((key) => {
              const scoreKey = `${key}_score` as keyof typeof s;
              const score = s[scoreKey] as number | null;
              const labels = { wholesale: "WS", flip: "F&F", rental: "LTR", airbnb: "STR" };
              return (
                <div key={key} className="bg-gray-50 rounded-lg py-1.5">
                  <div className="text-xs text-gray-400 mb-0.5">{labels[key]}</div>
                  <ScoreBadge score={score} size="sm" />
                </div>
              );
            })}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <Link
            href={`/properties/${p.id}`}
            className="flex-1 text-center py-2 px-3 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            View Analysis
          </Link>
          <button
            onClick={handleSave}
            disabled={saving}
            title={saved ? "Remove from saved" : "Save property"}
            className={`p-2 rounded-lg border transition-colors ${
              saved
                ? "bg-amber-50 border-amber-300 text-amber-500 hover:bg-amber-100"
                : "border-gray-200 text-gray-400 hover:bg-gray-50"
            }`}
          >
            <Bookmark size={16} className={saved ? "fill-amber-400" : ""} />
          </button>
          {p.listing_url && (
            <a
              href={p.listing_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              title="View on Zillow"
            >
              <ExternalLink size={16} className="text-gray-500" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
