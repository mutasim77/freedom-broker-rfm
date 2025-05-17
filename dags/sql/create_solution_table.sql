DROP TABLE IF EXISTS team_twenty.task1_solution;
CREATE TABLE team_twenty.task1_solution AS
SELECT
    client_id,
    login,
    recency_days AS recency,
    frequency,
    monetary_value AS monetary,
    r_score,
    f_score,
    m_score,
    rfm_score,
    segment_name,
    -- Additional useful fields
    total_commission,
    total_deposits,
    current_balance,
    trade_count,
    inout_count,
    last_activity_date,
    age_segment,
    sex_type,
    acquisition_channel,
    client_type,
    created_at
FROM team_twenty.rfm_segmentation;

CREATE INDEX IF NOT EXISTS idx_solution_client_id ON team_twenty.task1_solution(client_id);
CREATE INDEX IF NOT EXISTS idx_solution_segment ON team_twenty.task1_solution(segment_name);

SELECT segment_name, COUNT(*) AS count
FROM team_twenty.task1_solution
GROUP BY segment_name
ORDER BY count DESC;