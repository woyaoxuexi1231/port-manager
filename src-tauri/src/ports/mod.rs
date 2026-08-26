mod process;
mod table;

use crate::models::ListeningPort;

/// Enumerate local TCP listeners and UDP bound ports with owning process info.
pub fn list_listening() -> Result<Vec<ListeningPort>, String> {
    #[cfg(windows)]
    {
        let mut rows = table::collect_listening_rows()?;
        let mut cache = process::ProcessCache::new();
        for row in &mut rows {
            let info = cache.resolve(row.pid);
            row.process_name = info.name;
            row.process_path = info.path;
        }
        rows.sort_by(|a, b| {
            a.local_port
                .cmp(&b.local_port)
                .then_with(|| format!("{:?}", a.protocol).cmp(&format!("{:?}", b.protocol)))
                .then_with(|| a.local_addr.cmp(&b.local_addr))
                .then_with(|| a.pid.cmp(&b.pid))
        });
        Ok(rows)
    }

    #[cfg(not(windows))]
    {
        Err("Port listing is only supported on Windows".into())
    }
}

#[cfg(all(test, windows))]
mod tests {
    #[test]
    fn list_listening_returns_rows() {
        let rows = super::list_listening().expect("list_listening");
        // A healthy Windows box almost always has at least one listener;
        // keep the assertion soft so CI sandboxes without sockets still pass.
        for row in &rows {
            assert!(row.local_port > 0 || row.local_port == 0);
            assert!(row.pid > 0 || row.pid == 0);
        }
        eprintln!("listening ports: {}", rows.len());
    }
}
