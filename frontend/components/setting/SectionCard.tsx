export function SectionCard(props: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-3xl bg-[var(--bg-card)] p-6 shadow-[0_12px_40px_rgba(0,0,0,0.30)]">
      <div className="mb-4">
        <div className="text-base font-medium text-[var(--foreground)]">
          {props.title}
        </div>
        {props.description && (
          <div className="mt-1 text-sm text-[var(--text-muted)]">
            {props.description}
          </div>
        )}
      </div>
      {props.children}
    </section>
  );
}
