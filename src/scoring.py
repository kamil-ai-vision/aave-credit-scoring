import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Define the weights for each feature. This is the core of the heuristic model.
# These can be tuned to adjust the scoring logic.
WEIGHTS = {
    # Positive Indicators (Good Behavior)
    'repayment_ratio': 25,      # Most important positive factor
    'lifespan_days': 10,        # Longer activity is better
    'total_deposits_usd': 15,   # Higher value deposited is a good sign
    'transaction_count': 5,     # General activity level
    
    # Negative Indicators (Risky Behavior)
    'liquidation_count': -50    # Most important negative factor
}

def calculate_credit_scores(features_df):
    """
    Calculates credit scores for each wallet based on engineered features.

    Args:
        features_df (pd.DataFrame): The DataFrame containing engineered features for each wallet.

    Returns:
        pd.DataFrame: The input DataFrame with an added 'credit_score' column.
    """
    print("Calculating credit scores...")
    
    # --- 1. Normalize Features ---
    # We only scale the features that are part of our scoring model.
    features_to_scale = [col for col in features_df.columns if col in WEIGHTS]
    
    # Check if there are any features to scale to avoid errors with empty data
    if not features_to_scale:
        print("Warning: No features found to calculate scores. Returning original data.")
        features_df['credit_score'] = 0
        return features_df

    scaler = MinMaxScaler()
    normalized_features = pd.DataFrame(
        scaler.fit_transform(features_df[features_to_scale]),
        columns=features_to_scale,
        index=features_df.index
    )

    # --- 2. Calculate Raw Score ---
    # Multiply the normalized features by their weights and sum them up.
    raw_score = (normalized_features * pd.Series(WEIGHTS)).sum(axis=1)

    # --- 3. Scale Final Score to 0-1000 ---
    # Use another scaler to map the raw scores to the desired 0-1000 range.
    final_score_scaler = MinMaxScaler(feature_range=(0, 1000))
    
    # Reshape the raw_score Series to a 2D array for the scaler
    scores_reshaped = raw_score.values.reshape(-1, 1)
    
    final_scores = final_score_scaler.fit_transform(scores_reshaped)

    # --- 4. Add Score to DataFrame ---
    # Create a copy to avoid SettingWithCopyWarning
    result_df = features_df.copy()
    result_df['credit_score'] = final_scores.astype(int)
    
    print("Credit score calculation complete.")
    return result_df