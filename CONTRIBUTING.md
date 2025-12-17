# Contributing to NYC Heat-Shield

First off, thanks for taking the time to contribute! 

## How to Contribute

### 1. Reporting Bugs
- Ensure the bug was not already reported by searching on GitHub under [Issues].
- If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a **title and clear description**, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

### 2. Suggesting Enhancements
- Open a new issue with the **Feature Request** template.
- Explain why this enhancement would be useful to other users.

### 3. Pull Requests
1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. Ensure the test suite passes.
4. Make sure your code lints.
5. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone [https://github.com/souravmb/nyc-heat-shield.git](https://github.com/souravmb/nyc-heat-shield.git)

# Install dependencies
pip install -r requirements.txt

# Run the Marimo app
marimo edit app.py
