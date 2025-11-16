<div align="center">
  <picture>
    <img src="docs/logo/light.svg" width="80" alt="PayLink Logo">
  </picture>
</div>

<h1 align="center">PayLink — AI‑Native Payments for Agents</h1>
<p align="center"><strong>Give your agent the capability to pay for services and get paid—securely and reliably—across providers and environments.</strong></p>

<div align="center">

[![Documentation](https://img.shields.io/badge/Documentation-📖-green)](https://paylink-platform.vercel.app/)
[![Website](https://img.shields.io/badge/Website-🌐-purple)](https://paylink-platform.vercel.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io)
![Contributors](https://img.shields.io/github/contributors/paylinkmcp/paylink)
![Good First Issues](https://img.shields.io/github/issues/paylinkmcp/paylink/good%20first%20issue)

</div>

## 📑 Table of Contents
- [🚀 What is PayLink?](#-what-is-paylink)
- [✨ Key Features](#-key-features)
- [🚀 Quick Start - Get Payment Processing in 5 Minutes](#-quick-start---get-payment-processing-in-5-minutes)
- [💳 Available Payment Providers](#-available-payment-providers)
- [🛣️ Roadmap](#️-roadmap)
- [📚 Resources & Community](#-resources--community)
- [🤝 Contributing](#-contributing)
- [🔒 Security](#-security)
- [📜 License](#-license)

## 🚀 What is PayLink?

PayLink is an open‑source framework designed to simplify payment integrations for AI agents via the Model Context Protocol (MCP). It provides a consistent interface to multiple providers (e.g., **M‑Pesa**, **Airtel Money**, **Equity Bank**, **KCB**) so agents can initiate and manage payments without bespoke, provider‑specific code.

### ✨ Highlights

- **Unified SDK** across providers
- **MCP‑native** for AI agents
- **Secure credential management**
- **Production‑ready workflows**

## 🚀 Quick Start

See the docs for the full guide: **Quickstart** → <a href="https://paylink-platform.vercel.app/quickstart">paylink-platform.vercel.app/quickstart</a>

### 🐳 Run with Docker (M‑Pesa MCP Server)

```bash
# Clone the repository
git clone https://github.com/paylinkmcp/paylink.git
cd paylink

# Start the M‑Pesa server (and example server) via Docker Compose
docker compose up --build
```

### 🖥️ Run Locally (M‑Pesa MCP Server)

```bash
cd mcp_servers/mpesa
# Using uv (recommended)
uv sync
uv run python server.py
```

## 💳 Available Payment Providers

| Provider | Status | Features | Docker Image |
|----------|--------|----------|--------------|
| **M-Pesa** | ✅ Supported | STK Push | `mpesa-mcp-server` (compose) |
| **Airtel Money** | Coming soon | STK Push, USSD | — |
| **Equity Bank** | Coming soon | Bank Transfers | — |
| **KCB** | Coming soon | Bank Transfers | — |

## 🛣️ Roadmap

- [ ] Add Airtel Money support
- [ ] Implement Equity and KCB bank transfers
- [ ] Publish TypeScript SDK
- [ ] Webhook/event framework

## 📚 Resources & Community

| Resource | Link | Description |
|----------|------|-------------|
| **📖 Documentation** | [paylink-platform.vercel.app](https://paylink-platform.vercel.app/) | Guides and examples |
| **🐛 Issues** | [GitHub Issues](https://github.com/paylinkmcp/paylink/issues) | Report bugs and request features |
| **📦 Examples** | [examples/](examples/) | Working examples with popular AI frameworks |
| **🔧 Server Guides** | [mcp_servers/](mcp_servers/) | Individual server documentation |

## 🤝 Contributing

We love contributions! Whether you want to:
- 🐛 Report bugs or request features
- 📝 Improve documentation  
- 🔧 Build new MCP servers
- 🎨 Enhance existing servers

Check out our [Contributing Guide](CONTRIBUTING.md) to get started!

## 🔒 Security

If you discover a security vulnerability, please see our [Security Policy](SECURITY.md) for how to report it responsibly.

## 📫 Contact

Questions or need help? Email us at <a href="mailto:paylinkmcp@gmail.com">paylinkmcp@gmail.com</a> or join our Discord from the docs.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p><strong>💳 Powering AI‑Native Payments for Agents</strong></p>
  <p>
    <a href="https://paylink-platform.vercel.app/">Documentation</a> •
    <a href="https://github.com/paylinkmcp/paylink/issues">Issues</a> •
    <a href="examples/">Examples</a>
  </p>
</div>
