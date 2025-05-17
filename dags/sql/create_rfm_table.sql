DROP TABLE IF EXISTS team_twenty.rfm_unified;
CREATE TABLE IF NOT EXISTS team_twenty.rfm_unified AS
WITH 
recency_data AS (
    SELECT 
        a.client_id,
        a.login,
        CASE
            WHEN t.date_last_activity IS NOT NULL OR e.date_last_conv IS NOT NULL OR i.date_last_inouts IS NOT NULL THEN
                GREATEST(
                    t.date_last_activity::date,
                    e.date_last_conv::date,
                    i.date_last_inouts::date
                )
            ELSE NULL
        END AS last_activity_date,
        CASE
            WHEN t.date_last_activity IS NOT NULL OR e.date_last_conv IS NOT NULL OR i.date_last_inouts IS NOT NULL THEN
                CURRENT_DATE - GREATEST(
                    t.date_last_activity::date,
                    e.date_last_conv::date,
                    i.date_last_inouts::date
                )
            ELSE NULL
        END AS days_since_last_activity
    FROM 
        freedom_broker.accounts a
    LEFT JOIN 
        freedom_broker.trades t ON a.login = t.login
    LEFT JOIN 
        freedom_broker.exchange e ON a.client_id = e.client_id
    LEFT JOIN 
        freedom_broker.inouts i ON a.client_id = i.client_id
),

frequency_data AS (
    SELECT 
        a.client_id,
        a.login,
        COALESCE(t.cnt_trades, 0) AS trade_count,
        COALESCE(i.cnt_inouts, 0) AS inout_count,
        COALESCE(t.cnt_trades, 0) + COALESCE(i.cnt_inouts, 0) AS total_activity_count
    FROM 
        freedom_broker.accounts a
    LEFT JOIN 
        freedom_broker.trades t ON a.login = t.login
    LEFT JOIN 
        freedom_broker.inouts i ON a.client_id = i.client_id
),

monetary_data AS (
    SELECT 
        a.client_id,
        a.login,
        SUM(COALESCE(c.comission, 0)) AS total_commission,
        COALESCE(ins.sum_ins, 0) AS total_deposits,
        COALESCE(b.balance, 0) AS current_balance,
        (SUM(COALESCE(c.comission, 0)) * 10) + -- Higher weight to commissions
        (COALESCE(ins.sum_ins, 0) * 0.2) +     -- Lower weight to deposits
        (COALESCE(b.balance, 0) * 0.1)         -- Lowest weight to balance
        AS weighted_monetary_value
    FROM 
        freedom_broker.accounts a
    LEFT JOIN 
        freedom_broker.comissions c ON a.login = c.login
    LEFT JOIN 
        freedom_broker.ins ON a.client_id = ins.client_id
    LEFT JOIN 
        freedom_broker.balance b ON a.client_id = b.client_id
    GROUP BY 
        a.client_id, a.login, ins.sum_ins, b.balance
)

SELECT 
    a.client_id,
    a.login,
    a.age_segment,
    a.sex_type,
    a."Канал привлечения" AS acquisition_channel,
    a.type AS client_type,
    -- Recency metrics
    r.last_activity_date,
    r.days_since_last_activity AS recency_days,
    -- Frequency metrics
    f.trade_count,
    f.inout_count,
    f.total_activity_count AS frequency,
    -- Monetary metrics
    m.total_commission,
    m.total_deposits,
    m.current_balance,
    m.weighted_monetary_value AS monetary_value,
    -- Include timestamps for audit/tracking
    CURRENT_TIMESTAMP AS created_at
FROM 
    freedom_broker.accounts a
LEFT JOIN 
    recency_data r ON a.client_id = r.client_id
LEFT JOIN 
    frequency_data f ON a.client_id = f.client_id
LEFT JOIN 
    monetary_data m ON a.client_id = m.client_id;

CREATE INDEX IF NOT EXISTS idx_rfm_client_id ON team_twenty.rfm_unified(client_id);