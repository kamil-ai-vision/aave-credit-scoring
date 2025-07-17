# 🏦 Aave V2 Wallet Credit Scoring Engine

This project provides a robust, one-step script to analyze transaction data from the Aave V2 protocol and assign a credit score between 0 and 1000 to each wallet. The scoring model is based on historical on-chain behavior, rewarding responsible usage and penalizing risky or exploitative actions.

---

## 📚 Table of Contents

- [Methodology](#methodology)
- [Feature Engineering](#feature-engineering)
- [Scoring Architecture](#scoring-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [How to Run](#how-to-run)

---

## 🧠 Methodology

This project utilizes a **heuristic-based scoring model**. Given the absence of pre-labeled "good" or "bad" wallets in the dataset (an unsupervised learning problem), this approach was chosen for its transparency, interpretability, and robustness.

The model works by quantifying various aspects of a wallet's transaction history into distinct features. These features are then normalized and combined using a weighted formula to produce a final credit score. This method makes the logic behind each score easily explainable.

---

## 🏗️ Feature Engineering

The credit score is derived from several key features engineered from the raw transaction data. Each feature is designed to be a proxy for financial health, risk, or protocol engagement.

### ✅ Positive Indicators (Responsible Behavior)

- **`repayment_ratio`**: The ratio of total USD value repaid to total USD value borrowed. A value >= 1 indicates a wallet that pays back its debts. This is the strongest positive signal.
- **`lifespan_days`**: The number of days between a wallet's first and last transaction. A longer lifespan suggests a long-term, committed user rather than a temporary or bot account.
- **`total_deposits_usd`**: The cumulative USD value of all deposits. Higher values indicate significant capital trust in the protocol.
- **`transaction_count`**: The total number of transactions. A higher count indicates a more active and engaged user.

### ⚠️ Negative Indicators (Risky Behavior)

- **`liquidation_count`**: The number of times a wallet's collateral was seized to cover its debt. This is the strongest signal of high-risk borrowing and financial distress.

---

## 🧮 Scoring Architecture

The final score is calculated using a **three-step process**:

### 1. Normalization

All engineered features are scaled to a common range of 0 to 1 using a **Min-Max Scaler**. This ensures that no single feature can dominate the score due to its scale (e.g., `total_deposits_usd` vs. `liquidation_count`).

### 2. Weighted Calculation

The normalized features are multiplied by their assigned weights and summed. Negative weights are used for risky behaviors.

**Formula**:

```
Raw Score = 
    (Norm_RepayRatio * 25)
  + (Norm_Lifespan * 10)
  + (Norm_Deposits * 15)
  + (Norm_TxnCount * 5)
  - (Norm_LiquidationCount * 50)
```

### 3. Final Scaling

The resulting raw scores are passed through a second **Min-Max Scaler** to map them to the required **0–1000** range, producing the final credit score.

---

## 📁 Project Structure

```
aave-credit-scoring/
│
├── data/
│   └── user-wallet-transactions.json
│
├── src/
│   ├── feature_engineering.py
│   └── scoring.py
│
├── score_wallets.py
├── wallet_scores.csv
├── analysis.md
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone <your-repo-url>
cd aave-credit-scoring
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

The entire pipeline can be executed with a single command. The script requires the path to the input JSON file and optionally accepts an output file path.

```bash
python score_wallets.py --input_file "path/to/user-wallet-transactions.json"
```

### Example:

```bash
python score_wallets.py --input_file "data/user-wallet-transactions.json"
```

This will process the data and save the results in a file named `wallet_scores.csv` in the project's root directory.

---
