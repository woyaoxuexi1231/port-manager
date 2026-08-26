import { useMemo, useState } from 'react';
import { Toolbar } from './components/Toolbar';
import { PortTable } from './components/PortTable';
import { StatusBar } from './components/StatusBar';
import { useListeningPorts } from './hooks/useListeningPorts';
import type { ProtocolFilter, SortDir, SortKey } from './types';

function comparePorts(
  a: { protocol: string; local_addr: string; local_port: number; pid: number; process_name: string | null },
  b: typeof a,
  key: SortKey,
  dir: SortDir,
): number {
  const mul = dir === 'asc' ? 1 : -1;
  switch (key) {
    case 'port':
      return (a.local_port - b.local_port) * mul;
    case 'protocol':
      return a.protocol.localeCompare(b.protocol) * mul;
    case 'addr':
      return a.local_addr.localeCompare(b.local_addr) * mul;
    case 'pid':
      return (a.pid - b.pid) * mul;
    case 'name':
      return (a.process_name ?? '').localeCompare(b.process_name ?? '') * mul;
  }
}

export default function App() {
  const { ports, loading, error, refreshedAt, refresh } = useListeningPorts();
  const [query, setQuery] = useState('');
  const [protocol, setProtocol] = useState<ProtocolFilter>('all');
  const [sortKey, setSortKey] = useState<SortKey>('port');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let rows = ports;
    if (protocol !== 'all') {
      rows = rows.filter((p) => p.protocol === protocol);
    }
    if (q) {
      rows = rows.filter((p) => {
        const hay = [
          p.protocol,
          p.local_addr,
          String(p.local_port),
          String(p.pid),
          p.process_name ?? '',
          p.process_path ?? '',
        ]
          .join(' ')
          .toLowerCase();
        return hay.includes(q);
      });
    }
    return [...rows].sort((a, b) => comparePorts(a, b, sortKey, sortDir));
  }, [ports, query, protocol, sortKey, sortDir]);

  const handleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  return (
    <div className="flex h-full flex-col bg-[#f9fafb] text-[#1a1c20]">
      <Toolbar
        query={query}
        onQueryChange={setQuery}
        protocol={protocol}
        onProtocolChange={setProtocol}
        loading={loading}
        onRefresh={() => void refresh()}
      />
      <PortTable
        ports={filtered}
        loading={loading}
        sortKey={sortKey}
        sortDir={sortDir}
        onSort={handleSort}
      />
      <StatusBar
        total={ports.length}
        shown={filtered.length}
        loading={loading}
        error={error}
        refreshedAt={refreshedAt}
      />
    </div>
  );
}
