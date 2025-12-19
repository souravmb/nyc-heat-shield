# Security Policy

## Supported Versions

We take security seriously. Since this is an active research project, we currently support security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within this project (e.g., SQL Injection, Data Leakage, API Exposure), please **DO NOT** create a public GitHub issue. Publicly reporting a vulnerability can put our users (and data) at risk before we have a chance to patch it.

### How to Report Safely
We prefer you use GitHub's **Private Vulnerability Reporting** feature:
1. Go to the **Security** tab of this repository.
2. Click on **"Report a vulnerability"**.
3. Detail the steps to reproduce the issue.

Alternatively, you can email the maintainer directly at: **[INSERT YOUR EMAIL HERE]**.

### What Happens Next?
1. **Acknowledgement:** We will acknowledge your report within 48 hours.
2. **Investigation:** We will verify the vulnerability and assess its severity.
3. **Fix:** A patch will be released via a Pull Request.
4. **Disclosure:** Once the fix is live, we will publicly credit you (if desired) for your responsible disclosure.

## Security Tools Used
This repository is automatically scanned and protected by:
- **CodeQL** (Static Application Security Testing)
- **Dependabot** (Supply Chain Security)
- **Secret Scanning** (Leak Prevention)
