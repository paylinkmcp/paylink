# Contributing to Paylink

Thank you for your interest in contributing to Paylink! This document explains how to contribute effectively and consistently to the project.

## Contributor License Agreement (CLA)

Before we can accept contributions, all contributors must sign our **Contributor License Agreement (CLA)**:

👉 [Sign the CLA here](https://cla-assistant.io/paylinkmcp/paylink)

This ensures that everyone submitting code has the legal right to do so and agrees to the project’s licensing terms.

## Table of Contents
- [Contributor License Agreement (CLA)](#contributor-license-agreement-cla)
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branch Naming](#branch-naming)
- [Development Workflow](#development-workflow)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [License](#license)

## Code of Conduct

We are committed to fostering a welcoming, inclusive, and respectful community.  
Please read and follow our [Code of Conduct](https://cla-assistant.io/paylinkmcp/paylink).

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/paylink.git
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/paylinkmcp/paylink.git
   ```
4. Create a new branch for your work
5. Make your changes
6. Submit a pull request (PR)

## Branch Naming

We recommend the following naming convention:
- `feature/<short-description>` for new features (e.g., `feature/mpesa-auth`)
- `fix/<short-description>` for bug fixes (e.g., `fix/airtel-pr-comments`)
- `docs/<short-description>` for documentation changes

## Development Workflow

### Monorepo Structure
The project uses a **monorepo** with multiple MCP servers and clients:
- `mcp_servers/` → individual Model Context Protocol servers
- `mcp_clients/` → clients that connect to MCP servers

Be mindful of the scope of your change and potential impacts on other components.

### MCP Server Contributions
If you are contributing a new MCP server, please see the [📖 MCP Server Guide](GUIDE.md), which covers:
- What MCP servers are
- How to design effective tools for AI agents
- Best practices and testing requirements
- Step-by-step development instructions

## Commit Message Convention

We follow a simplified [Conventional Commits](https://www.conventionalcommits.org/) convention:

```
<type>(<scope>): <subject>
```

**Types:**
- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation changes
- `style`: formatting only (no code changes)
- `refactor`: code restructure without changing behavior
- `perf`: performance improvements
- `test`: adding/correcting tests
- `chore`: build or tooling changes
- `ci`: CI/CD config changes

**Examples:**
```
feat(mpesa): add user profile lookup functionality
fix(airtel): resolve PR comment retrieval issue
docs(kcb): update installation instructions
```

## Pull Request Process

1. Create a descriptive PR title following the commit format
2. Fill in the [PR template](.github/pull_request_template.md)
3. Link related issues (`Fixes #123`, `Closes #456`)
4. Keep PRs focused and manageable
5. Update docs if your changes affect the public API or UX
6. Add tests for new features/bug fixes
7. Ensure all tests and checks pass locally
8. Request reviews from maintainers
9. Address review feedback promptly
10. Rebase your branch on the latest `main` before merging

## Code Style Guidelines

- Follow the style conventions of the language you’re working in (Python/Go/Node.js)
- Use linters and formatters (configured in the repo)
- Keep code readable and well-documented

## Testing Guidelines

- Write tests for all new features and bug fixes
- Ensure code coverage does not decrease
- Test across supported Node.js/Python/Go versions when relevant
- Run the full test suite before submitting:
  ```bash
  npm test    # for Node.js
  pytest      # for Python
  go test ./...  # for Go
  ```

## License

By contributing to Paylink, you agree that your contributions are licensed under the project’s [MIT License](LICENSE).
