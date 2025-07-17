import pandas as pd
import argparse
import sys

# We need to add the 'src' directory to the Python path so we can import our modules.
# This is a common pattern for structuring Python projects.
sys.path.append('src')

from feature_engineering import create_wallet_features
from scoring import calculate_credit_scores

def main():
    """
    The main function to run the wallet scoring pipeline.
    """
    # --- 1. Set up Command-Line Argument Parser ---
    parser = argparse.ArgumentParser(description="Calculate credit scores for Aave wallets from transaction data.")
    parser.add_argument(
        "--input_file", 
        type=str, 
        required=True, 
        help="Path to the user-transactions.json file."
    )
    parser.add_argument(
        "--output_file", 
        type=str, 
        default="wallet_scores.csv", 
        help="Path to save the output CSV file. (default: wallet_scores.csv)"
    )
    args = parser.parse_args()

    # --- 2. Load Data ---
    print(f"Loading data from {args.input_file}...")
    try:
        # Using lines=True is more robust for this kind of JSON data
        df_raw = pd.read_json(args.input_file, lines=True)
    except ValueError:
        # Fallback for standard JSON array format
        df_raw = pd.read_json(args.input_file)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input_file}'")
        return # Exit the function

    # --- 3. Run the Pipeline ---
    # Step 1: Create features from raw data
    features_df = create_wallet_features(df_raw)
    
    # Step 2: Calculate scores from the features
    scores_df = calculate_credit_scores(features_df)

    # --- 4. Prepare and Save Final Output ---
    # Select and reorder columns for a clean output file
    final_output = scores_df[['credit_score', 'lifespan_days', 'transaction_count', 'liquidation_count', 'repayment_ratio']].sort_values('credit_score', ascending=False)
    
    print(f"Saving final scores to {args.output_file}...")
    final_output.to_csv(args.output_file)
    
    print("\n--- Process Finished Successfully! ---")
    print(f"Top 5 Wallets by Credit Score:")
    print(final_output.head())
    print("\n")


if __name__ == "__main__":
    main()