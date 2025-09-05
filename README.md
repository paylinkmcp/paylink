<div align="center">
  <picture>
    <img src="docs/logo/light.svg" width="80" alt="PayLink Logo">
  </picture>
</div>

<h1 align="center">AI-Powered Payment Integration Framework</h1>
<p align="center"><strong>Seamlessly integrate multiple payment providers (M-Pesa, Airtel Money, KCB, Equity) into your AI applications with our comprehensive MCP-based framework.</strong></p>

<div align="center">

[![Documentation](https://img.shields.io/badge/Documentation-📖-green)](https://paylink.mintlify.app/)
[![Website](https://img.shields.io/badge/Website-🌐-purple)](https://paylink.mintlify.app/)
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

PayLink is an open-source framework designed to simplify payment integrations for AI agents by leveraging the Model Context Protocol (MCP). It provides a standardized interface for various payment providers, including **M-Pesa**, **Airtel**, **Equity Bank**, and **KCB**, enabling seamless integration of payment functionalities into your AI applications.

### ✨ Key Features

- **💳 Multi-Provider Support**: M-Pesa, Airtel Money, Equity Bank, KCB
- **🤖 AI-First Design**: Built specifically for AI agents and MCP integration
- **🔐 Secure Authentication**: Enterprise-grade security with OAuth support
- **🚀 Instant Setup**: Get payment processing running in minutes
- **📱 Mobile-First**: Optimized for mobile payment workflows
- **🌍 East Africa Focus**: Specialized for regional payment systems

## 🚀 Quick Start - Get Payment Processing in 5 Minutes

### 🌐 Using PayLink Hosted Service (Recommended)

Get instant access to payment processing with our managed infrastructure:

```bash
pip install paylink
```

```python
from paylink import PayLink

# Initialize with your API key
paylink = PayLink(api_key="your-api-key")

# Create M-Pesa server instance
mpesa_server = paylink.create_server("mpesa", {
    "business_shortcode": "your_shortcode",
    "consumer_key": "your_consumer_key",
    "consumer_secret": "your_consumer_secret"
})

# Initiate payment
result = await mpesa_server.stk_push(
    amount="100",
    phone_number="254797357665",
    account_reference="PAYMENT001",
    transaction_desc="Payment for services"
)
```

### 🐳 Self-Hosting with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/paylink.git
cd paylink

# Run M-Pesa server
cd mcp_servers/mpesa
docker build -t paylink-mpesa .
docker run -p 5002:5002 paylink-mpesa

# Run Airtel server
cd ../airtel
docker build -t paylink-airtel .
docker run -p 5003:5003 paylink-airtel
```

### 🖥️ Direct Setup

```bash
# Install dependencies
cd mcp_servers/mpesa
pip install -r requirements.txt

# Set environment variables
export MPESA_CONSUMER_KEY="your_consumer_key"
export MPESA_CONSUMER_SECRET="your_consumer_secret"
export MPESA_BUSINESS_SHORT_CODE="your_shortcode"
export MPESA_PASSKEY="your_passkey"
export MPESA_CALLBACK_URL="https://yourdomain.com/callback"

# Run the server
python server.py
```

## 💳 Available Payment Providers

| Provider | Status | Features | Docker Image |
|----------|--------|----------|--------------|
| **M-Pesa** | 🚧 In Development | STK Push (Active Development), C2B, B2C | `paylink-mpesa:latest` |
| **Airtel Money** | 🚧 In Development | STK Push, USSD | `paylink-airtel:latest` |
| **Equity Bank** | 🚧 In Development | Bank Transfers | `paylink-equity:latest` |
| **KCB** | 🚧 In Development | Bank Transfers | `paylink-kcb:latest` |

## 🛣️ Roadmap

- [ ] Complete M-Pesa STK Push support
- [ ] Add Airtel Money USSD support
- [ ] Implement Equity and KCB bank transfers
- [ ] Publish SDK for Node.js and Go
- [ ] Add webhook event framework

## 📚 Resources & Community

| Resource | Link | Description |
|----------|------|-------------|
| **📖 Documentation** | [paylink.mintlify.app](https://paylink-1220482c.mintlify.app/) | Complete guides and API reference |
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

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p><strong>💳 Powering AI-Powered Payments Across East Africa</strong></p>
  <p>
    <a href="https://paylink-1220482c.mintlify.app/">Documentation</a> •
    <a href="https://github.com/paylinkmcp/paylink/issues">Issues</a> •
    <a href="examples/">Examples</a>
  </p>
</div>
