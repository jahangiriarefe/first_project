import mysql.connector
import os

config = {'user': os.environ.get('DATABASE_USER'), 'password': os.environ.get('DATABASE_PASSWORD'), 'host': os.environ.get('DATABASE_HOST')}
database = os.environ.get('DATABASE_NAME')

def create_database():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {database};")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {database};")
    conn.commit()
    cur.close()
    conn.close()
    print(f'database {database} created successfully')

def create_table_product():
    conn = mysql.connector.connect(**config, database=database)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE product (
                    `id`                    INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
                    `name`                  VARCHAR(100) NOT NULL,
                    `description`           VARCHAR(200),
                    `category`              ENUM('shoe', 'bag', 'accessory'),
                    `price`                 DECIMAL(10, 2) NOT NULL,
                    `inventory`             MEDIUMINT UNSIGNED NOT NULL DEFAULT 0,
                    `file_id`               VARCHAR(200),
                    `register_date`         DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `last_update`           DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );""")
    conn.commit()
    cur.close()
    conn.close()
    print(f'table products created successfully')


if __name__ == "__main__":
    create_database()
    create_table_product()