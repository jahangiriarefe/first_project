import mysql.connector
import os

config = {'user': os.environ.get('DATABASE_USER'), 'password': os.environ.get('DATABASE_PASSWORD'), 'host': os.environ.get('DATABASE_HOST')}
database = os.environ.get('DATABASE_NAME')


def insert_product_data(name, description, category, price, inventory=0, file_id=None):
    conn = mysql.connector.connect(**config, database=database)
    cur = conn.cursor()
    SQL_QUERY = """INSERT INTO product 
                (name, description, category, price, inventory, file_id)
                VALUES (%s, %s, %s, %s, %s, %s);"""
    cur.execute(SQL_QUERY, (name, description, category, price, inventory, file_id))
    product_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    print(f'product inserted with id: {product_id}')
    return product_id  

if __name__ == "__main__":
    insert_product_data('shoe', 'brown', 'shoe', 100, 10) 