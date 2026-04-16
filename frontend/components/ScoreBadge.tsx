import { cn, scoreBg } from "@/lib/utils";

interface Props {
  score: number | null;
  label?: string;
  size?: "sm" | "md";
}

export default function ScoreBadge({ score, label, size = "md" }: Props) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-semibold rounded-full",
        scoreBg(score),
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm"
      )}
    >
      {score != null ? score.toFixed(1) : "—"}
      {label && <span className="font-normal opacity-75 text-xs">{label}</span>}
    </span>
  );
}
