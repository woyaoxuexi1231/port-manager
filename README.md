# Port Manager

## 简介 / Introduction

**中文** — Windows 桌面工具，用于排查本地监听端口（TCP / UDP）及归属进程。展示 PID、进程名与可执行路径，支持搜索、协议过滤与列排序；只读查询、不会结束进程，帮你快速定位"是哪个程序占了这个端口"。

**English** — A Windows desktop tool for inspecting local listening ports (TCP / UDP) and the processes that own them. It shows PID, process name, and executable path with search, protocol filtering, and sortable columns — a read-only, query-only tool (never terminates processes) for quickly finding which program holds a port.

![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-1.1.3-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Stack](https://img.shields.io/badge/stack-Tauri%202%20%7C%20Rust%20%7C%20React-black)

## Features

- List local TCP listeners and UDP bound ports
- Show PID, process name, and executable path
- Search, protocol filter, and column sort
- Query only — no process termination

## Stack

- **Shell:** [Tauri 2](https://tauri.app/)
- **Backend:** Rust (`GetExtendedTcpTable` / `GetExtendedUdpTable`)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind 4

## Download

Installers are published on [GitHub Releases](https://github.com/woyaoxuexi1231/port-manager/releases).

Pushing a tag like `v1.0.0` triggers CI to build the Windows NSIS setup and attach it to the release.

## Develop

Requirements: Node.js 18+, Rust stable, Windows.

```bash
npm install
npm run tauri dev
```

Build installer:

```bash
npm run tauri build
```

## Architecture

```text
UI (React) → invoke.ts → commands/ports → ports/{table,process}
```

- Frontend never calls Tauri `invoke` outside `src/utils/invoke.ts`
- `models.rs` and `src/types/index.ts` stay in sync (snake_case fields)
- Port enumeration uses Win32 IP Helper APIs, not `netstat` text parsing

## License

[MIT](LICENSE)
