CREATE OR REPLACE TABLE `{{ params.project_id }}.{{ params.dataset_id }}.example` AS
SELECT * FROM `{{ params.project_id }}.{{ params.dataset_id }}.loaded_example`
