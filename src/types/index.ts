export type Protocol = 'tcp' | 'udp';

export type ProtocolFilter = 'all' | Protocol;

export interface ListeningPort {
  protocol: Protocol;
  local_addr: string;
  local_port: number;
  pid: number;
  process_name: string | null;
  process_path: string | null;
}

export type SortKey = 'port' | 'protocol' | 'addr' | 'pid' | 'name';

export type SortDir = 'asc' | 'desc';
