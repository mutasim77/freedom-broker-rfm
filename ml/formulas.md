# The Mathematical Formulas Used For Prediction

1. Trade Frequency:
```py
trade_frequency = trade_count / account_age_days
```

2. Average Days Between Trades
```py
avg_days_between_trades = account_age_days / trade_count
```

3. Predicted Days Until Next Trade
```py
predicted_days_to_next_trade = avg_days_between_trades - recency_days
```

4. Trading Probability (using sigmoid function):
```py
trade_probability_30days = 1 / (1 + exp(0.1 * (predicted_days_to_next_trade - 30)))
```

5. Expected Commission
```py
expected_commission_30days = avg_commission_per_trade * trade_probability_30days
```

6. Trading Urgency Score
```py
trading_urgency_score = (trade_probability_30days * 10) + 
                       (normalized_monetary_value * 3) + 
                       (normalized_current_balance * 2)
```