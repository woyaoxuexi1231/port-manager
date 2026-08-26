mod commands;
pub mod models;
mod ports;

use tauri::Manager;

fn app_icon() -> tauri::image::Image<'static> {
    tauri::image::Image::from_bytes(include_bytes!("../icons/128x128.png"))
        .expect("failed to decode app icon")
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let icon = app_icon();
            if let Some(window) = app.get_webview_window("main") {
                window.set_icon(icon)?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::ports::list_listening_ports,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
