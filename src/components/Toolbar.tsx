import { RefreshCw, Search } from 'lucide-react';
import type { ProtocolFilter } from '../types';
import { cn } from '../lib/cn';

interface Props {
  query: string;
  onQueryChange: (value: string) => void;
  protocol: ProtocolFilter;
  onProtocolChange: (value: ProtocolFilter) => void;
  loading: boolean;
  onRefresh: () => void;
}

const FILTERS: { id: ProtocolFilter; label: string }[] = [
  { id: 'all', label: '全部' },
  { id: 'tcp', label: 'TCP' },
  { id: 'udp', label: 'UDP' },
];

export function Toolbar({
  query,
  onQueryChange,
  protocol,
  onProtocolChange,
  loading,
  onRefresh,
}: Props) {
  return (
    <header className="flex flex-wrap items-center gap-3 border-b border-[#e2e4e8] bg-white px-4 py-3">
      <div className="min-w-0 flex-1">
        <h1 className="text-[15px] font-semibold tracking-tight text-[#1a1c20]">
          Port Manager
        </h1>
        <p className="text-[12px] text-[#6b7280]">本机监听端口占用查询</p>
      </div>

      <div className="relative min-w-[200px] flex-1 max-w-sm">
        <Search
          className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-[#9ca3af]"
          aria-hidden
        />
        <input
          type="search"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="搜索端口、进程、路径…"
          className="w-full rounded-[4px] border border-[#e2e4e8] bg-[#f0f1f3] py-1.5 pl-8 pr-3 font-mono text-[13px] text-[#1a1c20] outline-none transition focus:border-[#6b7280] focus:shadow-[0_0_0_2px_rgba(107,114,128,0.1)]"
        />
      </div>

      <div
        className="inline-flex rounded-[4px] border border-[#e2e4e8] bg-[#f8f9fa] p-0.5"
        role="group"
        aria-label="协议筛选"
      >
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => onProtocolChange(f.id)}
            className={cn(
              'rounded-[3px] px-2.5 py-1 text-[12px] font-medium transition',
              protocol === f.id
                ? 'bg-[#2d2d2d] text-white'
                : 'text-[#6b7280] hover:text-[#1a1c20]',
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      <button
        type="button"
        onClick={onRefresh}
        disabled={loading}
        className="inline-flex items-center gap-1.5 rounded-[4px] border border-[#e2e4e8] bg-white px-3 py-1.5 text-[13px] text-[#1a1c20] transition hover:border-[#c4c8cf] hover:bg-[#f3f4f6] disabled:cursor-not-allowed disabled:opacity-45"
      >
        <RefreshCw className={cn('size-3.5', loading && 'animate-spin')} />
        刷新
      </button>
    </header>
  );
}
