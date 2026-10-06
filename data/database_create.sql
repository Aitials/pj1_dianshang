-- ============================================================================
--  data/database_create.sql
--  项目数据库初始化脚本 —— 全库 DDL 的唯一来源
--
--  内容：建库 + 18 张表 + 全部索引 + RBAC 初始数据
--        9 张 Olist 业务表 / 5 张 RBAC 表 / 库存 2 张 / 操作日志 1 张 / AI 问答 1 张
--        3 个角色 / 12 个权限 / 1 个管理员账号
--
--  用法：
--    本地   ：mysql -uroot -p < data/database_create.sql
--    Docker ：MySQL 容器首次初始化时自动执行（脚本挂到 /docker-entrypoint-initdb.d/）
--
--  适用场景：⚠️ 只用于【初始化空库】—— 本地新库 / Docker 首次初始化 / down -v 重置之后
--
--  幂等性：建表用 CREATE TABLE IF NOT EXISTS、写数据用 INSERT IGNORE，重复执行不报错。
--    但有两个限制必须知道：
--    a) IF NOT EXISTS 对【已存在的表】是整表跳过，不会补建缺失的索引。
--       若某张表已存在却缺索引，只能先 DROP TABLE 再重跑本脚本。
--    b) system_role_permission / system_user_role 只有 id 主键，缺少
--       (role_id, permission_id) / (user_id, role_id) 唯一约束，
--       因此 INSERT IGNORE 是按 id 去重的。
--       在【已有 RBAC 数据的库】上执行会因 id 对不上而插入重复授权：
--       例 —— 现有库里 (role 1, permission 12) 的 id 是 26，而本脚本用的是 id 12，
--       id 不冲突 → 会再插一条，于是同一个授权出现两行。
--    → 结论：已有数据的库【不要】重复执行本脚本。
--      根治办法是给这两张表补唯一约束，但那是针对现有库的结构变更，未在本次改动范围内。
--
--  初始管理员（首次部署用；登录后请立即改密码）：
--    用户名：admin
--    密码  ：Olist@Admin2026
--    ⚠️ 本仓库是公开仓库，这串密码等同于公开信息，务必尽快修改。
--       改密入口：PUT /api/users/{id}（需 user:update 权限，用 admin 登录后调用）
--       项目目前没有"用户自助改密码"接口，只能用管理员账号改。
--
--  －－ 与上一版的差异（供审查） －－－－－－－－－－－－－－－－－－－－－－
--  1. 补齐了原先只由 ORM 的 Base.metadata.create_all 创建的 9 张表：
--     system_user / system_role / system_permission / system_user_role /
--     system_role_permission / inventory / inventory_log / operation_log / ai_analysis
--     原因：本脚本要成为唯一 DDL 来源；否则新机器上这 9 张表永远不落地，
--           seed_inventory.py 会因 inventory 不存在而直接失败。
--  2. 索引由独立的 CREATE INDEX 语句改为写在 CREATE TABLE 内的 KEY 子句。
--     原因：MySQL 不支持 CREATE INDEX IF NOT EXISTS，独立语句无法幂等；
--          写进建表语句后，配合 IF NOT EXISTS 才能重复执行。
--     索引数量与旧版一致（业务表共 9 个）。
--  3. 字符类型统一：原 character(35)/character(5)/character(2) 改为
--     varchar(35)/(5)/(2)。原因：CHAR 是定长、不足会补空格（32 位 ID 补 3 个空格），
--     且 SQLAlchemy 模型声明的是 String(n) 即 VARCHAR，两边应对齐。
--     inventory.product_id 本来就是 varchar(35)，此改动也消除了同类不同型。
--  4. RBAC 初始数据来自物理机 3306 的现有数据，但【只保留 admin 一个账号】。
--     原库里的 string / test / test2 / test3 / string3 是测试遗留数据，未收录。
--  5. 显式写死 ENGINE 与 CHARSET。原因：docker-compose 里配的服务器默认排序规则是
--     utf8mb4_general_ci，而现有库是 utf8mb4_0900_ai_ci，不显式指定会导致
--     本地库与容器库不一致。
--  6. 保留索引名里的原有拼写 idx_customers_uniqe_id（uniqe 少个 u），
--     以便与现有库中的索引名保持一致，避免重建时出现同名冲突。
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `olist`
    DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE `olist`;


-- ============================================================================
-- 一、Olist 业务数据表（9 张）
--     由 data/scripts/clean_fir.py 从 data/raw/*.csv 清洗后写入
-- ============================================================================

CREATE TABLE IF NOT EXISTS `olist_customers_dataset_clean` (
    `customer_id`              varchar(35) NOT NULL,
    `customer_unique_id`       varchar(35) NOT NULL,
    `customer_zip_code_prefix` varchar(5)  NOT NULL,
    `customer_city`            varchar(40) NOT NULL,
    `customer_state`           varchar(2)  NOT NULL,
    PRIMARY KEY (`customer_id`),
    KEY `idx_customers_uniqe_id` (`customer_unique_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `olist_geolocation_dataset_clean` (
    `geolocation_zip_code_prefix` varchar(5)  NOT NULL,
    `geolocation_lat`             double     NOT NULL,
    `geolocation_lng`             double     NOT NULL,
    `geolocation_city`            varchar(50) NOT NULL,
    `geolocation_state`           varchar(2)  NOT NULL,
    PRIMARY KEY (`geolocation_zip_code_prefix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `olist_order_items_dataset_clean` (
    `order_id`           varchar(35)   NOT NULL,
    `order_item_id`      int           NOT NULL,
    `product_id`         varchar(35)   NOT NULL,
    `seller_id`          varchar(35)   NOT NULL,
    `shipping_limit_date` datetime     NOT NULL,
    `price`              decimal(12,2) NOT NULL,
    `freight_value`      decimal(12,2) NOT NULL,
    PRIMARY KEY (`order_id`, `order_item_id`),
    KEY `idx_product_id` (`product_id`),
    KEY `idx_seller_id` (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `olist_order_payments_dataset_clean` (
    `order_id`             varchar(35)   NOT NULL,
    `payment_sequential`   int           NOT NULL,
    `payment_type`         varchar(15)   NOT NULL,
    `payment_installments` int           NOT NULL,
    `payment_value`        decimal(12,2) NOT NULL,
    PRIMARY KEY (`order_id`, `payment_sequential`),
    KEY `idx_payment_type` (`payment_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `olist_order_reviews_dataset_clean` (
    `review_id`              varchar(35)  NOT NULL,
    `order_id`               varchar(35)  NOT NULL,
    `review_score`           int          NOT NULL,
    `review_comment_title`   varchar(50)  DEFAULT NULL,
    `review_comment_message` varchar(500) DEFAULT NULL,
    `review_creation_date`   datetime     DEFAULT NULL,
    `review_answer_timestamp` datetime    DEFAULT NULL,
    PRIMARY KEY (`review_id`),
    KEY `idx_order_id` (`order_id`),
    KEY `idx_review` (`review_score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `olist_orders_dataset_clean` (
    `order_id`                      varchar(35) NOT NULL,
    `customer_id`                   varchar(35) NOT NULL,
    `order_status`                  varchar(15) NOT NULL,
    `order_purchase_timestamp`      datetime    DEFAULT NULL,
    `order_approved_at`             datetime    DEFAULT NULL,
    `order_delivered_carrier_date`  datetime    DEFAULT NULL,
    `order_delivered_customer_date` datetime    DEFAULT NULL,
    `order_estimated_delivery_date` datetime    DEFAULT NULL,
    PRIMARY KEY (`order_id`),
    KEY `idx_customers_id` (`customer_id`),
    KEY `idx_purchase_timestamp` (`order_purchase_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `olist_products_dataset_clean` (
    `product_id`                 varchar(35) NOT NULL,
    `product_category_name`      varchar(50) NOT NULL,
    `product_name_length`        int         DEFAULT NULL,
    `product_description_length` int         DEFAULT NULL,
    `product_photos_qty`         tinyint     DEFAULT NULL,
    `product_weight_g`           int         DEFAULT NULL,
    `product_length_cm`          int         DEFAULT NULL,
    `product_height_cm`          int         DEFAULT NULL,
    `product_width_cm`           int         DEFAULT NULL,
    PRIMARY KEY (`product_id`),
    KEY `idx_product_category_name` (`product_category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `olist_sellers_dataset_clean` (
    `seller_id`              varchar(35) NOT NULL,
    `seller_zip_code_prefix` varchar(5)  NOT NULL,
    `seller_city`            varchar(50) NOT NULL,
    `seller_state`           varchar(2)  NOT NULL,
    PRIMARY KEY (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `product_category_name_translation_clean` (
    `product_category_name`         varchar(50) NOT NULL,
    `product_category_name_english` varchar(50) NOT NULL,
    PRIMARY KEY (`product_category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ============================================================================
-- 二、RBAC 权限体系（5 张）
--     用户 → 角色 → 权限 两级多对多，鉴权见 app/repositories/permission.py
-- ============================================================================

CREATE TABLE IF NOT EXISTS `system_user` (
    `id`            int          NOT NULL AUTO_INCREMENT,
    `username`      varchar(50)  NOT NULL,
    `password_hash` varchar(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `system_role` (
    `id`          int          NOT NULL AUTO_INCREMENT,
    `name`        varchar(50)  NOT NULL,
    `description` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `system_permission` (
    `id`          int          NOT NULL AUTO_INCREMENT,
    `name`        varchar(100) NOT NULL,
    `description` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `system_role_permission` (
    `id`            int NOT NULL AUTO_INCREMENT,
    `role_id`       int NOT NULL,
    `permission_id` int NOT NULL,
    PRIMARY KEY (`id`),
    KEY `role_id` (`role_id`),
    KEY `permission_id` (`permission_id`),
    CONSTRAINT `system_role_permission_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `system_role` (`id`),
    CONSTRAINT `system_role_permission_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `system_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `system_user_role` (
    `id`      int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `role_id` int NOT NULL,
    PRIMARY KEY (`id`),
    KEY `user_id` (`user_id`),
    KEY `role_id` (`role_id`),
    CONSTRAINT `system_user_role_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `system_user` (`id`),
    CONSTRAINT `system_user_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `system_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ============================================================================
-- 三、库存（2 张）
--     inventory 由 backend/seed_inventory.py 初始化；inventory_log 记录每次调整流水
-- ============================================================================

CREATE TABLE IF NOT EXISTS `inventory` (
    `product_id`   varchar(35) NOT NULL,
    `quantity`     int         NOT NULL,
    `safety_stock` int         NOT NULL,
    PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `inventory_log` (
    `id`         int          NOT NULL AUTO_INCREMENT,
    `product_id` varchar(35)  NOT NULL,
    `change`     int          NOT NULL,
    `before`     int          NOT NULL,
    `after`      int          NOT NULL,
    `reason`     varchar(100) DEFAULT NULL,
    `operator`   varchar(50)  DEFAULT NULL,
    `created_at` datetime     DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ============================================================================
-- 四、操作日志与 AI 问答（2 张）
-- ============================================================================

CREATE TABLE IF NOT EXISTS `operation_log` (
    `id`         int          NOT NULL AUTO_INCREMENT,
    `operator`   varchar(50)  NOT NULL,
    `action`     varchar(50)  NOT NULL,
    `target`     varchar(100) DEFAULT NULL,
    `detail`     varchar(500) DEFAULT NULL,
    `created_at` datetime     DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `ai_analysis` (
    `id`           int         NOT NULL AUTO_INCREMENT,
    `user_id`      varchar(50) DEFAULT NULL,
    `question`     text        NOT NULL,
    `tool_context` text,
    `answer`       text        NOT NULL,
    `created_at`   datetime    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- ============================================================================
-- 五、RBAC 初始数据
--     顺序不能变：先角色/权限，再关联表，最后用户与其角色
-- ============================================================================

INSERT IGNORE INTO `system_role` (`id`, `name`, `description`) VALUES
    (1, 'admin',     '系统管理员'),
    (2, 'operator',  '运营人员'),
    (3, 'warehouse', '仓库人员');

INSERT IGNORE INTO `system_permission` (`id`, `name`, `description`) VALUES
    (1,  'user:read',        '查看用户'),
    (2,  'user:create',      '创建用户'),
    (3,  'user:update',      '修改用户'),
    (4,  'order:read',       '查看订单'),
    (5,  'product:read',     '查看商品'),
    (6,  'customer:read',    '查看客户'),
    (7,  'seller:read',      '查看卖家'),
    (8,  'inventory:read',   '查看库存'),
    (9,  'inventory:adjust', '调整库存'),
    (10, 'dashboard:read',   '查看数据看板'),
    (11, 'logistics:read',   '查看物流数据'),
    (12, 'ai:chat',          'AI运营助手');

-- admin：全部 12 项
-- operator：订单/商品/客户/卖家/看板/物流 + AI（不含用户管理与库存调整）
-- warehouse：商品 + 库存查看/调整 + AI
INSERT IGNORE INTO `system_role_permission` (`id`, `role_id`, `permission_id`) VALUES
    (1,  1, 1),  (2,  1, 2),  (3,  1, 3),  (4,  1, 4),
    (5,  1, 5),  (6,  1, 6),  (7,  1, 7),  (8,  1, 8),
    (9,  1, 9),  (10, 1, 10), (11, 1, 11), (12, 1, 12),
    (13, 2, 4),  (14, 2, 5),  (15, 2, 6),  (16, 2, 7),
    (17, 2, 10), (18, 2, 11), (19, 2, 12),
    (20, 3, 5),  (21, 3, 8),  (22, 3, 9),  (23, 3, 12);

-- 唯一初始账号；密码见文件头说明，登录后请立即修改
INSERT IGNORE INTO `system_user` (`id`, `username`, `password_hash`) VALUES
    (1, 'admin', '$argon2id$v=19$m=65536,t=3,p=4$XJuxyIiAmAHMKYjHM7a0XQ$KdAo6BlH5YuFbcP1W0iSyAZTztY9FQriRvHIgJOuAFc');

INSERT IGNORE INTO `system_user_role` (`id`, `user_id`, `role_id`) VALUES
    (1, 1, 1);


-- ============================================================================
-- 六、自检：执行完应看到 3 个角色 / 12 个权限 / 23 条角色权限 / 1 个用户
-- ============================================================================

SELECT 'database_create.sql 执行完毕' AS msg;
SELECT (SELECT COUNT(*) FROM `system_role`)            AS roles,
       (SELECT COUNT(*) FROM `system_permission`)      AS permissions,
       (SELECT COUNT(*) FROM `system_role_permission`) AS role_perms,
       (SELECT COUNT(*) FROM `system_user`)            AS users;
