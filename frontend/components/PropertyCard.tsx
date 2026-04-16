import Link from "next/link";
import { Property } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import ScoreBadge from "./ScoreBadge";
import StrategyBadge from "./StrategyBadge";
import { Bed, Bath, Square, MapPin, ExternalLink } from "lucide-react";

interface Props {
  property: Property;
}

export default function PropertyCard({ property: p }: Props) {
  const s = p.scores;

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
          <div>
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
        <div className="flex items-center gap-3 text-sm text-gray-500 mb-4">
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
