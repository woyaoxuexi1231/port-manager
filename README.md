# Port Manager

Windows desktop tool for inspecting **local listening ports** (TCP / UDP) and the processes that own them.

![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-1.0.1-green)
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
