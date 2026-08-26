import { useEffect } from 'react';
import { X } from 'lucide-react';
import type { ListeningPort } from '../types';
import { cn } from '../lib/cn';

interface Props {
  port: ListeningPort;
  onClose: () => void;
}

function Field({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="grid gap-1">
      <dt className="text-[11px] font-medium uppercase tracking-wide text-[#9ca3af]">
        {label}
      </dt>
      <dd
        className={cn(
          'text-[13px] text-[#1a1c20] break-all',
          mono && 'font-mono text-[12px]',
        )}
      >
        {value}
      </dd>
    </div>
  );
}

export function PortDetailDialog({ port, onClose }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const endpoint = `${port.local_addr}:${port.local_port}`;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-[#0a1b33]/25 px-4 backdrop-blur-[1px]"
      onClick={onClose}
    >
      <div
        className="w-full max-w-[480px] overflow-hidden rounded-lg border border-[#e2e4e8] bg-white shadow-[0_8px_32px_rgba(0,0,0,0.08)]"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="port-detail-title"
      >
        <header className="flex items-start justify-between gap-3 border-b border-[#e2e4e8] px-4 py-3">
          <div>
            <h2 id="port-detail-title" className="text-[15px] font-semibold text-[#1a1c20]">
              端口详情
            </h2>
            <p className="mt-0.5 font-mono text-[12px] text-[#6b7280]">{endpoint}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-[4px] p-1 text-[#6b7280] transition hover:bg-[#f3f4f6] hover:text-[#1a1c20]"
            aria-label="关闭"
          >
            <X className="size-4" />
          </button>
        </header>

        <dl className="grid gap-4 px-4 py-4">
          <Field label="协议" value={port.protocol.toUpperCase()} />
          <Field label="本地地址" value={port.local_addr} mono />
          <Field label="端口" value={String(port.local_port)} mono />
          <Field label="本地端点" value={endpoint} mono />
          <Field label="进程 ID (PID)" value={String(port.pid)} mono />
          <Field label="进程名" value={port.process_name ?? '—'} />
          <Field label="可执行路径" value={port.process_path ?? '—（权限不足或系统进程）'} mono />
        </dl>

        <footer className="border-t border-[#e2e4e8] px-4 py-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-[4px] border border-[#e2e4e8] bg-white px-3 py-1.5 text-[13px] text-[#1a1c20] transition hover:bg-[#f3f4f6]"
          >
            关闭
          </button>
        </footer>
      </div>
    </div>
  );
}
