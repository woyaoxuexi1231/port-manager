import { useCallback, useEffect, useState } from 'react';
import { listListeningPorts } from '../utils/invoke';
import type { ListeningPort } from '../types';

export function useListeningPorts() {
  const [ports, setPorts] = useState<ListeningPort[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshedAt, setRefreshedAt] = useState<Date | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const next = await listListeningPorts();
      setPorts(next);
      setRefreshedAt(new Date());
    } catch (e) {
      setError(String(e));
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { ports, loading, error, refreshedAt, refresh };
}
