# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within the CompText ecosystem, please send an email to security@comptext.dev. All security vulnerabilities will be promptly addressed.

**Please do not create public GitHub issues for security vulnerabilities.**

### What to include in your report:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability

### What to expect:

- Acknowledgment of your report within 48 hours
- Regular updates on the progress
- Credit in the security advisory (if desired)

## Security Best Practices

When using CompText:

1. **API Keys**: Never commit API keys or credentials to version control
2. **Dependencies**: Keep dependencies up to date
3. **Validation**: Always validate input when using CompText DSL
4. **Permissions**: Use least-privilege principles for MCP server access

## Security Updates

Security updates are released as patch versions (e.g., 1.0.1, 1.0.2) and are announced through:

- GitHub Security Advisories
- Release notes
- Mailing list (security@comptext.dev)

Thank you for helping keep CompText and our users safe!
