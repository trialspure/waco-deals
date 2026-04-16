import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const STRATEGY_CONFIG = {
  wholesale: {
    label: "Wholesale",
    color: "bg-purple-100 text-purple-800",
    mapColor: "#9333ea",
    description: "Buy deep below market, assign to another investor",
  },
  flip: {
    label: "Fix & Flip",
    color: "bg-orange-100 text-orange-800",
    mapColor: "#f97316",
    description: "Renovate and resell for profit",
  },
  rental: {
    label: "Long-Term Rental",
    color: "bg-blue-100 text-blue-800",
    mapColor: "#3b82f6",
    description: "Buy and hold for monthly rental income",
  },
  airbnb: {
    label: "Airbnb / STR",
    color: "bg-green-100 text-green-800",
    mapColor: "#22c55e",
    description: "Short-term rental for higher nightly returns",
  },
} as const;

export function formatCurrency(val: number | null | undefined): string {
  if (val == null) return "N/A";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(val);
}

export function formatPct(val: number | null | undefined): string {
  if (val == null) return "N/A";
  return `${val.toFixed(1)}%`;
}

export function scoreColor(score: number | null): string {
  if (score == null) return "text-gray-400";
  if (score >= 8) return "text-green-600";
  if (score >= 5) return "text-yellow-600";
  return "text-red-500";
}

export function scoreBg(score: number | null): string {
  if (score == null) return "bg-gray-100 text-gray-500";
  if (score >= 8) return "bg-green-100 text-green-800";
  if (score >= 5) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}
