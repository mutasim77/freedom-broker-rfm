DROP TABLE IF EXISTS team_twenty.rfm_segmentation;
CREATE TABLE team_twenty.rfm_segmentation AS
WITH rfm_scores AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_value DESC) AS m_score
    FROM team_twenty.rfm_unified
),
rfm_segments AS (
    SELECT
        *,
        r_score::text || f_score::text || m_score::text AS rfm_score,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            
            WHEN r_score >= 4 AND f_score >= 3 AND m_score < 3 THEN 'Potential Loyalists'
            
            WHEN r_score >= 4 AND f_score < 2 THEN 'New Customers'
            
            WHEN r_score >= 4 AND f_score < 2 AND m_score >= 4 THEN 'Promising'
            
            WHEN r_score < 3 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
            
            WHEN r_score < 2 AND f_score >= 4 AND m_score >= 4 THEN 'Cant Lose Them'
            
            WHEN r_score < 2 AND f_score < 2 AND m_score < 2 THEN 'Hibernating'
            
            WHEN r_score < 3 AND f_score < 3 AND m_score >= 2 THEN 'About to Sleep'
            
            WHEN r_score < 3 AND f_score >= 2 AND f_score < 4 THEN 'Need Attention'
            
            ELSE 'Other'
        END AS segment_name
    FROM rfm_scores
)
SELECT * FROM rfm_segments;

CREATE INDEX IF NOT EXISTS idx_segment_client_id ON team_twenty.rfm_segmentation(client_id);
CREATE INDEX IF NOT EXISTS idx_segment_segment ON team_twenty.rfm_segmentation(segment_name);