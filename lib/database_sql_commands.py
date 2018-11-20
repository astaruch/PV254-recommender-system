CREATE_TABLE_IMAGE_LABEL = '''CREATE TABLE IF NOT EXISTS `image_label` (
    `id` INT PRIMARY KEY,
    `path_prefix` TEXT NOT NULL,
    `filename` TEXT NOT NULL,
    `label` TEXT NOT NULL,
    `score` REAL NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)'''