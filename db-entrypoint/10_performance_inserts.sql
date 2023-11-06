CREATE DATABASE IF NOT EXISTS performance_inserts;
USE performance_inserts;

CREATE TABLE IF NOT EXISTS entries (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `description` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP()
)
