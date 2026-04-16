import { cn, STRATEGY_CONFIG } from "@/lib/utils";

type Strategy = keyof typeof STRATEGY_CONFIG;

interface Props {
  strategy: string | null | undefined;
  size?: "sm" | "md";
}

export default function StrategyBadge({ strategy, size = "md" }: Props) {
  if (!strategy || !(strategy in STRATEGY_CONFIG)) return null;
  const config = STRATEGY_CONFIG[strategy as Strategy];
  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-full",
        config.color,
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm"
      )}
    >
      {config.label}
    </span>
  );
}
