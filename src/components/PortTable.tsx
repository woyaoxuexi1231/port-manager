import type { ListeningPort, SortDir, SortKey } from '../types';
import { cn } from '../lib/cn';

interface Props {
  ports: ListeningPort[];
  /** Forces a clean table body remount when the visible set changes. */
  listKey: string;
  loading: boolean;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (key: SortKey) => void;
}

const COLUMNS: { key: SortKey; label: string; className?: string }[] = [
  { key: 'protocol', label: '协议', className: 'w-16' },
  { key: 'addr', label: '本地地址', className: 'w-[160px]' },
  { key: 'port', label: '端口', className: 'w-20' },
  { key: 'pid', label: 'PID', className: 'w-20' },
  { key: 'name', label: '进程' },
];

export function PortTable({ ports, listKey, loading, sortKey, sortDir, onSort }: Props) {
  if (!loading && ports.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center text-[13px] text-[#9ca3af]">
        没有匹配的监听端口
      </div>
    );
  }

  return (
    <div className="relative min-h-0 flex-1 overflow-auto">
      {loading && (
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-0.5 overflow-hidden bg-[#e2e4e8]">
          <div className="h-full w-1/3 animate-pulse bg-[#2d2d2d]" />
        </div>
      )}
      <table className="w-full border-collapse text-left text-[13px]">
        <thead className="sticky top-0 z-[1] bg-[#f8f9fa]">
          <tr className="border-b border-[#e2e4e8]">
            {COLUMNS.map((col) => (
              <th key={col.key} className={cn('px-3 py-2 font-medium text-[#6b7280]', col.className)}>
                <button
                  type="button"
                  onClick={() => onSort(col.key)}
                  className="inline-flex items-center gap-1 hover:text-[#1a1c20]"
                >
                  {col.label}
                  {sortKey === col.key && (
                    <span className="text-[10px] text-[#9ca3af]">
                      {sortDir === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </button>
              </th>
            ))}
            <th className="px-3 py-2 font-medium text-[#6b7280]">路径</th>
          </tr>
        </thead>
        <tbody key={listKey}>
          {ports.map((row, index) => (
            <tr
              key={`${listKey}-${index}`}
              className="border-b border-[#f0f1f3] hover:bg-[#f8f9fa]"
            >
              <td className="px-3 py-2">
                <span
                  className={cn(
                    'inline-block rounded-[3px] px-1.5 py-0.5 font-mono text-[11px] font-medium uppercase',
                    row.protocol === 'tcp'
                      ? 'bg-[#f0fdf4] text-[#16a34a]'
                      : 'bg-[#fffbeb] text-[#d97706]',
                  )}
                >
                  {row.protocol}
                </span>
              </td>
              <td className="px-3 py-2 font-mono text-[12px] text-[#1a1c20]">
                {row.local_addr}
              </td>
              <td className="px-3 py-2 font-mono text-[12px] font-medium text-[#1a1c20]">
                {row.local_port}
              </td>
              <td className="px-3 py-2 font-mono text-[12px] text-[#6b7280]">{row.pid}</td>
              <td className="max-w-[180px] truncate px-3 py-2 text-[#1a1c20]" title={row.process_name ?? undefined}>
                {row.process_name ?? '—'}
              </td>
              <td
                className="max-w-[320px] truncate px-3 py-2 font-mono text-[11px] text-[#9ca3af]"
                title={row.process_path ?? undefined}
              >
                {row.process_path ?? '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
