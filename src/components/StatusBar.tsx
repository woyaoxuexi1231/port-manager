interface Props {
  total: number;
  shown: number;
  loading: boolean;
  error: string | null;
  refreshedAt: Date | null;
}

export function StatusBar({ total, shown, loading, error, refreshedAt }: Props) {
  const time =
    refreshedAt &&
    refreshedAt.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

  return (
    <footer className="flex h-7 shrink-0 items-center gap-3 border-t border-[#e2e4e8] bg-[#f8f9fa] px-4 text-[11px] text-[#6b7280]">
      <span>
        {shown === total ? `共 ${total} 条监听` : `显示 ${shown} / ${total} 条`}
      </span>
      {loading && <span className="text-[#9ca3af]">刷新中…</span>}
      {error && (
        <span className="truncate text-[#dc2626]" title={error}>
          {error}
        </span>
      )}
      <span className="ml-auto">{time ? `上次刷新 ${time}` : '尚未刷新'}</span>
    </footer>
  );
}
