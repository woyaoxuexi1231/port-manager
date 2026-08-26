import { invoke } from '@tauri-apps/api/core';
import type { ListeningPort } from '../types';

export async function listListeningPorts(): Promise<ListeningPort[]> {
  return invoke('list_listening_ports');
}
