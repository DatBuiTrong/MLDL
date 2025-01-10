class SqlQueries:
    dim_customer_insert = ("""
        CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{dim_customer_id}` AS (
        SELECT 
            Customer_ID,
            Name,
            Email,
            Phone,
            Address,
            City_ID,
            Age,
            Gender,
            Income,
            Customer_Segment
        FROM {project_id}.{dataset_id}.{table_customer_raw_id};
        )
    """)

    dim_city_insert = ("""
        CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{dim_city_id}` AS (
        SELECT 
            CityId,
            City,
            State,
            Country
        FROM {project_id}.{dataset_id}.{table_city_raw_id};
        )
    """)

    dim_product_insert = ("""
        CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{dim_product_id}` AS (
        SELECT 
            Product_Id,
            Product_Name,
            Product_Category,
            Product_Brand,
            Product_Type
        FROM {project_id}.{dataset_id}.{table_product_raw_id};
        )
    """)

    fact_transaction_insert = ("""
        CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{fact_transaction_id}` AS (
        WITH Ranked_Transactions AS (
            SELECT 
                FT.*,
                ROW_NUMBER() OVER (PARTITION BY FT.Transaction_ID ORDER BY FT.Transaction_ID) AS rn
            FROM 
                {project_id}.{dataset_id}.{table_transaction_raw_id} FT
            )
        SELECT 
            RT.Transaction_ID,
            RT.Customer_ID,
            RT.Product_Id,
            PARSE_DATE('%Y%m%d', CAST(RT.Date AS STRING)) AS Date,
            RT.Time,
            RT.Quantity,
            RT.Price,
            RT.Feedback,
            RT.Shipping_Method,
            RT.Payment_Method,
            RT.Order_Status,
            RT.Ratings

        FROM 
            Ranked_Transactions RT
        JOIN 
            {project_id}.{dataset_id}.{dim_customer_id} DC 
        ON 
            RT.Customer_ID = DC.Customer_ID
        JOIN 
            {project_id}.{dataset_id}.{dim_product_id} DP 
        ON 
            RT.Product_Id = DP.Product_Id
        WHERE 
            RT.rn = 1;
        )
    """)

