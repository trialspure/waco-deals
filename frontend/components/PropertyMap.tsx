"use client";
import { useEffect, useRef } from "react";
import { Property } from "@/lib/api";
import { STRATEGY_CONFIG, formatCurrency } from "@/lib/utils";

interface Props {
  properties: Property[];
}

// Leaflet must be loaded client-side only
export default function PropertyMap({ properties }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Dynamic import to avoid SSR issues
    import("leaflet").then((L) => {
      // Fix default icon paths broken by bundlers
      // @ts-expect-error - leaflet internals
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      // Center on Waco
      const map = L.map(mapRef.current!).setView([31.5493, -97.1467], 12);
      mapInstanceRef.current = map;

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
      }).addTo(map);

      // Add markers
      properties.forEach((p) => {
        if (!p.latitude || !p.longitude) return;
        const strategy = p.scores?.best_strategy;
        const color = strategy
          ? STRATEGY_CONFIG[strategy as keyof typeof STRATEGY_CONFIG]?.mapColor
          : "#6b7280";

        const icon = L.divIcon({
          className: "",
          html: `<div style="
            width:28px;height:28px;border-radius:50% 50% 50% 0;
            background:${color};border:2px solid white;
            transform:rotate(-45deg);box-shadow:0 1px 4px rgba(0,0,0,0.3);
          "><span style="
            display:block;transform:rotate(45deg);
            color:white;font-size:10px;font-weight:bold;
            text-align:center;line-height:24px;
          ">${p.scores?.best_score?.toFixed(0) ?? "?"}</span></div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 28],
          popupAnchor: [0, -28],
        });

        const strategyLabel = strategy
          ? STRATEGY_CONFIG[strategy as keyof typeof STRATEGY_CONFIG]?.label
          : p.listing_type === "rent"
          ? "Acquisition Target"
          : "Unscored";

        const isFacebook = p.source === "facebook_marketplace";
        const sourceLabel = isFacebook ? "FB Marketplace" : "Zillow";
        const sourceBg = isFacebook ? "#dbeafe" : "#f3f4f6";
        const sourceFg = isFacebook ? "#1d4ed8" : "#374151";

        const priceHtml =
          p.listing_type === "rent" && p.estimated_rent
            ? `${formatCurrency(p.estimated_rent)}/mo rent`
            : formatCurrency(p.asking_price);

        const popup = `
          <div style="font-family:system-ui,sans-serif;min-width:200px">
            <p style="font-weight:600;margin:0 0 4px">${p.address}</p>
            <p style="font-size:18px;font-weight:700;margin:0 0 4px">${priceHtml}</p>
            <p style="font-size:12px;color:#666;margin:0 0 8px">${p.beds ?? "?"}bd / ${p.baths ?? "?"}ba · ${p.sqft?.toLocaleString() ?? "?"} sqft</p>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap">
              <span style="background:${color};color:white;border-radius:9999px;padding:2px 8px;font-size:11px;font-weight:600">${strategyLabel}</span>
              ${p.scores?.best_score != null ? `<span style="font-size:12px">Score: <strong>${p.scores.best_score.toFixed(1)}</strong></span>` : ""}
              <span style="background:${sourceBg};color:${sourceFg};border-radius:4px;padding:2px 6px;font-size:10px;font-weight:600">${sourceLabel}</span>
            </div>
            <a href="/properties/${p.id}" style="display:block;text-align:center;background:#2563eb;color:white;border-radius:6px;padding:6px;font-size:12px;font-weight:600;text-decoration:none">
              View Analysis →
            </a>
          </div>
        `;
        L.marker([p.latitude, p.longitude], { icon }).addTo(map).bindPopup(popup);
      });
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update markers when properties change (re-mount approach: remove and re-add)
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    // Markers are added once on mount; full re-mount on property change is handled by key prop
  }, [properties]);

  return <div ref={mapRef} style={{ height: "100%", width: "100%" }} />;
}
