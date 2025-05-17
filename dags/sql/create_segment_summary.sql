DROP TABLE IF EXISTS schema_twenty.rfm_segment_summary;
CREATE TABLE schema_twenty.rfm_segment_summary AS
SELECT
    segment_name,
    COUNT(*) AS client_count,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM schema_twenty.rfm_segmentation))::numeric(10,2) AS percent_of_clients,
    
    AVG(recency_days)::numeric(10,2) AS avg_recency_days,
    MIN(recency_days) AS min_recency_days,
    MAX(recency_days) AS max_recency_days,
    
    AVG(frequency)::numeric(10,2) AS avg_frequency,
    SUM(trade_count) AS total_trades,
    SUM(inout_count) AS total_inouts,
    
    SUM(total_commission)::numeric(20,2) AS total_commission,
    AVG(total_commission)::numeric(10,2) AS avg_commission_per_client,
    SUM(total_deposits)::numeric(20,2) AS total_deposits,
    SUM(current_balance)::numeric(20,2) AS total_balance,
    
    (SUM(total_commission) * 100.0 / 
     NULLIF((SELECT SUM(total_commission) FROM schema_twenty.rfm_segmentation), 0))::numeric(10,2) AS revenue_contribution_percent,
     
    AVG(r_score)::numeric(10,2) AS avg_r_score,
    AVG(f_score)::numeric(10,2) AS avg_f_score,
    AVG(m_score)::numeric(10,2) AS avg_m_score
    
FROM schema_twenty.rfm_segmentation
GROUP BY segment_name
ORDER BY revenue_contribution_percent DESC NULLS LAST;