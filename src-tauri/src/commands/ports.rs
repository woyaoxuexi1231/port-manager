use crate::models::ListeningPort;
use crate::ports;

#[tauri::command]
pub async fn list_listening_ports() -> Result<Vec<ListeningPort>, String> {
    tokio::task::spawn_blocking(ports::list_listening)
        .await
        .map_err(|e| format!("task join error: {e}"))?
}
