#[cfg(windows)]
use std::collections::HashMap;

#[cfg(windows)]
#[derive(Clone, Default)]
pub struct ProcessInfo {
    pub name: Option<String>,
    pub path: Option<String>,
}

#[cfg(windows)]
pub struct ProcessCache {
    cache: HashMap<u32, ProcessInfo>,
}

#[cfg(windows)]
impl ProcessCache {
    pub fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    pub fn resolve(&mut self, pid: u32) -> ProcessInfo {
        if let Some(info) = self.cache.get(&pid) {
            return info.clone();
        }
        let info = lookup(pid);
        self.cache.insert(pid, info.clone());
        info
    }
}

#[cfg(windows)]
fn lookup(pid: u32) -> ProcessInfo {
    use std::path::Path;
    use windows::core::PWSTR;
    use windows::Win32::Foundation::CloseHandle;
    use windows::Win32::System::Threading::{
        OpenProcess, QueryFullProcessImageNameW, PROCESS_NAME_WIN32,
        PROCESS_QUERY_LIMITED_INFORMATION,
    };

    if pid == 0 {
        return ProcessInfo {
            name: Some("System Idle Process".into()),
            path: None,
        };
    }
    if pid == 4 {
        return ProcessInfo {
            name: Some("System".into()),
            path: None,
        };
    }

    unsafe {
        let Ok(handle) = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, pid) else {
            return ProcessInfo::default();
        };

        let mut buf = vec![0u16; 1024];
        let mut size = buf.len() as u32;
        let result = QueryFullProcessImageNameW(
            handle,
            PROCESS_NAME_WIN32,
            PWSTR(buf.as_mut_ptr()),
            &mut size,
        );
        let _ = CloseHandle(handle);

        if result.is_err() || size == 0 {
            return ProcessInfo::default();
        }

        let path = String::from_utf16_lossy(&buf[..size as usize]);
        let name = Path::new(&path)
            .file_name()
            .map(|s| s.to_string_lossy().into_owned());

        ProcessInfo {
            name,
            path: Some(path),
        }
    }
}
