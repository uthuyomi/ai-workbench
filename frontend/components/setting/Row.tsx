export function Row(props: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-6 py-3">
      <div className="text-sm text-[var(--text-faint)]">{props.label}</div>
      <div className="text-sm text-[var(--foreground)] text-right min-w-0">
        {props.value}
      </div>
    </div>
  );
}
