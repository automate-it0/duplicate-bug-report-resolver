# 🛡️ HackerOne Duplicate Bug Report Resolver

An automated python tool for security teams and bug bounty managers to detect and manage duplicate vulnerability reports on HackerOne using text similarity matching.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![HackerOne API](https://img.shields.io/badge/HackerOne-API_v1-lightgrey?logo=hackerone)](https://api.hackerone.com/v1/docs)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 Features

* **🔑 Secure Authentication**: Fully supports the HackerOne API v1 using HTTP Basic Authentication (`api_token_identifier` and `api_token`).
* **🧠 Cosine Similarity Engine**: Computes text similarity on title and vulnerability descriptions using a lightweight, pure-Python vector space model (no heavy machine-learning libraries required).
* **⏳ Chronological Analysis**: Automatically sorts reports to ensure newer submissions are marked as duplicates of older ones (preventing circular flagging).
* **💬 Auto-Commenting**: Automatically posts internal team comments on suspected duplicate reports pointing to the original report with a calculated similarity percentage.

---

## ⚙️ How It Works (Similarity Matching)

The tool processes reports using the following pipeline:
1. **Tokenization**: Cleans and splits the report text into lowercase alphanumeric tokens.
2. **Frequency Vectors**: Computes term frequency distributions for each report.
3. **Cosine Similarity**: Measures the cosine angle between frequency vectors in the multi-dimensional word space:
   $$\text{similarity} = \frac{A \cdot B}{\|A\| \|B\|}$$
   If the score is above the configured threshold (default: `0.8`), it flags the newer report.

---

## 🚀 Setup & Installation

### 1. Clone & Install Dependencies
Ensure you have `requests` installed:
```bash
pip install -r requirements.txt
```

### 2. Get HackerOne API Credentials
Go to your HackerOne Program Settings -> API Tokens and generate a token containing:
- **API Token Identifier** (Username)
- **API Token** (Password/Secret)

---

## 💻 Usage

Run the script from your terminal:
```bash
python main.py --api-identifier <YOUR_IDENTIFIER> --api-token <YOUR_TOKEN> --threshold 0.85
```

### Options:
- `--api-identifier` (Required): Your HackerOne API Token Identifier.
- `--api-token` (Required): Your HackerOne API Token Secret.
- `--threshold` (Optional): The similarity threshold above which reports are considered duplicates. Value between `0.0` (completely different) and `1.0` (exact copy). Default is `0.8`.

---

## 📄 License
Licensed under the [MIT License](LICENSE).