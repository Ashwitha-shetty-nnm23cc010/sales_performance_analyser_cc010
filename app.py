from flask import Flask, render_template, request, redirect, session, send_file
import mysql.connector
import csv
import io
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'secretkey'

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if not conn:
            return render_template('login.html', error="Database connection error")
        cursor = conn.cursor()
        # Use %s placeholders for MySQL
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if not conn:
            return "Database connection error", 500
        cursor = conn.cursor()
        try:
            # Use %s placeholders for MySQL
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/login')  # Redirect to login after successful registration
        except mysql.connector.IntegrityError as e:
            cursor.close()
            conn.close()
            return render_template('register.html', error="Username already exists")
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
    cursor = conn.cursor(dictionary=True)  # Use dictionary=True for easier access in templates
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', sales=sales, username=session['username'])
@app.route('/add-sale', methods=['GET', 'POST'])
def add_sale():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        region = request.form['region']
        salesperson = request.form['salesperson']
        sale_date = request.form['sale_date']
        conn = get_db_connection()
        if not conn:
            return "Database connection error", 500
        cursor = conn.cursor()
        # Exclude the 'total' column from the INSERT query
        cursor.execute(
            "INSERT INTO sales (product_name, quantity, price, region, salesperson, sale_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (product_name, quantity, price, region, salesperson, sale_date)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')
    return render_template('add_sale.html')

@app.route('/export')
def export():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    cursor.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Product Name', 'Quantity', 'Price', 'Total', 'Region', 'Salesperson', 'Sale Date'])
    for row in sales:
        writer.writerow(row)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     download_name='sales_data.csv',
                     as_attachment=True)
@app.route('/region-sales')
def region_sales():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
    cursor = conn.cursor(dictionary=True)
    # Query to calculate total sales grouped by region
    cursor.execute("""
        SELECT region, SUM(total) AS total_sales
        FROM sales
        GROUP BY region
    """)
    region_sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('region_sales.html', region_sales=region_sales)

@app.route('/sales-by-salesperson')
def sales_by_salesperson():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
    cursor = conn.cursor(dictionary=True)
    # Query to calculate total sales grouped by salesperson
    cursor.execute("""
        SELECT salesperson, SUM(total) AS total_sales
        FROM sales
        GROUP BY salesperson
    """)
    sales_by_salesperson = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('sales_by_salesperson.html', sales_by_salesperson=sales_by_salesperson)

@app.route('/feedback')
def feedback():
    if 'username' not in session:
        return redirect('/login')
    return render_template('feedback.html')

@app.route('/profit-loss-calculator')
def profit_loss_calculator():
    if 'username' not in session:
        return redirect('/login')
    return render_template('profit_loss_calculator.html')


@app.route('/products', methods=['GET', 'POST'])
def products():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            stock = request.form['stock']

            # Check if the product name already exists
            cursor.execute("SELECT * FROM products WHERE name = %s", (name,))
            existing_product = cursor.fetchone()
            if existing_product:
                return "Error: A product with this name already exists.", 400

            # Insert the new product
            cursor.execute(
                "INSERT INTO products (name, description, price, stock) VALUES (%s, %s, %s, %s)",
                (name, description, price, stock)
            )
            conn.commit()

        # Fetch all products
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
    except Exception as e:
        conn.rollback()
        return f"Database error: {e}", 500
    finally:
        cursor.close()
        conn.close()
    return render_template('products.html', products=products)

@app.route('/regions', methods=['GET', 'POST'])
def regions():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        cursor.execute("INSERT INTO regions (name) VALUES (%s)", (name,))
        conn.commit()
    cursor.execute("SELECT * FROM regions")
    regions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('regions.html', regions=regions)

@app.route('/salespersons', methods=['GET', 'POST'])
def salespersons():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cursor.execute(
            "INSERT INTO salespersons (name, email, phone) VALUES (%s, %s, %s)",
            (name, email, phone)
        )
        conn.commit()
    cursor.execute("SELECT * FROM salespersons")
    salespersons = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('salespersons.html', salespersons=salespersons)

@app.route('/feedback-list', methods=['GET', 'POST'])
def feedback_list():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            username = request.form['username']
            feedback = request.form['feedback']
            # Insert the feedback into the database
            cursor.execute(
                "INSERT INTO feedback (username, feedback) VALUES (%s, %s)",
                (username, feedback)
            )
            conn.commit()
        # Fetch all feedbacks
        cursor.execute("SELECT * FROM feedback")
        feedbacks = cursor.fetchall()
    except Exception as e:
        conn.rollback()
        return f"Database error: {e}", 500
    finally:
        cursor.close()
        conn.close()
    return render_template('feedback_list.html', feedbacks=feedbacks)

@app.route('/profit-loss-history', methods=['GET', 'POST'])
def profit_loss_history():
    if 'username' not in session:
        return redirect('/login')
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cost_price = float(request.form['cost_price'])
        selling_price = float(request.form['selling_price'])
        if selling_price > cost_price:
            profit_loss_amount = selling_price - cost_price
            profit_loss_percentage = (profit_loss_amount / cost_price) * 100
        else:
            profit_loss_amount = cost_price - selling_price
            profit_loss_percentage = (profit_loss_amount / cost_price) * 100
        cursor.execute(
            "INSERT INTO profit_loss (cost_price, selling_price, profit_loss_amount, profit_loss_percentage) VALUES (%s, %s, %s, %s)",
            (cost_price, selling_price, profit_loss_amount, profit_loss_percentage)
        )
        conn.commit()
    cursor.execute("SELECT * FROM profit_loss")
    profit_loss_records = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('profit_loss_history.html', profit_loss_records=profit_loss_records)



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)