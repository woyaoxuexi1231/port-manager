#[cfg(windows)]
use crate::models::{ListeningPort, Protocol};

#[cfg(windows)]
pub fn collect_listening_rows() -> Result<Vec<ListeningPort>, String> {
    let mut rows = Vec::new();
    rows.extend(tcp_table(false)?);
    rows.extend(tcp_table(true)?);
    rows.extend(udp_table(false)?);
    rows.extend(udp_table(true)?);
    Ok(rows)
}

#[cfg(windows)]
fn tcp_table(ipv6: bool) -> Result<Vec<ListeningPort>, String> {
    use windows::Win32::NetworkManagement::IpHelper::{
        GetExtendedTcpTable, TCP_TABLE_OWNER_PID_LISTENER,
    };
    use windows::Win32::Networking::WinSock::{AF_INET, AF_INET6};

    let family = if ipv6 { AF_INET6 } else { AF_INET };
    let mut size = 0u32;

    unsafe {
        let _ = GetExtendedTcpTable(
            None,
            &mut size,
            false,
            family.0 as u32,
            TCP_TABLE_OWNER_PID_LISTENER,
            0,
        );

        if size == 0 {
            return Ok(Vec::new());
        }

        let mut buffer = vec![0u8; size as usize];
        let status = GetExtendedTcpTable(
            Some(buffer.as_mut_ptr().cast()),
            &mut size,
            false,
            family.0 as u32,
            TCP_TABLE_OWNER_PID_LISTENER,
            0,
        );

        // Table can grow between size query and fetch — retry once.
        if status != windows::Win32::Foundation::NO_ERROR.0
            && status == windows::Win32::Foundation::ERROR_INSUFFICIENT_BUFFER.0
        {
            buffer.resize(size as usize, 0);
            let status = GetExtendedTcpTable(
                Some(buffer.as_mut_ptr().cast()),
                &mut size,
                false,
                family.0 as u32,
                TCP_TABLE_OWNER_PID_LISTENER,
                0,
            );
            if status != windows::Win32::Foundation::NO_ERROR.0 {
                return Err(format!("GetExtendedTcpTable failed: {status}"));
            }
        } else if status != windows::Win32::Foundation::NO_ERROR.0 {
            return Err(format!("GetExtendedTcpTable failed: {status}"));
        }

        if ipv6 {
            parse_tcp6(&buffer)
        } else {
            parse_tcp4(&buffer)
        }
    }
}

#[cfg(windows)]
fn udp_table(ipv6: bool) -> Result<Vec<ListeningPort>, String> {
    use windows::Win32::NetworkManagement::IpHelper::{
        GetExtendedUdpTable, UDP_TABLE_OWNER_PID,
    };
    use windows::Win32::Networking::WinSock::{AF_INET, AF_INET6};

    let family = if ipv6 { AF_INET6 } else { AF_INET };
    let mut size = 0u32;

    unsafe {
        let _ = GetExtendedUdpTable(
            None,
            &mut size,
            false,
            family.0 as u32,
            UDP_TABLE_OWNER_PID,
            0,
        );

        if size == 0 {
            return Ok(Vec::new());
        }

        let mut buffer = vec![0u8; size as usize];
        let status = GetExtendedUdpTable(
            Some(buffer.as_mut_ptr().cast()),
            &mut size,
            false,
            family.0 as u32,
            UDP_TABLE_OWNER_PID,
            0,
        );

        if status != windows::Win32::Foundation::NO_ERROR.0
            && status == windows::Win32::Foundation::ERROR_INSUFFICIENT_BUFFER.0
        {
            buffer.resize(size as usize, 0);
            let status = GetExtendedUdpTable(
                Some(buffer.as_mut_ptr().cast()),
                &mut size,
                false,
                family.0 as u32,
                UDP_TABLE_OWNER_PID,
                0,
            );
            if status != windows::Win32::Foundation::NO_ERROR.0 {
                return Err(format!("GetExtendedUdpTable failed: {status}"));
            }
        } else if status != windows::Win32::Foundation::NO_ERROR.0 {
            return Err(format!("GetExtendedUdpTable failed: {status}"));
        }

        if ipv6 {
            parse_udp6(&buffer)
        } else {
            parse_udp4(&buffer)
        }
    }
}

#[cfg(windows)]
fn parse_tcp4(buffer: &[u8]) -> Result<Vec<ListeningPort>, String> {
    use windows::Win32::NetworkManagement::IpHelper::MIB_TCPTABLE_OWNER_PID;

    if buffer.len() < std::mem::size_of::<MIB_TCPTABLE_OWNER_PID>() {
        return Ok(Vec::new());
    }

    let table = unsafe { &*(buffer.as_ptr() as *const MIB_TCPTABLE_OWNER_PID) };
    let count = table.dwNumEntries as usize;
    let rows_ptr = table.table.as_ptr();
    let mut out = Vec::with_capacity(count);

    for i in 0..count {
        let row = unsafe { &*rows_ptr.add(i) };
        out.push(ListeningPort {
            protocol: Protocol::Tcp,
            local_addr: ipv4_to_string(row.dwLocalAddr),
            local_port: port_from_network(row.dwLocalPort),
            pid: row.dwOwningPid,
            process_name: None,
            process_path: None,
        });
    }
    Ok(out)
}

#[cfg(windows)]
fn parse_tcp6(buffer: &[u8]) -> Result<Vec<ListeningPort>, String> {
    use windows::Win32::NetworkManagement::IpHelper::MIB_TCP6TABLE_OWNER_PID;

    if buffer.len() < std::mem::size_of::<MIB_TCP6TABLE_OWNER_PID>() {
        return Ok(Vec::new());
    }

    let table = unsafe { &*(buffer.as_ptr() as *const MIB_TCP6TABLE_OWNER_PID) };
    let count = table.dwNumEntries as usize;
    let rows_ptr = table.table.as_ptr();
    let mut out = Vec::with_capacity(count);

    for i in 0..count {
        let row = unsafe { &*rows_ptr.add(i) };
        out.push(ListeningPort {
            protocol: Protocol::Tcp,
            local_addr: ipv6_to_string(&row.ucLocalAddr),
            local_port: port_from_network(row.dwLocalPort),
            pid: row.dwOwningPid,
            process_name: None,
            process_path: None,
        });
    }
    Ok(out)
}

#[cfg(windows)]
fn parse_udp4(buffer: &[u8]) -> Result<Vec<ListeningPort>, String> {
    use windows::Win32::NetworkManagement::IpHelper::MIB_UDPTABLE_OWNER_PID;

    if buffer.len() < std::mem::size_of::<MIB_UDPTABLE_OWNER_PID>() {
        return Ok(Vec::new());
    }

    let table = unsafe { &*(buffer.as_ptr() as *const MIB_UDPTABLE_OWNER_PID) };
    let count = table.dwNumEntries as usize;
    let rows_ptr = table.table.as_ptr();
    let mut out = Vec::with_capacity(count);

    for i in 0..count {
        let row = unsafe { &*rows_ptr.add(i) };
        out.push(ListeningPort {
            protocol: Protocol::Udp,
            local_addr: ipv4_to_string(row.dwLocalAddr),
            local_port: port_from_network(row.dwLocalPort),
            pid: row.dwOwningPid,
            process_name: None,
            process_path: None,
        });
    }
    Ok(out)
}

#[cfg(windows)]
fn parse_udp6(buffer: &[u8]) -> Result<Vec<ListeningPort>, String> {
    use windows::Win32::NetworkManagement::IpHelper::MIB_UDP6TABLE_OWNER_PID;

    if buffer.len() < std::mem::size_of::<MIB_UDP6TABLE_OWNER_PID>() {
        return Ok(Vec::new());
    }

    let table = unsafe { &*(buffer.as_ptr() as *const MIB_UDP6TABLE_OWNER_PID) };
    let count = table.dwNumEntries as usize;
    let rows_ptr = table.table.as_ptr();
    let mut out = Vec::with_capacity(count);

    for i in 0..count {
        let row = unsafe { &*rows_ptr.add(i) };
        out.push(ListeningPort {
            protocol: Protocol::Udp,
            local_addr: ipv6_to_string(&row.ucLocalAddr),
            local_port: port_from_network(row.dwLocalPort),
            pid: row.dwOwningPid,
            process_name: None,
            process_path: None,
        });
    }
    Ok(out)
}

#[cfg(windows)]
fn port_from_network(port: u32) -> u16 {
    u16::from_be(port as u16)
}

#[cfg(windows)]
fn ipv4_to_string(addr: u32) -> String {
    let b = addr.to_ne_bytes();
    format!("{}.{}.{}.{}", b[0], b[1], b[2], b[3])
}

#[cfg(windows)]
fn ipv6_to_string(addr: &[u8; 16]) -> String {
    std::net::Ipv6Addr::from(*addr).to_string()
}
