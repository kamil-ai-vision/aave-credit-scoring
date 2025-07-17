import pandas as pd
import numpy as np

# Define token decimals for accurate value calculation. This is standard practice in DeFi.
TOKEN_DECIMALS = {
    'USDC': 6,
    'USDT': 6,
    'DAI': 18,
    'WETH': 18,
    'WMATIC': 18,
    'WBTC': 8,
    'AAVE': 18,
    'EURS': 2
    # Default to 18 if a token is not in this list
}

def _calculate_real_amount_usd(row):
    """
    Internal helper function to calculate the true USD value from transaction data.
    (Prefixed with _ to indicate it's not meant to be used outside this module).
    """
    action_data = row['actionData']
    
    if not isinstance(action_data, dict):
        return 0.0

    amount_str = action_data.get('amount')
    price_usd_str = action_data.get('assetPriceUSD')
    symbol = action_data.get('assetSymbol')

    if not all([amount_str, price_usd_str, symbol]):
        return 0.0

    try:
        amount = float(amount_str)
        price_usd = float(price_usd_str)
        decimals = TOKEN_DECIMALS.get(symbol, 18)
        final_usd_amount = (amount / (10**decimals)) * price_usd
        return final_usd_amount
    except (ValueError, TypeError):
        return 0.0

def create_wallet_features(df_raw):
    """
    Takes the raw transaction DataFrame and engineers features for each wallet.

    Args:
        df_raw (pd.DataFrame): The raw DataFrame loaded from the JSON file.

    Returns:
        pd.DataFrame: A DataFrame where each row is a wallet and each column is an engineered feature.
    """
    print("Engineering features...")
    
    # --- 1. Initial Data Cleaning & Preprocessing ---
    df = df_raw.copy()
    df['amountUSD'] = df.apply(_calculate_real_amount_usd, axis=1)
    df = df.rename(columns={'userWallet': 'wallet'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # --- 2. Aggregate Transaction Data ---
    wallet_actions = df.pivot_table(
        index='wallet', 
        columns='action', 
        values='amountUSD', 
        aggfunc='sum'
    ).fillna(0)
    wallet_actions.columns = [f"{col.lower()}_usd" for col in wallet_actions.columns]

    # --- 3. Create Feature DataFrame ---
    features = pd.DataFrame(index=wallet_actions.index)
    
    # Financial Features
    features['total_deposits_usd'] = wallet_actions.get('deposit_usd', 0)
    features['total_borrows_usd'] = wallet_actions.get('borrow_usd', 0)
    features['total_repays_usd'] = wallet_actions.get('repay_usd', 0)
    features['total_redeems_usd'] = wallet_actions.get('redeemunderlying_usd', 0)
    
    # Repayment Ratio
    features['repayment_ratio'] = features['total_repays_usd'] / (features['total_borrows_usd'] + 1e-6)
    features['repayment_ratio'] = features['repayment_ratio'].clip(upper=5)

    # Behavioral Features
    wallet_age = df.groupby('wallet')['timestamp'].agg(['min', 'max'])
    features['lifespan_days'] = (wallet_age['max'] - wallet_age['min']).dt.days
    
    wallet_counts = df.groupby('wallet')['action'].agg(
        transaction_count='count',
        liquidation_count=lambda x: (x == 'liquidationcall').sum()
    )
    features = features.join(wallet_counts)

    # --- 4. Final Cleanup ---
    features = features.fillna(0)
    
    print("Feature engineering complete.")
    return features