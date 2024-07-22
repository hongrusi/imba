### Business background

Instacart, began in 2012 is a leading American delivery platform in the US, offering same-day delivery and pick-up from almost any chain grocer or retailer in the USA and Canada, accessible via a website and mobile app.  It allows users to purchase from some wholesale clubs (like Costco), even if you don’t have a club membership. Instacart itself does not hold any inventory

### Project objective

Develop and implement a robust infrastructure for the Next Item Order Prediction (NIOP) aimed at accurately predicting which specific items customers are most likely to purchase next.

### Project Valuae

This system can significantly boost sales and grow business in several ways.

- Use the prediction results to provide personalized product recommendations on the website, app, and via email marketing to increase the likelihood of additional purchases
- Recommend complementary products (cross-selling) or premium versions (upselling) of items that the customer is predicted to buy next.
- Offer special deals or discounts on items that a customer is predicted to buy to increase sales
- Send personalized alerts or notifications when predicted items go on sale, are back in stock, or when there are special deals related to these items
- Help inventory management by stock more of what is predicted to sell
- Adjust inventory at specific locations based on predicted regional purchase patterns
- Marketing strategies can be more effective by promoting products that are more likely to be purchased

### Dataset

The dataset is a relational set of files describing customers' online orders over time. The goal of the project is to predict which products will be in a user's next order. The dataset is anonymized and contains a sample of over 3 million grocery orders from more than 200,000 Instacart users. For each user, we provide between 4 and 100 of their orders, with the sequence of products purchased in each order. We also provide the week and hour of day the order was placed, and a relative measure of time between orders.

### Data Dictionary

`orders` (3.4m rows, 206k users):

- `order_id`: order identifier
- `user_id`: customer identifier
- `eval_set`: which evaluation set this order belongs in (see `SET` described below)
- `order_number`: the order sequence number for this user (1 = first, n = nth)
- `order_dow`: the day of the week the order was placed on
- `order_hour_of_day`: the hour of the day the order was placed on
- `days_since_prior`: days since the last order, capped at 30 (with NAs for `order_number` = 1)

`products` (50k rows):

- `product_id`: product identifier
- `product_name`: name of the product
- `aisle_id`: foreign key
- `department_id`: foreign key

`aisles` (134 rows):

- `aisle_id`: aisle identifier
- `aisle`: the name of the aisle

`deptartments` (21 rows):

- `department_id`: department identifier
- `department`: the name of the department

`order_products__SET` (30m+ rows):

- `order_id`: foreign key
- `product_id`: foreign key
- `add_to_cart_order`: order in which each product was added to cart
- `reordered`: 1 if this product has been ordered by this user in the past, 0 otherwise

where `SET` is one of the four following evaluation sets (`eval_set` in `orders`):

- `"prior"`: orders prior to that users most recent order (~3.2m orders)
- `"train"`: training data supplied to participants (~131k orders)
- `"test"`: test data reserved for machine learning competitions (~75k orders)