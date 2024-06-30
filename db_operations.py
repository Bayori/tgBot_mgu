import mysql.connector
from db_config import db_config
from decimal import Decimal

def get_db_connection():
    return mysql.connector.connect(**db_config)

def get_menu():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM t_menu")
    menu = cursor.fetchall()
    cursor.close()
    connection.close()
    return menu

def update_product_count(product_id, count_kg):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE t_products SET count_kg = %s WHERE id_product = %s", (count_kg, product_id))
    connection.commit()
    cursor.close()
    connection.close()

def add_order(client_id, dish_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO t_orders (id_client, id_dish) VALUES (%s, %s)", (client_id, dish_id))
    connection.commit()
    cursor.close()
    connection.close()

def get_orders():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM t_orders")
    orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return orders

def get_clients():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM t_client")
    clients = cursor.fetchall()
    cursor.close()
    connection.close()
    return clients

def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_product, title, count_kg FROM t_products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return products

def get_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM t_products WHERE id_product = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    connection.close()
    return product
