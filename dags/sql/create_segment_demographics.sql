DROP TABLE IF EXISTS schema_twenty.rfm_segment_demographics;
CREATE TABLE schema_twenty.rfm_segment_demographics AS
WITH age_dist AS (
    SELECT
        segment_name,
        age_segment,
        COUNT(*) AS count,
        (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY segment_name))::numeric(10,2) AS percentage
    FROM schema_twenty.rfm_segmentation
    GROUP BY segment_name, age_segment
),
gender_dist AS (
    SELECT
        segment_name,
        sex_type,
        COUNT(*) AS count,
        (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY segment_name))::numeric(10,2) AS percentage
    FROM schema_twenty.rfm_segmentation
    GROUP BY segment_name, sex_type
),
acquisition_dist AS (
    SELECT
        segment_name,
        acquisition_channel,
        COUNT(*) AS count,
        (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY segment_name))::numeric(10,2) AS percentage
    FROM schema_twenty.rfm_segmentation
    GROUP BY segment_name, acquisition_channel
),
client_type_dist AS (
    SELECT
        segment_name,
        client_type,
        COUNT(*) AS count,
        (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY segment_name))::numeric(10,2) AS percentage
    FROM schema_twenty.rfm_segmentation
    GROUP BY segment_name, client_type
)

SELECT
    segment_name,
    'age_segment' AS demographic_type,
    age_segment AS demographic_value,
    count,
    percentage
FROM age_dist

UNION ALL

SELECT
    segment_name,
    'sex_type' AS demographic_type,
    sex_type AS demographic_value,
    count,
    percentage
FROM gender_dist

UNION ALL

SELECT
    segment_name,
    'acquisition_channel' AS demographic_type,
    acquisition_channel AS demographic_value,
    count,
    percentage
FROM acquisition_dist

UNION ALL

SELECT
    segment_name,
    'client_type' AS demographic_type,
    client_type AS demographic_value,
    count,
    percentage
FROM client_type_dist

ORDER BY segment_name, demographic_type, percentage DESC;