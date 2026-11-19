import csv
import sqlite3

conn = sqlite3.connect("cleanorders.db3")
cur = conn.cursor()
conn.executescript("""
    DELETE FROM customers;
    DELETE FROM managers;
    DELETE FROM products;
    DELETE FROM orders;
    DELETE FROM statuses;
    DELETE FROM product_categories;
    DELETE FROM order_products;
    DELETE FROM sqlite_sequence;
""")

customer_statuses = ["Bronze", "Silver", "Gold", "Platinum"]
for i in range(4):
    cur.execute(f"INSERT INTO statuses(title, discount) VALUES ('{customer_statuses[i]}', {i*5})")
with open('dirtyorders.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        categories = row['product_categories'].split(', ')
        products = row['products_ordered'].split(', ')
        prices = row['product_prices'].split(', ')
        for i in range(len(categories)):
            cur.execute(f"SELECT ID FROM product_categories WHERE title = ('{categories[i]}')")
            cat_ID = cur.fetchone()
            if not cat_ID:
                cur.execute(f"INSERT INTO product_categories (title) VALUES ('{categories[i]}')")
                cur.execute(f"SELECT ID FROM product_categories WHERE title = ('{categories[i]}')")
                cat_ID = cur.fetchone()
            cat_ID = cat_ID[0]
            
            cur.execute(f"SELECT ID FROM products WHERE title = ('{products[i]}')")
            product_ID = cur.fetchone()
            if not product_ID:
                cur.execute(f"INSERT INTO products (title, price, category_ID) VALUES ('{products[i]}', {prices[i]}, {cat_ID})")
                cur.execute(f"SELECT ID FROM products WHERE title = ('{products[i]}')")
                product_ID = cur.fetchone()
            product_ID = product_ID[0]
            cur.execute(f"INSERT INTO order_products (order_ID, product_ID) VALUES ({row['order_id']}, {product_ID})")
        cur.execute(f"SELECT ID FROM managers WHERE manager_ID = '{row['manager_id']}'")
        if not cur.fetchone():
            cur.execute(f"INSERT INTO managers (name, manager_ID) VALUES ('{row['manager_name']}', '{row['manager_id']}')")
        cur.execute(f"SELECT ID FROM customers WHERE email = '{row['customer_email']}'")
        if not cur.fetchone():
            cur.execute(f"SELECT ID FROM statuses WHERE title = '{row['customer_status']}'")
            status_ID = cur.fetchone()[0]
            cur.execute(f"INSERT INTO customers (email, name, phone, status_ID) VALUES ('{row['customer_email']}', '{row['customer_name']}', '{row['customer_phone']}', {status_ID})")
        cur.execute(f"SELECT ID FROM customers WHERE email = '{row['customer_email']}'")
        customer_ID = cur.fetchone()[0]
        cur.execute(f"SELECT ID FROM managers WHERE manager_ID = '{row['manager_id']}'")
        manager_ID = cur.fetchone()[0]
        cur.execute(f"INSERT INTO orders (ID, create_date, customer_ID, manager_ID) VALUES ('{row['order_id']}', '{row['order_date']}', {customer_ID}, {manager_ID})")
conn.commit()
conn.close()
