import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import lifelines
from lifelines import CoxPHFitter

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    try:
        data = pd.read_csv(filepath)
        print(f"Successfully loaded data with {data.shape[0]} rows and {data.shape[1]} columns.")
        return data
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        exit(1)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        exit(1)

def prepare_features(data):
    print("Preparing features for prediction...")
    
    model_data = data.copy()
    
    date_columns = ['last_activity_date', 'created_at']
    for col in date_columns:
        if col in model_data.columns:
            try:
                model_data[col] = pd.to_datetime(model_data[col], utc=True)
                print(f"Sample {col} value: {model_data[col].iloc[0]} (type: {type(model_data[col].iloc[0])})")
            except Exception as e:
                print(f"Warning: Couldn't convert {col} to datetime: {str(e)}")
    
    if 'created_at' in model_data.columns and pd.api.types.is_datetime64_any_dtype(model_data['created_at']):
        try:
            now = pd.Timestamp.now(tz='UTC')
            model_data['account_age_days'] = (now - model_data['created_at']).dt.days
            print(f"Successfully calculated account_age_days from created_at")
        except Exception as e:
            print(f"Error calculating account age: {str(e)}")
            if 'recency_days' in model_data.columns:
                model_data['account_age_days'] = model_data['recency_days'] * 2
                print(f"Using fallback calculation: account_age_days = recency_days * 2")
    else:
        if 'recency_days' in model_data.columns:
            model_data['account_age_days'] = model_data['recency_days'] * 2
            print(f"Using fallback calculation: account_age_days = recency_days * 2")
        else:
            model_data['account_age_days'] = 365  # Default to 1 year
            print(f"No date information available. Using default account_age_days = 365")
    
    if 'trade_count' in model_data.columns and 'account_age_days' in model_data.columns:
        model_data['trade_frequency'] = model_data['trade_count'] / model_data['account_age_days'].replace(0, 1)
        print(f"Calculated trade_frequency from trade_count and account_age_days")
    elif 'frequency' in model_data.columns and 'account_age_days' in model_data.columns:
        model_data['trade_frequency'] = model_data['frequency'] / model_data['account_age_days'].replace(0, 1)
        print(f"Calculated trade_frequency from frequency and account_age_days")
    
    if 'monetary_value' in model_data.columns and 'trade_count' in model_data.columns:
        trade_count_safe = model_data['trade_count'].replace(0, 1)  # Avoid division by zero
        model_data['avg_value_per_trade'] = model_data['monetary_value'] / trade_count_safe
        print(f"Calculated avg_value_per_trade")
    
    if 'total_commission' in model_data.columns and 'trade_count' in model_data.columns:
        trade_count_safe = model_data['trade_count'].replace(0, 1)
        model_data['avg_commission_per_trade'] = model_data['total_commission'] / trade_count_safe
        print(f"Calculated avg_commission_per_trade")
    
    potential_features = [
        'recency_days',           
        'frequency',              
        'trade_count',            
        'inout_count',            
        'total_commission',       
        'monetary_value',         
        'total_deposits',         
        'current_balance',       
        'cluster',                
        'gmm_cluster',            
        'account_age_days',       
        'trade_frequency',        
        'avg_value_per_trade',    
        'avg_commission_per_trade'
    ]
    
    available_features = [f for f in potential_features if f in model_data.columns]
    
    if not available_features:
        print("Error: None of the expected prediction features are available in the data.")
        print(f"Available columns: {model_data.columns.tolist()}")
        exit(1)
    
    print(f"Using these features for prediction: {available_features}")
    return model_data, available_features

def predict_next_trade_simple(data, features):
    print("Using simplified prediction method based on trading patterns...")
    
    predictions = data.copy()
    
    if 'trade_count' in features and 'account_age_days' in predictions.columns:
        trade_count_safe = predictions['trade_count'].replace(0, 1)  # Avoid division by zero
        
        predictions['avg_days_between_trades'] = predictions['account_age_days'] / trade_count_safe
        print("Calculated avg_days_between_trades from trade_count")
    elif 'frequency' in features and 'account_age_days' in predictions.columns:
        frequency_safe = predictions['frequency'].replace(0, 1)
        predictions['avg_days_between_trades'] = predictions['account_age_days'] / frequency_safe
        print("Calculated avg_days_between_trades from frequency")
    else:
        if 'cluster' in features:
            cluster_avg_recency = data.groupby('cluster')['recency_days'].mean()
            predictions['avg_days_between_trades'] = predictions['cluster'].map(cluster_avg_recency)
            print("Calculated avg_days_between_trades from cluster averages")
        else:
            predictions['avg_days_between_trades'] = data['recency_days'].mean()
            print("Using recency_days mean as avg_days_between_trades")
    
    predictions['avg_days_between_trades'] = np.minimum(predictions['avg_days_between_trades'], 180)
    
    if 'recency_days' in features:
        predictions['predicted_days_to_next_trade'] = (
            predictions['avg_days_between_trades'] - predictions['recency_days']
        )
        
        overdue_mask = predictions['predicted_days_to_next_trade'] < 0
        num_overdue = overdue_mask.sum()
        
        if num_overdue > 0:
            predictions.loc[overdue_mask, 'predicted_days_to_next_trade'] = np.random.randint(1, 15, size=num_overdue)
            print(f"Found {num_overdue} overdue customers, assigned random 1-15 day predictions")
        
        if 'cluster' in features:
            cluster_std = data.groupby('cluster')['recency_days'].std().fillna(10)
            for cluster in predictions['cluster'].unique():
                mask = predictions['cluster'] == cluster
                std = cluster_std.get(cluster, 10)
                noise = np.random.normal(0, std/2, size=sum(mask))
                predictions.loc[mask, 'predicted_days_to_next_trade'] += noise
        else:
            std = data['recency_days'].std() if 'recency_days' in features else 10
            noise = np.random.normal(0, std/2, size=len(predictions))
            predictions['predicted_days_to_next_trade'] += noise
        
        predictions['predicted_days_to_next_trade'] = np.maximum(1, predictions['predicted_days_to_next_trade'])
        
    else:
        predictions['predicted_days_to_next_trade'] = 30 
        print("No recency data available, using default 30 days prediction")
    
    today = datetime.now().date()
    predictions['predicted_next_trade_date'] = predictions['predicted_days_to_next_trade'].apply(
        lambda x: (today + timedelta(days=int(round(x)))).strftime('%Y-%m-%d')
    )
    
    predictions['trade_probability_7days'] = 1 / (1 + np.exp(0.3 * (predictions['predicted_days_to_next_trade'] - 7)))
    predictions['trade_probability_30days'] = 1 / (1 + np.exp(0.1 * (predictions['predicted_days_to_next_trade'] - 30)))
    predictions['trade_probability_90days'] = 1 / (1 + np.exp(0.05 * (predictions['predicted_days_to_next_trade'] - 90)))
    
    if 'avg_commission_per_trade' in predictions.columns:
        predictions['expected_commission_30days'] = (
            predictions['avg_commission_per_trade'] * predictions['trade_probability_30days']
        )
        predictions['expected_commission_90days'] = (
            predictions['avg_commission_per_trade'] * predictions['trade_probability_90days']
        )
    
    predictions['trading_urgency_score'] = predictions['trade_probability_30days'] * 10
    
    if 'monetary_value' in features:
        max_monetary = predictions['monetary_value'].max()
        if max_monetary > 0:
            monetary_normalized = predictions['monetary_value'] / max_monetary
            predictions['trading_urgency_score'] += monetary_normalized * 3
    
    if 'current_balance' in features:
        max_balance = predictions['current_balance'].max()
        if max_balance > 0:
            balance_normalized = predictions['current_balance'] / max_balance
            predictions['trading_urgency_score'] += balance_normalized * 2
    
    predictions['trading_urgency_category'] = pd.cut(
        predictions['trading_urgency_score'],
        bins=[0, 5, 8, 12, 100],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
    
    return_columns = [
        'predicted_days_to_next_trade', 
        'predicted_next_trade_date',
        'trade_probability_7days',
        'trade_probability_30days', 
        'trade_probability_90days',
        'trading_urgency_score',
        'trading_urgency_category'
    ]
    
    if 'expected_commission_30days' in predictions.columns:
        return_columns.extend(['expected_commission_30days', 'expected_commission_90days'])
    
    return predictions[return_columns]

def predict_next_trade_survival(data, features):
    print("Using survival analysis to predict next trade...")
    
    survival_data = data.copy()

    if 'recency_days' not in survival_data.columns:
        print("Error: recency_days column required for survival analysis")
        return predict_next_trade_simple(data, features)
    
    survival_data['duration'] = survival_data['recency_days']
    survival_data['event'] = 0  
    model_features = [f for f in features if f != 'recency_days']
    
    categorical_features = ['age_segment', 'sex_type', 'acquisition_channel', 'client_type']
    for col in categorical_features:
        if col in survival_data.columns:
            try:
                dummies = pd.get_dummies(survival_data[col], prefix=col, drop_first=True)
                survival_data = pd.concat([survival_data, dummies], axis=1)
                model_features.extend(dummies.columns.tolist())
                if col in model_features:
                    model_features.remove(col)
            except Exception as e:
                print(f"Warning: Couldn't create dummies for {col}: {str(e)}")
    
    if not model_features and 'cluster' in survival_data.columns:
        model_features = ['cluster']
    
    if not model_features:
        print("Warning: No suitable features for survival analysis")
        return predict_next_trade_simple(data, features)
    
    # Cox Proportional Hazards model
    cph = CoxPHFitter()
    try:
        for col in model_features:
            if survival_data[col].dtype == 'object':
                try:
                    survival_data[col] = pd.to_numeric(survival_data[col])
                except:
                    print(f"Warning: Could not convert column {col} to numeric. Dropping from model.")
                    model_features.remove(col)
        
        for col in model_features.copy():
            if survival_data[col].isnull().any():
                print(f"Warning: Column {col} has missing values. Filling with median.")
                survival_data[col] = survival_data[col].fillna(survival_data[col].median())
        
        print(f"Fitting survival model with features: {model_features}")
        cph.fit(survival_data[model_features + ['duration', 'event']], 
                duration_col='duration', 
                event_col='event')
        
        print("\nSurvival Model Summary:")
        print(cph.summary)
        
        time_horizons = [7, 30, 90, 180] 
        
        survival_func = cph.predict_survival_function(survival_data[model_features])
        
        predictions = pd.DataFrame(index=survival_data.index)
        
        for t in time_horizons:
            if t in survival_func.index:
                predictions[f'trade_probability_{t}days'] = 1 - survival_func.loc[t].values
            else:
                closest_t = min(survival_func.index, key=lambda x: abs(x - t))
                predictions[f'trade_probability_{t}days'] = 1 - survival_func.loc[closest_t].values
        
        median_time = cph.predict_median(survival_data[model_features])
        predictions['predicted_days_to_next_trade'] = median_time.values
        
        today = datetime.now().date()
        predictions['predicted_next_trade_date'] = predictions['predicted_days_to_next_trade'].apply(
            lambda x: (today + timedelta(days=int(round(x)))).strftime('%Y-%m-%d')
        )
        
        if 'avg_commission_per_trade' in survival_data.columns:
            predictions['expected_commission_30days'] = (
                survival_data['avg_commission_per_trade'] * predictions['trade_probability_30days']
            )
            predictions['expected_commission_90days'] = (
                survival_data['avg_commission_per_trade'] * predictions['trade_probability_90days']
            )
        
        predictions['trading_urgency_score'] = predictions['trade_probability_30days'] * 10
        
        if 'monetary_value' in features:
            max_monetary = survival_data['monetary_value'].max()
            if max_monetary > 0:
                monetary_normalized = survival_data['monetary_value'] / max_monetary
                predictions['trading_urgency_score'] += monetary_normalized * 3
        
        if 'current_balance' in features:
            max_balance = survival_data['current_balance'].max()
            if max_balance > 0:
                balance_normalized = survival_data['current_balance'] / max_balance
                predictions['trading_urgency_score'] += balance_normalized * 2
        
        predictions['trading_urgency_category'] = pd.cut(
            predictions['trading_urgency_score'],
            bins=[0, 5, 8, 12, 100],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        return predictions
        
    except Exception as e:
        print(f"Error in survival analysis: {str(e)}")
        print("Falling back to simplified prediction method")
        return predict_next_trade_simple(data, features)

def main():
    """Main function to run the prediction pipeline."""
    print("=" * 50)
    print("Freedom Broker Customer Return Prediction (Fixed TZ Version)")
    print("=" * 50)
    
    input_file = "rfm_segmented.csv"
    output_file = "next_trade_predictions.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        exit(1)
    
    # Load data
    data = load_data(input_file)
    
    # Prepare features
    model_data, features = prepare_features(data)
    
    predictions = predict_next_trade_survival(model_data, features)
    prediction_method = "Survival Analysis"

    # SIMPLER METHOD
    # predictions = predict_next_trade_simple(model_data, features)
    # prediction_method = "Simple Method"
    
    essential_columns = [
        'client_id', 'login', 'age_segment', 'sex_type', 
        'acquisition_channel', 'client_type', 'recency_days',
        'trade_count', 'frequency', 'total_commission', 
        'monetary_value', 'current_balance', 'cluster'
    ]
    
    essential_columns = [col for col in essential_columns if col in data.columns]
    result = pd.concat([data[essential_columns], predictions], axis=1)
    
    result.to_csv(output_file, index=False)
    print(f"Predictions saved to '{output_file}'")
    
    print(f"\nPrediction Summary (using {prediction_method}):")
    print(f"Average days to next trade: {predictions['predicted_days_to_next_trade'].mean():.1f}")
    
    if 'cluster' in data.columns:
        cluster_summary = result.groupby('cluster')['predicted_days_to_next_trade'].mean().sort_values()
        print("\nAverage days to next trade by cluster:")
        for cluster, avg_days in cluster_summary.items():
            print(f"  Cluster {cluster}: {avg_days:.1f} days")
    
    if 'age_segment' in data.columns:
        age_summary = result.groupby('age_segment')['predicted_days_to_next_trade'].mean().sort_values()
        print("\nAverage days to next trade by age segment:")
        for age, avg_days in age_summary.items():
            print(f"  {age}: {avg_days:.1f} days")
    
    if 'client_type' in data.columns:
        type_summary = result.groupby('client_type')['predicted_days_to_next_trade'].mean().sort_values()
        print("\nAverage days to next trade by client type:")
        for client_type, avg_days in type_summary.items():
            print(f"  {client_type}: {avg_days:.1f} days")
    
    print("\nPercentage of customers likely to trade in:")
    print(f"  Next 7 days: {(predictions['trade_probability_7days'] > 0.5).mean() * 100:.1f}%")
    print(f"  Next 30 days: {(predictions['trade_probability_30days'] > 0.5).mean() * 100:.1f}%")
    print(f"  Next 90 days: {(predictions['trade_probability_90days'] > 0.5).mean() * 100:.1f}%")
    
    urgency_counts = predictions['trading_urgency_category'].value_counts()
    print("\nCustomers by trading urgency category:")
    total = len(predictions)
    for category, count in urgency_counts.items():
        percentage = 100 * count / total
        print(f"  {category}: {count} customers ({percentage:.1f}%)")
    
    print("\nNext Trade Prediction completed successfully!")

if __name__ == "__main__":
    main()