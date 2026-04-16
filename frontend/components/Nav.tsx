"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Home, Map, FileText, Settings, RefreshCw } from "lucide-react";
import { useState } from "react";
import { api } from "@/lib/api";

const links = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/map", label: "Map", icon: Map },
  { href: "/offers", label: "Make Offer", icon: FileText },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Nav() {
  const pathname = usePathname();
  const [scraping, setScraping] = useState(false);

  async function handleScrape() {
    setScraping(true);
    try {
      await api.triggerScrape();
      alert("Scrape started! Refresh in a minute to see new listings.");
    } catch {
      alert("Could not reach the backend. It may be waking up — please try again in 30 seconds.");
    } finally {
      setScraping(false);
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
        <div className="flex items-center gap-6">
          <span className="font-bold text-lg tracking-tight">
            Waco Deals
          </span>
          <nav className="flex items-center gap-1">
            {links.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                  pathname === href
                    ? "bg-gray-100 text-gray-900"
                    : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                )}
              >
                <Icon size={15} />
                {label}
              </Link>
            ))}
          </nav>
        </div>
        <button
          onClick={handleScrape}
          disabled={scraping}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw size={14} className={scraping ? "animate-spin" : ""} />
          {scraping ? "Scraping…" : "Refresh Listings"}
        </button>
      </div>
    </header>
  );
}
