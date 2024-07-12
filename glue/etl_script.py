import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession
from awsglue.context import GlueContext
from awsglue.job import Job
  

def main():

    # create glue context first
    sc = SparkSession.builder.getOrCreate()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    
    # TODO ---------------------------------------------------
    # write codes to produce pyspark dataframes for up_features,prd_features,user_features_1, user_features_2 according to the sql queries you written.
    # write the dataframe to s3 location with parquet format (e.g. write up_feature dataframe to s3://<your s3 bucket>/features/up_feature/)

    dy_orders = glueContext.create_dynamic_frame.from_catalog(database='imba', table_name='orders')
    df_orders = dy_orders.toDF()

    dy_order_product = glueContext.create_dynamic_frame.from_catalog(database='imba', table_name='order_product')
    df_order_product = dy_order_product.toDF()

    df_join = df_orders.join(df_order_product, on='order_id', how='inner')
    df_filter = df_join.filter(df_join.eval_set=='prior')
    df_filter.write.mode('overwrite').format('parquet').save("s3://imba-stanley/data/order_product_prior")


    # User Feature 1
    df_orders.createOrReplaceTempView("orders")
    query="""
            SELECT user_id,
            Max(order_number) AS user_orders
            ,Sum(days_since_prior_order) AS user_period
            ,Avg(days_since_prior_order) AS user_mean_days_since_prior 
            FROM orders 
            GROUP BY user_id"""
    df_uf1 = spark.sql(query)


    # User Feature 2
    df_order_products_prior = spark.read.format("parquet").load("s3://imba-stanley/data/order_product_prior")
    df_order_products_prior.createOrReplaceTempView('order_products_prior')
    query ="""
            SELECT user_id
                ,count(product_id) AS user_total_products
                ,count(DISTINCT product_id) AS user_distinct_products
                ,SUM(CASE WHEN reordered = 1 AND order_number > 1 THEN 1 ELSE 0 END) * 1.0 
                    / SUM(CASE WHEN order_number > 1 THEN 1 ELSE 0 END) AS user_reorder_ratio
            FROM order_products_prior
            GROUP BY user_id
            """
    df_uf2 = spark.sql(query)


    # Up Features
    query ="""
            SELECT
                user_id,
                product_id,
                count(order_id) AS up_orders,
                min(order_number) AS up_first_order,
                max(order_number) AS up_last_order,
                avg(add_to_cart_order) AS up_average_cart_position
            FROM order_products_prior
            GROUP BY user_id, product_id
            """
   
    df_upf = spark.sql(query)


    # Prod Features
    query="""
            SELECT t.product_id
                    ,count(t.product_id) AS prod_orders
                    ,sum(t.reordered) AS prod_reorders
                    ,sum(case when t.product_seq_time = 1 then 1 else 0 end) AS prod_first_orders
                    ,sum(case when t.product_seq_time = 2 then 1 else 0 end) AS prod_second_orders 
            FROM 
            (
                    SELECT user_id
                        ,order_number
                        ,product_id
                        ,reordered
                        ,row_number()over(partition by user_id, product_id order by order_number) as product_seq_time
                    FROM order_products_prior
            ) t
            GROUP BY t.product_id
            """

    df_prod = spark.sql(query)


    # END TODO ---------------------------------------------------
    
    
    # join user features together
    df_uf1 = df_uf1.withColumnRenamed('user_id', 'user_id1')
    users = df_uf1.join(df_uf2, df_uf1.user_id1 == df_uf2.user_id).drop('user_id1')
    
    # join everything together
    df = df_upf.join(users, on='user_id',how='inner')\
        .join(df_prod,on='product_id')
          
    # convert glue dynamic dataframe to spark dataframe
    df.repartition(1).write.mode('overwrite').format('csv').option('header', 'true').save("s3://imba-stanley/output")
    
if __name__ == '__main__':
    main()
