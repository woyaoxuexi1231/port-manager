use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Protocol {
    Tcp,
    Udp,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListeningPort {
    pub protocol: Protocol,
    pub local_addr: String,
    pub local_port: u16,
    pub pid: u32,
    pub process_name: Option<String>,
    pub process_path: Option<String>,
}
