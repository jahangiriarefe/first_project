import mysql.connector
import os

config = {'user': os.environ.get('DATABASE_USER'), 'password': os.environ.get('DATABASE_PASSWORD'), 'host': os.environ.get('DATABASE_HOST')}
database = os.environ.get('DATABASE_NAME')


def get_categories():
    conn = mysql.connector.connect(**config, database=database)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT(category) FROM product;")
    data = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return data

def get_products_by_cat(category='%'):
    conn = mysql.connector.connect(**config, database=database)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM product WHERE category LIKE %s", (category,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_products_by_id(product_id):
    conn = mysql.connector.connect(**config, database=database)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM product WHERE id=%s", (product_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data



if __name__ == "__main__":
    # print(get_categories())
    # print(get_products_by_cat())
    print(get_products_by_id(1))