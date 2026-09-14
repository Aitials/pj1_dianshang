#create database olist;
use olist;

create table olist_customers_dataset_clean(
    customer_id character(35) primary key not null ,
    customer_unique_id character(35)not null,
    customer_zip_code_prefix character(5)not null,
    customer_city varchar(40)not null,
    customer_state character(2)not null
);

create table olist_geolocation_dataset_clean(
    geolocation_zip_code_prefix character(5) primary key not null,
    geolocation_lat float8 not null,
    geolocation_lng float8 not null,
    geolocation_city varchar(50)not null,
    geolocation_state character(2)not null
);

create table olist_order_items_dataset_clean(
    order_id character(35)not null ,
    order_item_id int not null ,
    product_id character(35)not null,
    seller_id character(35)not null,
    shipping_limit_date datetime not null,
    price decimal(12,2)not null,
    freight_value decimal(12,2)not null,
    primary key (order_id,order_item_id)
);

create table olist_order_payments_dataset_clean(
    order_id character(35) not null,
    payment_sequential int not null,
    payment_type varchar(15) not null,
    payment_installments int not null,
    payment_value decimal(12,2)not null,
    primary key (order_id,payment_sequential)
);

create table olist_order_reviews_dataset_clean(
    review_id character(35) not null primary key ,
    order_id character(35) not null ,
    review_score int not null ,
    review_comment_title varchar(50),
    review_comment_message varchar(500),
    review_creation_date datetime,
    review_answer_timestamp datetime
);

create table olist_orders_dataset_clean(
    order_id character(35) primary key not null ,
    customer_id character(35) not null ,
    order_status character(15) not null ,
    order_purchase_timestamp datetime,
    order_approved_at datetime,
    order_delivered_carrier_date datetime,
    order_delivered_customer_date datetime,
    order_estimated_delivery_date datetime
);

create table olist_products_dataset_clean(
    product_id character(35) primary key not null ,
    product_category_name varchar(50) not null ,
    product_name_length int ,
    product_description_length int ,
    product_photos_qty tinyint ,
    product_weight_g int,
    product_length_cm int,
    product_height_cm int,
    product_width_cm int
);

create table olist_sellers_dataset_clean(
    seller_id character(35) not null  primary key ,
    seller_zip_code_prefix  character(5) not null ,
    seller_city varchar(50) not null ,
    seller_state character(2) not null
);

create table product_category_name_translation_clean(
    product_category_name varchar(50) not null primary key ,
    product_category_name_english varchar(50) not null
);

create index idx_customers_uniqe_id on olist_customers_dataset_clean(customer_unique_id);

create index idx_product_id on olist_order_items_dataset_clean(product_id);
create index idx_seller_id on olist_order_items_dataset_clean(seller_id);

create index idx_payment_type on olist_order_payments_dataset_clean(payment_type);

create index idx_order_id on olist_order_reviews_dataset_clean(order_id);
create index idx_review on olist_order_reviews_dataset_clean(review_score);

create index idx_customers_id on olist_orders_dataset_clean(customer_id);
create index idx_purchase_timestamp on olist_orders_dataset_clean(order_purchase_timestamp);

create index idx_product_category_name on olist_products_dataset_clean(product_category_name);


#业务建表



