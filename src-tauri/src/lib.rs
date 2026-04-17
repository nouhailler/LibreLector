use std::net::TcpStream;
use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::Manager;

struct PythonServer(Mutex<Option<Child>>);

fn wait_for_port(port: u16, max_attempts: u32) -> bool {
    for _ in 0..max_attempts {
        if TcpStream::connect(format!("127.0.0.1:{}", port)).is_ok() {
            return true;
        }
        std::thread::sleep(std::time::Duration::from_millis(300));
    }
    false
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let child = Command::new("python3")
                .args(["-m", "librelector.api.server"])
                .spawn()
                .expect("Impossible de démarrer le backend Python (python3 requis dans PATH)");

            app.manage(PythonServer(Mutex::new(Some(child))));

            let handle = app.handle().clone();
            std::thread::spawn(move || {
                if wait_for_port(7531, 60) {
                    if let Some(win) = handle.get_webview_window("main") {
                        let _ = win.show();
                    }
                } else {
                    eprintln!("[LibreLector] Le serveur Python n'a pas répondu dans le délai imparti.");
                }
            });

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                if let Some(state) = window.app_handle().try_state::<PythonServer>() {
                    if let Ok(mut guard) = state.0.lock() {
                        if let Some(mut child) = guard.take() {
                            let _ = child.kill();
                            let _ = child.wait();
                        }
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
