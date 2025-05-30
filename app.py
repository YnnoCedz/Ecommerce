from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_mail import Mail,Message
import MySQLdb.cursors,re
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from decimal import Decimal
import os, random, string,requests
from fpdf import FPDF
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# MySQL Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bbb'

# Configure the upload folder for product images
UPLOAD_FOLDER = 'D:/xampp/htdocs/bbb_api/uploads/'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

#Flask mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sampleecommerce05@gmail.com' #email for books_media
app.config['MAIL_PASSWORD'] = 'lflc ygep yakq ftyl' #app password for books_media
app.config['MAIL_DEFAULT_SENDER'] = 'sampleecommerce05@gmail.com'


mail = Mail(app)

# Initialize MySQL and CORS
mysql = MySQL(app)
CORS(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#para pag nag run diretso login page
@app.route('/')
def index():
    return redirect(url_for('login'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



# def get_location_name(code, location_type):
#     # Build the URL based on the location type (province, municipality, barangay)
#     base_url = "https://psgc.gitlab.io/api/"
    
#     if location_type == 'province':
#         url = f"{base_url}provinces/{code}"
#     elif location_type == 'municipality':
#         url = f"{base_url}municipalities/{code}"
#     elif location_type == 'barangay':
#         url = f"{base_url}barangays/{code}"
#     else:
#         return 'Select Location'

#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         data = response.json()

#         # Return the name from the response
#         return data.get('name', 'Unknown Location')
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching location: {e}")
#         return 'Select Location'


def get_location_name(code, location_type):
    base_url = "https://psgc.gitlab.io/api/"
    
    if location_type == 'province':
        url = f"{base_url}provinces/{code}"
    elif location_type == 'municipality':
        url = f"{base_url}municipalities/{code}"
    elif location_type == 'barangay':
        url = f"{base_url}barangays/{code}"
    else:
        return 'Unknown Location'

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('name', 'Unknown Location')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {location_type} name: {e}")
        return 'Unknown Location'

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check in users table
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            hashed_password = generate_password_hash(temp_password, method='pbkdf2:sha256')
            expiry_time = datetime.now() + timedelta(minutes=5)  # Password expires in 5 minutes

            # Update the database with the temp password and expiry
            cur.execute("UPDATE users SET password = %s, password_expiry = %s WHERE email = %s",
                        (hashed_password, expiry_time, email))
            mysql.connection.commit()

            # Send email with temporary password
            msg = Message('Password Reset Request', sender='your-email@example.com', recipients=[email])
            msg.body = f"Hello {user['first_name']},\n\nYour temporary password is: {temp_password}\n" \
                       f"Please log in and change your password immediately. Note that this password will expire in 5 minutes.\n\n" \
                       f"Best regards,\nSupport Team"
            mail.send(msg)

            flash('A temporary password has been sent to your email.', 'info')

        else:
            # Check in sellers table
            cur.execute("SELECT * FROM sellers WHERE email = %s", (email,))
            seller = cur.fetchone()

            if seller:
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                hashed_password = generate_password_hash(temp_password, method='pbkdf2:sha256')
                expiry_time = datetime.now() + timedelta(minutes=5)  # Password expires in 5 minutes

                # Update the database with the temp password and expiry
                cur.execute("UPDATE sellers SET password = %s, password_expiry = %s WHERE email = %s",
                            (hashed_password, expiry_time, email))
                mysql.connection.commit()

                # Send email with temporary password
                msg = Message('Password Reset Request', sender='your-email@example.com', recipients=[email])
                msg.body = f"Hello {seller['first_name']} {seller['last_name']},\n\nYour temporary password is: {temp_password}\n" \
                           f"Please log in and change your password immediately. Note that this password will expire in 5 minutes.\n\n" \
                           f"Best regards,\nSupport Team"
                mail.send(msg)

                flash('A temporary password has been sent to your email.', 'info')
            else:
                # Email not found in both tables
                flash('This email is not registered in our system.', 'danger')

        cur.close()
        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    modal_message = None
    modal_title = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check admin credentials
        cur.execute("SELECT * FROM admin WHERE email = %s", (email,))
        admin = cur.fetchone()
        if admin:
            if check_password_hash(admin['password'], password):
                session['admin_id'] = admin['admin_id']
                session['email'] = admin['email']
                session['role'] = admin['role']
                cur.close()
                return redirect(url_for('admin_homepage'))
            else:
                modal_title = "Login Error"
                modal_message = "Invalid email or password."
        else:
            # Check user credentials
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                if user['approved'] == 0:
                    if user.get('rejected') == 1:
                        modal_title = "Application Rejected"
                        modal_message = "Your application has been rejected. Contact us for more information."
                    else:
                        modal_title = "Account Under Review"
                        modal_message = "Your account is under review for approval."
                elif user['archived'] == 1:
                    modal_title = "Account Suspended"
                    modal_message = "Your account has been banned or temporarily suspended. Please contact us for more information."
                elif check_password_hash(user['password'], password):
                    session['user_id'] = user['user_id']
                    session['email'] = user['email']
                    session['role'] = 'buyer'
                    cur.close()
                    return redirect(url_for('homepage'))
                else:
                    modal_title = "Login Error"
                    modal_message = "Invalid email or password."
            else:
                # Check seller credentials
                cur.execute("SELECT * FROM sellers WHERE email = %s", (email,))
                seller = cur.fetchone()
                if seller:
                    if seller['approved'] == 0:
                        if seller['archived'] == 1:
                            modal_title = "Account Suspended"
                            modal_message = "Your account has been banned or temporarily suspended. Please contact us for more information."
                        else:
                            modal_title = "Account Under Review"
                            modal_message = "Your account is under review for approval."
                    elif seller.get('rejected') == 1:
                        modal_title = "Application Rejected"
                        modal_message = "Your application has been rejected. Contact us for more information."
                    elif check_password_hash(seller['password'], password):
                        session['seller_id'] = seller['seller_id']
                        session['email'] = seller['email']
                        session['role'] = 'seller'
                        cur.close()
                        return redirect(url_for('seller_homepage'))
                    else:
                        modal_title = "Login Error"
                        modal_message = "Invalid email or password."
                else:
                    # Check courier credentials
                    cur.execute("SELECT * FROM courier WHERE email = %s", (email,))
                    courier = cur.fetchone()
                    if courier:
                        if courier['approved'] == 0:
                            if courier.get('rejected') == 1:
                                modal_title = "Application Rejected"
                                modal_message = "Your application has been rejected. Contact us for more information."
                            else:
                                modal_title = "Account Under Review"
                                modal_message = "Your account is under review for approval."
                        elif courier['archived'] == 1:
                            modal_title = "Account Suspended"
                            modal_message = "Your account has been banned or temporarily suspended. Please contact us for more information."
                        elif check_password_hash(courier['password'], password):
                            session['courier_id'] = courier['id']
                            session['email'] = courier['email']
                            session['role'] = 'courier'
                            cur.close()
                            return redirect(url_for('courier_homepage'))
                        else:
                            modal_title = "Login Error"
                            modal_message = "Invalid email or password."
                    else:
                        modal_title = "Login Error"
                        modal_message = "Invalid email or password."

        cur.close()

    return render_template('login.html', modal_message=modal_message, modal_title=modal_title)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
#==================================================== ADMIN  for USERS/BUYERS===============================================================================
# @app.route('/register-admin', methods=['GET', 'POST'])
# def admin_registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'  # Set the role as 'admin' for this route

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new admin into the database
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("INSERT INTO admin (email, password, role) VALUES (%s, %s, %s)", 
                        (email, hashed_password, role))
            mysql.connection.commit()
            cur.close()

            flash('Admin registered successfully!', 'success')
            return redirect(url_for('login'))
        
        except MySQLdb.Error as e:
            flash('Error: Could not register admin. Please try again.', 'danger')
            print(f"Error: {e}")
        
    return render_template('admin_registration.html')

@app.route('/admin')
def admin_homepage():
    if 'admin_id' in session and session['role'] == 'admin':
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Dashboard Metrics
            cur.execute("SELECT COUNT(*) AS total_users FROM users")
            total_users = cur.fetchone()['total_users']

            cur.execute("SELECT COUNT(*) AS total_sellers FROM sellers")
            total_sellers = cur.fetchone()['total_sellers']

            cur.execute("SELECT COUNT(*) AS total_products FROM products")
            total_products = cur.fetchone()['total_products']

            cur.execute("SELECT SUM(commission) AS total_commission FROM orders")
            total_commission = cur.fetchone()['total_commission'] or 0

            cur.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM users WHERE approved = 0 AND rejected = 0) +
                    (SELECT COUNT(*) FROM sellers WHERE approved = 0 AND rejected = 0) AS total_pending
            """)
            total_pending = cur.fetchone()['total_pending']

            cur.execute("SELECT COUNT(*) AS orders_cancelled_count FROM orders WHERE order_status = 'cancelled'")
            orders_cancelled_count = cur.fetchone()['orders_cancelled_count'] or 0

            cur.execute("""
                SELECT SUM(commission) AS daily_commission 
                FROM orders 
                WHERE DATE(created_at) = CURDATE()
            """)
            daily_commission = cur.fetchone()['daily_commission'] or 0

            cur.execute("""
                SELECT 
                    s.store_name,
                    s.seller_image,
                    COUNT(o.product_id) AS products_sold,
                    SUM(o.total_price) AS total_sales,
                    SUM(o.commission) AS total_commission
                FROM sellers s
                LEFT JOIN orders o ON s.seller_id = o.seller_id
                WHERE o.order_status = 'completed'
                GROUP BY s.seller_id
                ORDER BY total_sales DESC
                LIMIT 5
            """)
            top_sellers = cur.fetchall()

            # Unread Chat Notifications
            cur.execute("""
                SELECT
                    c.sender_id,
                    CASE
                        WHEN c.sender_role = 'seller' THEN s.email
                        WHEN c.sender_role = 'user' THEN u.email
                    END AS sender_email,
                    'New message' AS message,
                    c.timestamp AS latest_message_time
                FROM
                    chats c
                LEFT JOIN
                    sellers s ON c.sender_id = s.seller_id AND c.sender_role = 'seller'
                LEFT JOIN
                    users u ON c.sender_id = u.user_id AND c.sender_role = 'user'
                WHERE
                    c.is_read = 0 AND c.sender_role = 'user' OR c.sender_role = 'seller'
                ORDER BY 
                    c.timestamp DESC
            """)
            unread_chat_notifications = cur.fetchall()

            cur.close()

            # Pass all data to the template
            return render_template(
                'admin.html',
                total_users=total_users,
                total_sellers=total_sellers,
                total_products=total_products,
                total_commission=total_commission,
                total_pending=total_pending,
                orders_cancelled_count=orders_cancelled_count,
                daily_commission=daily_commission,
                top_sellers=top_sellers,
                unread_chat_notifications=unread_chat_notifications
            )

        except MySQLdb.Error as e:
            flash('Database error: Could not load admin dashboard data', 'danger')
            print(f"Error: {e}")
            return redirect(url_for('login'))

    else:
        flash('Please log in to access the admin page', 'warning')
        return redirect(url_for('login'))


@app.route('/admin_users')
def admin_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, first_name, last_name, email, role, archived FROM users WHERE approved = 1")
    users = cur.fetchall()
    cur.close()

    # Transforming the result into a list of dictionaries for easier access in the template
    user_list = [
        {
            'id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'role': user[4],
            'archived': user[5]
        }
        for user in users
    ]
    return render_template('admin_user_management.html', users=user_list)

# Define route to view user profile
@app.route('/view_user/<int:user_id>')
def view_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT first_name, last_name, email, phone_number, street, barangay, city, province, zip_code,role, profile_image_url, user_id_path,role
        FROM users
        WHERE user_id = %s
    """, (user_id,))
    result = cur.fetchone()
    
    if result:
        user = {
            'first_name': result[0],
            'last_name': result[1],
            'email': result[2],
            'phone_number': result[3],
            'street': result[4],
            'barangay': result[5],
            'city': result[6],
            'province': result[7],
            'zip_code': result[8],
            'role': result[9],
            'profile_image_url': result[10],
            'user_id_path': result[11] 
        }
    else:
        user = None

    cur.close()
    return render_template('admin_view_user.html', user=user)




@app.route('/archive_user/<int:user_id>', methods=['POST'])
def archive_user(user_id):
    # Update the archived status of the user to TRUE
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET archived = TRUE WHERE user_id = %s", (user_id,))
    mysql.connection.commit()  # Commit the changes
    cur.close()

    # Optionally, flash a success message or redirect back to the admin user management page
    flash('User has been archived successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/toggle_archive/<int:user_id>', methods=['POST'])
def toggle_archive(user_id):
    action = request.args.get('action')
    archive_status = 1 if action == 'archive' else 0
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET archived = %s WHERE user_id = %s", (archive_status, user_id))
    mysql.connection.commit()
    cur.close()

    message = 'User has been archived successfully!' if archive_status == 1 else 'User has been retrieved successfully!'
    flash(message, 'success')
    return redirect(url_for('admin_users'))

#================================================ ADMIN FOR SELLERS =======================================================================

# Route to display all sellers
@app.route('/admin_sellers')
def admin_sellers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT seller_id, first_name, last_name, email, role, archived FROM sellers")
    sellers = cur.fetchall()
    cur.close()

    # Convert result into a list of dictionaries for easy access in the template
    seller_list = [
        {
            'id': seller[0],
            'first_name': seller[1],
            'last_name': seller[2],
            'email': seller[3],
            'role': seller[4],
            'archived': seller[5]
        }
        for seller in sellers
    ]
    return render_template('admin_seller_management.html', sellers=seller_list)

@app.route('/view_seller/<int:seller_id>')
def view_seller(seller_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM sellers WHERE seller_id = %s', (seller_id,))
    seller = cursor.fetchone()

    if seller:
        return render_template('admin_view_seller.html', seller=seller)
    else:
        flash('Seller not found!', 'error')
        return redirect(url_for('admin'))

# Route to chat with the seller (Placeholder)
@app.route('/chat_seller/<int:seller_id>')
def chat_seller(seller_id):
    # Implement chat functionality or redirect to chat page here
    return f"Chatting with seller {seller_id}"

@app.route('/archive_seller/<int:seller_id>', methods=['POST'])
def archive_seller(seller_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE sellers SET archived = TRUE WHERE seller_id = %s", (seller_id,))
    mysql.connection.commit()  # Commit the changes
    cur.close()

    flash('Seller has been archived successfully!', 'success')
    return redirect(url_for('admin_sellers'))

# Route to toggle archived status for a seller
@app.route('/toggle_archived/<int:seller_id>', methods=['POST'])
def toggle_archived(seller_id):
    action = request.args.get('action')
    archive_status = 1 if action == 'archive' else 0
    cur = mysql.connection.cursor()
    cur.execute("UPDATE sellers SET archived = %s WHERE seller_id = %s", (archive_status, seller_id))
    mysql.connection.commit()
    cur.close()

    message = 'Seller has been archived successfully!' if archive_status == 1 else 'Seller has been retrieved successfully!'
    flash(message, 'success')
    return redirect(url_for('admin_sellers'))


#-============================================= ADMIN FOR COURIERS =============================================================
@app.route('/admin_couriers')
def admin_courier():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, first_name, last_name, email, role, archived FROM courier")
    sellers = cur.fetchall()
    cur.close()

    # Convert result into a list of dictionaries for easy access in the template
    seller_list = [
        {
            'id': seller[0],
            'first_name': seller[1],
            'last_name': seller[2],
            'email': seller[3],
            'role': seller[4],
            'archived': seller[5]
        }
        for seller in sellers
    ]
    return render_template('admin_courier_management.html', sellers=seller_list)



@app.route('/view_courier_applicants', methods=['GET'])
def view_courier_applicants():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, first_name, last_name, email, role FROM courier WHERE approved = 0 AND rejected = 0")
    sellers = cur.fetchall()
    cur.close()
    courier_list = [
        {
            'id': seller[0],
            'first_name': seller[1],
            'last_name': seller[2],
            'email': seller[3],
            'role': seller[4],
        }
        for seller in sellers
    ]
    return render_template('admin_courier_applicants.html', couriers=courier_list)


@app.route('/view_courier/<int:courier_id>', methods=['GET'])
def view_courier(courier_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM courier WHERE id = %s', (courier_id,))
    courier = cursor.fetchone()

    if courier:
        return render_template('admin_view_courier.html', courier=courier)
    else:
        flash('Courier not found!', 'error')
        return redirect(url_for('admin'))
    


# ====================================================== ADMIN for Registration/Application Approval ====================================================== 
@app.route('/view_user_applicants', methods=['GET'])
def view_user_applicants():
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id, first_name, last_name, email, role FROM users WHERE approved = 0 AND rejected = 0")
    users = cur.fetchall()
    cur.close()
    user_list = [
        {
            'id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'role': user[4],
        }
        for user in users
    ]
    return render_template('admin_user_applicants.html', users=user_list)

@app.route('/view_seller_applicants', methods=['GET'])
def view_seller_applicants():
    cur = mysql.connection.cursor()
    cur.execute("SELECT seller_id, first_name, last_name, email, role FROM sellers WHERE approved = 0 AND rejected = 0")
    sellers = cur.fetchall()
    cur.close()
    seller_list = [
        {
            'id': seller[0],
            'first_name': seller[1],
            'last_name': seller[2],
            'email': seller[3],
            'role': seller[4],
        }
        for seller in sellers
    ]
    return render_template('admin_seller_applicants.html', sellers=seller_list)



@app.route('/update_status', methods=['POST'])
def update_status():
    user_id = request.form.get('user_id')
    approved = request.form.get('approved')

    # Debugging logs
    app.logger.debug(f"Received user_id: {user_id}, approved: {approved}")

    # Validate inputs
    if not user_id or not user_id.isdigit() or approved not in ['0', '1']:
        flash("Invalid data provided. Please check your input.", "danger")
        app.logger.error("Invalid input data received.")
        return redirect(url_for('view_user_applicants'))

    try:
        # Open a database cursor
        cur = mysql.connection.cursor()

        # Get the email of the user if they are being approved
        if approved == '1':
            app.logger.info(f"Approving user with ID {user_id}")
            cur.execute(
                "SELECT email FROM users WHERE user_id = %s",
                (user_id,)
            )
            user = cur.fetchone()
            
            if user:
                recipient_email = user[0]  # Access email from tuple (index 0)
                message_content = "Your account has been approved for Books,Bytes and Blockbusters. Consume Entertainment to the fullest!"

                # Send the approval email
                msg = Message(
                    subject="Account Approved",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email]
                )
                msg.body = message_content
                mail.send(msg)
                app.logger.info(f"Approval email sent to {recipient_email}")
            
            # Update the user's status to approved
            cur.execute(
                "UPDATE users SET approved = 1, archived = 0 WHERE user_id = %s",
                (user_id,)
            )
        elif approved == '0':  # Reject the user
            app.logger.info(f"Rejecting user with ID {user_id}")
            cur.execute(
                "SELECT email FROM users WHERE user_id = %s",
                (user_id,)
            )
            user = cur.fetchone()
            
            if user:
                recipient_email = user[0]  # Access email from tuple (index 0)
                message_content = "We regret to inform you that your application for Books, Bytes, and Blockbusters was not approved. Thank you for your interest. Contact us for more information."

                # Send the approval email
                msg = Message(
                    subject="Application Rejected",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email]
                )
                msg.body = message_content
                mail.send(msg)
                app.logger.info(f"Approval email sent to {recipient_email}")
            
            # Update the user's status to approved
            cur.execute(
                "UPDATE users SET approved = 0, archived = 1, rejected = 1 WHERE user_id = %s",
                (user_id,)  
            )

        # Commit changes
        mysql.connection.commit()
        flash("User status updated successfully!", "success")
    except Exception as e:
        # Rollback on error
        mysql.connection.rollback()
        flash(f"An error occurred while updating user status: {e}", "danger")
        app.logger.error(f"Error updating user status: {e}")
    finally:
        # Close the cursor
        cur.close()

    return redirect(url_for('view_user_applicants'))

@app.route('/update_seller_status', methods=['POST'])
def update_seller_status():
    if 'admin_id' not in session:  # Ensure only logged-in admins can update
        flash("You must be logged in to perform this action.", "danger")
        return redirect(url_for('login'))

    seller_id = request.form.get('seller_id')
    approved = request.form.get('approved')

    # Debugging logs
    app.logger.debug(f"Received seller_id: {seller_id}, approved: {approved}")

    # Validate inputs
    if not seller_id or not seller_id.isdigit() or approved not in ['0', '1']:
        flash("Invalid data provided. Please check your input.", "danger")
        app.logger.error("Invalid input data received.")
        return redirect(url_for('view_seller_applicants'))

    try:
        cur = mysql.connection.cursor()

        if approved == '1':  # Approve the seller
            app.logger.info(f"Approving seller with ID {seller_id}")
            cur.execute("SELECT email FROM sellers WHERE seller_id = %s", (seller_id,))
            seller = cur.fetchone()

            if seller:
                recipient_email = seller[0]
                message_content = "Your account has been approved for Books, Bytes, and Blockbusters!"

                # Send the approval email
                msg = Message(
                    subject="Account Approved",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email]
                )
                msg.body = message_content
                mail.send(msg)
                app.logger.info(f"Approval email sent to {recipient_email}")

            cur.execute("UPDATE sellers SET approved = 1, archived = 0 WHERE seller_id = %s", (seller_id,))
        elif approved == '0':  # Reject the seller
            app.logger.info(f"Rejecting seller with ID {seller_id}")
            cur.execute("SELECT email FROM sellers WHERE seller_id = %s", (seller_id,))
            seller = cur.fetchone()

            if seller:
                recipient_email = seller[0]
                message_content = "We regret to inform you that your application was not approved. Thank you for your interest."

                # Send the rejection email
                msg = Message(
                    subject="Application Rejected",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email]
                )
                msg.body = message_content
                mail.send(msg)
                app.logger.info(f"Rejection email sent to {recipient_email}")

            cur.execute("UPDATE sellers SET approved = 0, archived = 1, rejected = 1 WHERE seller_id = %s", (seller_id,))

        mysql.connection.commit()
        flash("Seller status updated successfully!", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"An error occurred: {e}", "danger")
        app.logger.error(f"Error: {e}")

    finally:
        cur.close()

    return redirect(url_for('view_seller_applicants'))



#courier
@app.route('/update_courier_status', methods=['POST'])
def update_courier_status():
    courier_id = request.form.get('courier_id')
    approved = request.form.get('approved')

    # Debugging logs
    app.logger.debug(f"Received courier_id: {courier_id}, approved: {approved}")

    # Validate inputs
    if not courier_id or not courier_id.isdigit() or approved not in ['0', '1']:
        flash("Invalid data provided. Please check your input.", "danger")
        app.logger.error("Invalid input data received.")
        return redirect(url_for('view_courier_applicants'))

    try:
        # Open a database cursor
        cur = mysql.connection.cursor()

        if approved == '1':
            app.logger.info(f"Approving courier with ID {courier_id}")
            cur.execute(
                "SELECT email FROM courier WHERE id = %s",
                (courier_id,)
            )
            courier = cur.fetchone()
            
            if courier:
                recipient_email = courier[0]  # Access email from tuple (index 0)
                message_content = "Your account has been approved for Books, Bytes and Blockbusters. Enjoy your deliveries!"
                # Send the approval email
                msg = Message(
                    subject="Account Approved",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email]
                )
                msg.body = message_content
                mail.send(msg)
                app.logger.info(f"Approval email sent to {recipient_email}")
            
            # Update the courier's status to approved
            cur.execute(
                "UPDATE courier SET approved = 1, archived = 0 WHERE id = %s",
                (courier_id,)
            )
        elif approved == '0':
            app.logger.info(f"Rejecting courier with ID {courier_id}")
            cur.execute(
                "SELECT email FROM courier WHERE id = %s",
                (courier_id,)
            )
            courier = cur.fetchone()
            
            if courier:
                recipient_email = courier[0]
                message_content = "We regret to inform you that your application for Books, Bytes, and Blockbusters was not approved. Thank you for your interest. Contact us for more information."
                msg = Message(
                    subject="Application Rejected",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email]
                )
                msg.body = message_content
                mail.send(msg)
                app.logger.info(f"Rejection email sent to {recipient_email}")
            
            # Update the courier's status to rejected
            cur.execute(
                "UPDATE courier SET approved = 0, archived = 1, rejected = 1 WHERE id = %s",
                (courier_id,)  
            )

        mysql.connection.commit()
        flash("Courier status updated successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"An error occurred while updating courier status: {e}", "danger")
        app.logger.error(f"Error updating courier status: {e}")
    finally:
        cur.close()

    return redirect(url_for('view_courier_applicants'))


@app.route('/view_rejected_applicants', methods=['GET'])
def view_rejected_applicants():
    try:
        cur = mysql.connection.cursor()
        
        # Query for rejected users
        cur.execute("SELECT user_id, first_name, last_name, email, role FROM users WHERE rejected = 1")
        users = cur.fetchall()

        # Query for rejected sellers
        cur.execute("SELECT seller_id, first_name, last_name, email, role FROM sellers WHERE rejected = 1")
        sellers = cur.fetchall()

        cur.close()

        # Combine users and sellers into a single list
        applicants = [
            {
                'id': user[0],
                'first_name': user[1],
                'last_name': user[2],
                'email': user[3],
                'role': user[4],
                'type': 'User'  # Add a type to distinguish between users and sellers
            }
            for user in users
        ] + [
            {
                'id': seller[0],
                'first_name': seller[1],
                'last_name': seller[2],
                'email': seller[3],
                'role': seller[4],
                'type': 'Seller'  # Add a type for sellers
            }
            for seller in sellers
        ]

        # Sort applicants by name or any other criteria if needed
        applicants.sort(key=lambda x: x['first_name'])

        return render_template('admin_rejected_applicants.html', applicants=applicants)

    except Exception as e:
        app.logger.error(f"Error fetching rejected applicants: {e}")
        flash("An error occurred while fetching rejected applicants.", "danger")
        return redirect(url_for('admin'))

@app.route('/restore_rejected_applicant', methods=['POST'])
def restore_rejected_applicant():
    applicant_id = request.form.get('id')
    applicant_type = request.form.get('type')  # Either "User" or "Seller"
    
    # Logging for debugging
    app.logger.debug(f"Restore request for {applicant_type} with ID: {applicant_id}")
    
    if not applicant_id or not applicant_id.isdigit():
        flash("Invalid applicant ID provided.", "danger")
        return redirect(url_for('view_rejected_applicants'))
    
    try:
        cur = mysql.connection.cursor()
        
        if applicant_type == "User":
            app.logger.info(f"Restoring user with ID: {applicant_id}")
            cur.execute("UPDATE users SET rejected = 0 WHERE user_id = %s", (applicant_id,))
        elif applicant_type == "Seller":
            app.logger.info(f"Restoring seller with ID: {applicant_id}")
            cur.execute("UPDATE sellers SET rejected = 0 WHERE seller_id = %s", (applicant_id,))
        else:
            flash("Invalid applicant type provided.", "danger")
            return redirect(url_for('view_rejected_applicants'))
        
        # Commit changes
        mysql.connection.commit()
        flash("Applicant restored successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"An error occurred while restoring the applicant: {e}", "danger")
        app.logger.error(f"Error restoring applicant: {e}")
    finally:
        cur.close()
    
    return redirect(url_for('view_rejected_applicants'))

#====================================================REGISTRATION ========================================================================
@app.route('/select-role', methods=['GET', 'POST'])
def select_role():
    if request.method == 'POST':
        role = request.form.get('role')
        
        # Redirect based on the selected role   
        if role == 'buyer':
            return redirect(url_for('register'))
        elif role == 'seller':
            return redirect(url_for('seller_application'))
        elif role == 'courier':
            return redirect(url_for('courier_registration'))

    return render_template('register-choice.html')


# @app.route('/register', methods=['GET', 'POST'])
# def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        phone_number = request.form['phone_number']
        province = request.form['province']
        city = request.form['city']
        barangay = request.form['barangay']
        street = request.form['street']
        zip_code = request.form['zip']
        image = request.files['image']

        # Password validation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('registration.html', success=False)

        # Validate file upload
        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Invalid or missing ID image.', 'danger')
            return render_template('registration.html', success=False)

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Database insertion
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO users (
                    first_name, last_name, email, password, phone_number,
                    province, city, barangay, street, zip_code, user_id_path
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, hashed_password, phone_number, 
                  province, city, barangay, street, zip_code, filename))
            mysql.connection.commit()
            flash('Registration successful! Please wait for account approval.', 'success')
            return render_template('registration.html', success=True)
        except Exception as e:
            flash('Error in registration. Email may already be registered.', 'danger')
            print(f"Error during registration: {e}")
        finally:
            cur.close()

    return render_template('registration.html', success=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        phone_number = request.form['phone_number']
        province_code = request.form['province']
        city_code = request.form['city']
        barangay_code = request.form['barangay']
        street = request.form['street']
        zip_code = request.form['zip']
        image = request.files['image']

        # Convert location codes to names
        province_name = get_location_name(province_code, 'province')
        city_name = get_location_name(city_code, 'municipality')
        barangay_name = get_location_name(barangay_code, 'barangay')

        # Password validation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('registration.html', success=False)

        # Validate file upload
        filename = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Invalid or missing ID image.', 'danger')
            return render_template('registration.html', success=False)

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Database insertion
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO users (
                    first_name, last_name, email, password, phone_number,
                    province, city, barangay, street, zip_code, user_id_path
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, hashed_password, phone_number, 
                  province_name, city_name, barangay_name, street, zip_code, filename))
            mysql.connection.commit()
            flash('Registration successful! Please wait for account approval.', 'success')
            return render_template('registration.html', success=True)
        except Exception as e:
            flash('Error in registration. Email may already be registered.', 'danger')
            print(f"Error during registration: {e}")
        finally:
            cur.close()

    return render_template('registration.html', success=False)

# @app.route('/seller-application', methods=['GET', 'POST'])
# def seller_application():
#     if request.method == 'POST':
#         # Get form data
#         first_name = request.form['first_name']
#         last_name = request.form['last_name']
#         email = request.form['contact_email']
#         password = request.form['password']
#         confirm_password = request.form['confirm-password']
#         contact_number = request.form['contact_number']
#         province = request.form['province']
#         city = request.form['city']
#         barangay = request.form['barangay']
#         street = request.form['street']
#         zip_code = request.form['zip']
#         store_name = request.form['store_name']
#         store_description = request.form['store_description']
        
#         # Get uploaded files
#         seller_image = request.files['seller_image']
#         seller_id_image = request.files['seller_id_image']
#         seller_certificate = request.files['seller_certificate']

#         # Check if passwords match
#         if password != confirm_password:
#             flash('Passwords do not match.', 'danger')
#             return render_template('seller-application.html', success=False)

#         # Check if email or phone number already exists
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM sellers WHERE email = %s OR contact_number = %s", (email, contact_number))
#         existing_user = cur.fetchone()
#         if existing_user:
#             flash('Email or contact number is already registered. Please use a different one.', 'danger')
#             return render_template('seller-application.html', success=False)

#         # Hash the password
#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

#         # Initialize file paths for saving
#         seller_image_filename = None
#         seller_id_image_filename = None
#         seller_certificate_filename = None

#         # Save files and store the filenames (not the full paths)
#         if seller_image and allowed_file(seller_image.filename):
#             seller_image_filename = secure_filename(seller_image.filename)
#             seller_image.save(os.path.join(app.config['UPLOAD_FOLDER'], seller_image_filename))

#         if seller_id_image and allowed_file(seller_id_image.filename):
#             seller_id_image_filename = secure_filename(seller_id_image.filename)
#             seller_id_image.save(os.path.join(app.config['UPLOAD_FOLDER'], seller_id_image_filename))

#         if seller_certificate and allowed_file(seller_certificate.filename):
#             seller_certificate_filename = secure_filename(seller_certificate.filename)
#             seller_certificate.save(os.path.join(app.config['UPLOAD_FOLDER'], seller_certificate_filename))

#         # Insert data into the database with the filenames (not the full paths)
#         try:
#             cur.execute("""
#                 INSERT INTO sellers (first_name, last_name, email, password, contact_number, province, city, barangay, street, zip_code,
#                                      store_name, store_description, seller_image, seller_id_path, seller_certificate_path)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """, (first_name, last_name, email, hashed_password, contact_number, province, city, barangay, street, zip_code,
#                   store_name, store_description, seller_image_filename, seller_id_image_filename, seller_certificate_filename))
#             mysql.connection.commit()

#             flash('Registration successful!', 'success')
#             return render_template('seller-application.html', success=True)
#         except Exception as e:
#             mysql.connection.rollback()
#             flash(f'Error registering seller: {str(e)}', 'danger')
#         finally:
#             cur.close()

#     return render_template('seller-application.html', success=False)

@app.route('/seller-application', methods=['GET', 'POST'])
def seller_application():
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['contact_email']
            password = request.form['password']
            confirm_password = request.form['confirm-password']
            contact_number = request.form['contact_number']
            province_code = request.form['province']
            city_code = request.form['city']
            barangay_code = request.form['barangay']
            street = request.form['street']
            zip_code = request.form['zip']
            store_name = request.form['store_name']
            store_description = request.form['store_description']

            # Validate passwords
            if password != confirm_password:
                return jsonify({'status': 'error', 'message': 'Passwords do not match.'})

            # Check if email or phone number already exists
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM sellers WHERE email = %s OR contact_number = %s", (email, contact_number))
            existing_user = cur.fetchone()
            if existing_user:
                return jsonify({'status': 'error', 'message': 'Email or phone number already registered. Please use a different one.'})

            # Convert location codes to names using PSGC API
            province_name = get_location_name(province_code, 'province')
            city_name = get_location_name(city_code, 'municipality')
            barangay_name = get_location_name(barangay_code, 'barangay')

            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # File upload handling
            def save_file(file):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    return filename
                return None

            seller_image_filename = save_file(request.files['seller_image'])
            seller_id_image_filename = save_file(request.files['seller_id_image'])
            seller_certificate_filename = save_file(request.files['seller_certificate'])

            # Insert data into the database with converted location names
            cur.execute("""
                INSERT INTO sellers (first_name, last_name, email, password, contact_number, province, city, barangay, street, zip_code,
                                    store_name, store_description, seller_image, seller_id_path, seller_certificate_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, hashed_password, contact_number, province_name, city_name, barangay_name, street, zip_code,
                store_name, store_description, seller_image_filename, seller_id_image_filename, seller_certificate_filename))
            mysql.connection.commit()

            return jsonify({'status': 'success', 'message': 'Registration successful! Please wait for approval.'})

        except Exception as e:
            mysql.connection.rollback()
            print(f"Database error: {e}")
            return jsonify({'status': 'error', 'message': f'Error registering seller: {str(e)}'})

        finally:
            cur.close()

    return render_template('seller-application.html')


@app.route('/courier_registration', methods=['GET', 'POST'])
def courier_registration():
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm-password']
            phone_number = request.form['phone_number']
            province_code = request.form['province']
            city_code = request.form['city']
            barangay_code = request.form['barangay']
            street = request.form['street']
            zip_code = request.form['zip']
            role = 'courier'

            # Validate passwords
            if password != confirm_password:
                return jsonify({'status': 'error', 'message': 'Passwords do not match.'})

            # Check if email or phone number already exists
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM courier WHERE email = %s OR phone_number = %s", (email, phone_number))
            existing_user = cur.fetchone()
            if existing_user:
                return jsonify({'status': 'error', 'message': 'Email or phone number already registered. Please use a different one.'})

            # Convert location codes to names using PSGC API
            province_name = get_location_name(province_code, 'province')
            city_name = get_location_name(city_code, 'municipality')
            barangay_name = get_location_name(barangay_code, 'barangay')

            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # File upload handling
            def save_file(file):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    return filename
                return None

            license_image_filename = save_file(request.files['license_image'])
            receipt_image_filename = save_file(request.files['receipt_image'])
            registration_image_filename = save_file(request.files['registration_image'])

            # Insert into database with the converted location names
            query = """
                INSERT INTO courier (
                    first_name, last_name, email, password, phone_number,
                    province, city, barangay, street, zip_code, role,
                    license_image, receipt_image, registration_image, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            """
            values = (
                first_name, last_name, email, hashed_password, phone_number,
                province_name, city_name, barangay_name, street, zip_code, role,
                license_image_filename, receipt_image_filename, registration_image_filename
            )

            cur.execute(query, values)
            mysql.connection.commit()
            cur.close()

            return jsonify({'status': 'success', 'message': 'Courier registration submitted! Please wait for approval.'})

        except Exception as e:
            mysql.connection.rollback()
            print(f"Database error: {e}")
            return jsonify({'status': 'error', 'message': f'Error registering courier: {str(e)}'})

    return render_template('courier-registration.html', success=False)






#=============================================== SELLER VIEW PRODUCTS TAB ================================================================
@app.route('/view-products')
def view_products():
    if 'seller_id' in session and session['role'] == 'seller':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM products WHERE archived = 0 AND seller_id = %s", (session['seller_id'],))
        products = cur.fetchall()
        cur.close()
        return render_template('view-products.html', products=products)
    else:
        return redirect(url_for('login'))

@app.route('/view-products-archived')
def view_products_archived():
    if 'seller_id' in session and session['role'] == 'seller':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM products WHERE archived = 1 AND seller_id = %s", (session['seller_id'],))
        products = cur.fetchall()
        cur.close()
        return render_template('view-products-archived.html', products=products)
    else:
        return redirect(url_for('login'))

# DONT DELETE THIS ORIGINAL CODE
# @app.route('/add-product', methods=['GET', 'POST'])
# def add_product():
#     if 'seller_id' in session and session['role'] == 'seller':
#         if request.method == 'POST':
#             # Get form data
#             product_name = request.form['product_name']
#             description = request.form['product_description']
#             price = request.form['product_price']
#             category = request.form['category']
#             subcategory = request.form.getlist('subcategory[]')  # Get list of selected subcategories
#             stocks = request.form['product_stock']
#             image = request.files['product_image']

#             if not subcategory:
#                 subcategory = None  
#             else:
#                 subcategory = ', '.join(subcategory)

#             # Handle image upload
#             if image and image.filename != '':
#                 # Secure file handling and path setup
#                 filename = secure_filename(image.filename)
#                 image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 image.save(image_path)
#             else:
#                 image_path = None  # In case no image is uploaded

#             cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             try:
#                 # Insert product into database
#                 cur.execute('''INSERT INTO products (product_name, description, price, category, subcategory, image_path, stocks, seller_id)
#                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
#                             (product_name, description, price, category, subcategory, filename, stocks, session['seller_id']))
#                 mysql.connection.commit()
#                 flash('Product added successfully!', 'success')
#                 return redirect(url_for('add_product'))
#             except Exception as e:
#                 flash('Error adding product. Please try again.', 'danger')
#                 print(e)
#             finally:
#                 cur.close()

#         return render_template('add-product.html')
#     else:
#         return redirect(url_for('login'))

# @app.route('/add-product', methods=['GET', 'POST'])
# def add_product():
    if 'seller_id' in session and session['role'] == 'seller':
        if request.method == 'POST':
            # Retrieve form data
            product_name = request.form['product_name']
            description = request.form['product_description']
            price = request.form['product_price']
            category = request.form['category']
            subcategory = request.form.getlist('subcategory[]')
            stocks = request.form['product_stock']
            main_image = request.files.get('product_image')
            additional_images = request.files.getlist('additional_images')  # Handles multiple images

            # Convert subcategories to a comma-separated string
            subcategory = ', '.join(subcategory) if subcategory else None

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            try:
                # Insert the new product without the image path first
                cur.execute('''
                    INSERT INTO products (product_name, description, price, category, subcategory, stocks, seller_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (product_name, description, price, category, subcategory, stocks, session['seller_id']))
                mysql.connection.commit()

                # Get the newly inserted product ID
                product_id = cur.lastrowid

                # Handle main product image upload
                if main_image and allowed_file(main_image.filename):
                    main_filename = secure_filename(main_image.filename)
                    main_image_path = os.path.join(app.config['UPLOAD_FOLDER'], main_filename)
                    main_image.save(main_image_path)

                    # Update products table with main image path
                    cur.execute('UPDATE products SET image_path = %s WHERE product_id = %s', (main_filename, product_id))
                    mysql.connection.commit()

                    # Also add the main image to the product_images table
                    cur.execute('INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)', 
                                (product_id, main_filename))
                    mysql.connection.commit()

                # Handle additional images upload
                for image in additional_images:
                    if image and allowed_file(image.filename):
                        additional_filename = secure_filename(image.filename)
                        additional_image_path = os.path.join(app.config['UPLOAD_FOLDER'], additional_filename)
                        image.save(additional_image_path)

                        # Insert each additional image into the product_images table
                        cur.execute('INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)', 
                                    (product_id, additional_filename))
                        mysql.connection.commit()

                flash('Product added successfully with all images!', 'success')
                return redirect(url_for('add_product_page', product_id=product_id))

            except Exception as e:
                flash(f'Error adding product: {e}', 'danger')
            finally:
                cur.close()

        return render_template('add-product.html')
    else:
        return redirect(url_for('login'))


@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if 'seller_id' in session and session['role'] == 'seller':
        if request.method == 'POST':
            # Retrieve form data
            product_name = request.form['product_name']
            description = request.form['product_description']
            price = request.form['product_price']
            category = request.form['category']
            subcategory = request.form.getlist('subcategory[]')
            stocks = request.form['product_stock']
            main_image = request.files.get('product_image')  # Single file
            additional_images = request.files.getlist('additional_images[]')  # Multiple files

            # Convert subcategories to a comma-separated string
            subcategory = ', '.join(subcategory) if subcategory else None

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            try:
                # Insert the new product WITHOUT the image path first
                cur.execute('''
                    INSERT INTO products (product_name, description, price, category, subcategory, stocks, seller_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (product_name, description, price, category, subcategory, stocks, session['seller_id']))
                mysql.connection.commit()

                # Get the newly inserted product ID
                product_id = cur.lastrowid

                # ✅ Save the main image
                if main_image and allowed_file(main_image.filename):
                    main_filename = secure_filename(main_image.filename)
                    main_image_path = os.path.join(app.config['UPLOAD_FOLDER'], main_filename)
                    main_image.save(main_image_path)

                    # Update products table with the main image
                    cur.execute('UPDATE products SET image_path = %s WHERE product_id = %s', (main_filename, product_id))
                    mysql.connection.commit()

                    # Insert the main image into `product_images`
                    cur.execute('INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)', 
                                (product_id, main_filename))
                    mysql.connection.commit()

                # ✅ Save additional images linked to the same `product_id`
                image_count = 0  # Debugging counter
                for image in additional_images:
                    if image and allowed_file(image.filename):
                        additional_filename = secure_filename(image.filename)
                        additional_image_path = os.path.join(app.config['UPLOAD_FOLDER'], additional_filename)
                        image.save(additional_image_path)

                        # Insert each additional image into `product_images`
                        cur.execute('INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)', 
                                    (product_id, additional_filename))
                        mysql.connection.commit()
                        image_count += 1  # Increment counter

                flash(f'Product added successfully with {image_count + 1} images!', 'success')
                return redirect(url_for('add_product_page', product_id=product_id))

            except Exception as e:
                flash(f'Error adding product: {e}', 'danger')
                print(f"Database Error: {e}")
            finally:
                cur.close()

        return render_template('add-product.html')
    else:
        return redirect(url_for('login'))


@app.route('/add-product-image/<int:product_id>', methods=['POST'])
def add_product_image(product_id):
    if 'seller_id' in session and session['role'] == 'seller':
        if 'product_image' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(request.referrer)

        image = request.files['product_image']
        if image.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.referrer)

        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cur.execute('INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)', (product_id, filename))
            mysql.connection.commit()
            flash('Image added successfully!', 'success')
        except Exception as e:
            flash('Error adding image.', 'danger')
            print(e)
        finally:
            cur.close()

        return redirect(request.referrer)
    else:
        return redirect(url_for('login'))


@app.route('/delete-product-image/<int:image_id>', methods=['POST'])
def delete_product_image(image_id):
    if 'seller_id' in session and session['role'] == 'seller':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cur.execute('SELECT image_path, product_id FROM product_images WHERE image_id = %s', (image_id,))
            image = cur.fetchone()

            if image:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image['image_path'])

                # Delete file from storage
                if os.path.exists(image_path):
                    os.remove(image_path)

                # Delete image record from database
                cur.execute('DELETE FROM product_images WHERE image_id = %s', (image_id,))
                mysql.connection.commit()

                # Check if the deleted image was the primary image
                cur.execute('SELECT COUNT(*) AS count FROM product_images WHERE product_id = %s', (image['product_id'],))
                image_count = cur.fetchone()['count']

                # If no images are left, reset the primary image in 'products' table
                if image_count == 0:
                    cur.execute('UPDATE products SET image_path = NULL WHERE product_id = %s', (image['product_id'],))
                    mysql.connection.commit()

                flash('Image deleted successfully!', 'success')
            else:
                flash('Image not found.', 'danger')
        except Exception as e:
            flash('Error deleting image.', 'danger')
            print(e)
        finally:
            cur.close()

        return redirect(request.referrer)
    else:
        return redirect(url_for('login'))


# Route to archive a product
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'seller_id' not in session:
        return jsonify(success=False, message="Seller not logged in"), 403

    seller_id = session['seller_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Archive the product by setting archived to 1
    cur.execute("UPDATE products SET archived = 1 WHERE product_id = %s AND seller_id = %s", (product_id, seller_id))
    mysql.connection.commit()
    cur.close()

    if cur.rowcount > 0:
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Item not found or archive failed"), 400

@app.route('/restore_product/<int:product_id>', methods=['POST'])
def restore_product(product_id):
    if 'seller_id' not in session:
        return jsonify(success=False, message="Seller not logged in"), 403

    seller_id = session['seller_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Archive the product by setting archived to 1
    cur.execute("UPDATE products SET archived = 0 WHERE product_id = %s AND seller_id = %s", (product_id, seller_id))
    mysql.connection.commit()
    cur.close()

    if cur.rowcount > 0:
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Item not found or archive failed"), 400
    
@app.route('/edit_product/<int:product_id>', methods=['GET'])
def edit_product(product_id):
    # Fetch the product details from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('view_products'))

    # Convert subcategories (comma-separated string) into a list
    product['subcategory'] = product['subcategory'].split(',') if product['subcategory'] else []

    return render_template('edit-product.html', product=product)


#save image file function & route
def save_image(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return filename

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if 'seller_id' not in session or session.get('role') != 'seller':
        return redirect('/login')

    # Retrieve form data
    product_name = request.form.get('product_name')
    description = request.form.get('product_description')
    price = request.form.get('product_price')
    category = request.form.get('category')
    subcategories = request.form.getlist('subcategory')  # Expecting a list of subcategories

    # Validate required fields
    if not (product_name and description and price and category and subcategories):
        flash("All fields are required. Please fill out the form correctly.", "error")
        return redirect(request.referrer)

    # Optional image handling
    image_path = None
    file = request.files.get('product_image')
    if file and allowed_file(file.filename):
        image_path = save_image(file)

    try:
        cur = mysql.connection.cursor()

        # Prepare the SQL update query
        query = """
            UPDATE products 
            SET product_name = %s, description = %s, price = %s, category = %s,
                subcategory = %s
        """
        values = [product_name, description, price, category, ','.join(subcategories)]

        # Add image_path to query if provided
        if image_path:
            query += ", image_path = %s"
            values.append(image_path)

        query += " WHERE product_id = %s AND seller_id = %s"
        values.extend([product_id, session['seller_id']])

        # Execute update
        cur.execute(query, tuple(values))
        mysql.connection.commit()
        cur.close()

        # Flash success message and redirect to the product details or list
        flash("Product updated successfully!", "success")
        return redirect('/view-products')

    except Exception as e:
        print("Error editing product:", str(e))
        flash("Failed to update product. Please try again.", "error")
        return redirect(request.referrer)


@app.route('/update-stocks/<int:product_id>', methods=['POST'])
def update_stocks(product_id):
    new_stocks = request.form.get('product_stocks')
    
    # Validate stock input
    if new_stocks is None or not new_stocks.isdigit() or int(new_stocks) < 0:
        return jsonify(success=False, error="Invalid stock quantity"), 400

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        update_query = "UPDATE products SET stocks = %s WHERE product_id = %s AND seller_id = %s"
        cursor.execute(update_query, (int(new_stocks), product_id, session['seller_id']))
        mysql.connection.commit()
        
        # Return success response
        return jsonify(success=True), 200

    except MySQLdb.Error as err:
        return jsonify(success=False, error=f'Error updating stock: {err}'), 500

    finally:
        cursor.close()

#================================================================BUYER Homepage ===========================================================
# @app.route('/search', methods=['GET'])
# def search_products():
    search_query = request.args.get('query', '')
    if search_query:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # SQL Query to get products where product name contains the input, limited to 7 results
        query = """
            SELECT p.product_id, p.image_path, p.product_name, p.price
            FROM products p
            WHERE p.product_name LIKE %s
            ORDER BY p.product_name
            LIMIT 7
        """
        cursor.execute(query, ('%' + search_query + '%',))
        products = cursor.fetchall()
        
        # Close the cursor after the query
        cursor.close()
        
        # If images are stored under `static/uploads/`, prepend the path
        for product in products:
            product['image_path'] = f'static/uploads/{product["image_path"]}'
        
        return jsonify(products)
    
    return jsonify([])

@app.route('/search', methods=['GET'])
def search_items():
    search_query = request.args.get('query', '')
    if search_query:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # SQL Query to search for products
        product_query = """
            SELECT p.product_id, p.image_path, p.product_name, p.price
            FROM products p
            WHERE p.product_name LIKE %s
            ORDER BY p.product_name
            LIMIT 7
        """
        cursor.execute(product_query, ('%' + search_query + '%',))
        products = cursor.fetchall()

        # SQL Query to search for sellers
        seller_query = """
            SELECT s.seller_id, s.seller_image, s.store_name
            FROM sellers s
            WHERE s.store_name LIKE %s
            ORDER BY s.store_name
            LIMIT 7
        """
        cursor.execute(seller_query, ('%' + search_query + '%',))
        sellers = cursor.fetchall()

        cursor.close()

        # Adjust image paths
        for product in products:
            product['image_path'] = f'static/uploads/{product["image_path"]}'
        for seller in sellers:
            seller['seller_image'] = f'static/uploads/{seller["seller_image"]}'

        # Combine results and add a type field for frontend differentiation
        results = {
            'products': products,
            'sellers': sellers
        }

        return jsonify(results)
    
    return jsonify({'products': [], 'sellers': []})




# #DONT DELETE
# @app.route('/homepage')
# def homepage():
#     if 'user_id' in session:
#         cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#         Redirect seller users to the seller's homepage
#         if session['role'] == 'seller':
#             return render_template('seller-homepage.html')

#         Pagination logic
#         per_page = 30  # Number of products per page
#         page = request.args.get('page', 1, type=int)
#         offset = (page - 1) * per_page

#         Fetch paginated products with randomized order
#         cur.execute("""
#             SELECT p.*, 
#                    COALESCE(AVG(r.rating), 0) AS avg_rating 
#             FROM products p
#             LEFT JOIN ratings r ON p.product_id = r.product_id
#             WHERE p.archived = 0
#             GROUP BY p.product_id
#             ORDER BY RAND()
#             LIMIT %s OFFSET %s
#         """, (per_page, offset))
#         products = cur.fetchall()

#         Get total product count for pagination controls
#         cur.execute("SELECT COUNT(*) AS total FROM products WHERE archived = 0")
#         total_products = cur.fetchone()['total']
#         total_pages = (total_products + per_page - 1) // per_page

#         Fetch recommended products based on their average ratings
#         cur.execute("""
#             SELECT p.*, 
#                    COALESCE(AVG(r.rating), 0) AS avg_rating 
#             FROM products p
#             LEFT JOIN ratings r ON p.product_id = r.product_id
#             WHERE p.archived = 0
#             GROUP BY p.product_id
#             ORDER BY avg_rating DESC, p.product_id ASC
#             LIMIT 5
#         """)
#         recommended_products = cur.fetchall()

#         cur.close()

#         Render the homepage with all required data
#         return render_template(
#             'homepage.html',
#             products=products,
#             recommended_products=recommended_products,
#             page=page,
#             total_pages=total_pages
#         )
#     else:
#         return redirect(url_for('login'))

@app.route('/homepage')
def homepage():
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Redirect seller users to the seller's homepage
        if session['role'] == 'seller':
            return render_template('seller-homepage.html')

        # Pagination logic
        per_page = 32  # Number of products per page
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * per_page

        # Fetch paginated products with randomized order
        cur.execute("""
            SELECT p.*, 
                   COALESCE(AVG(r.rating), 0) AS avg_rating 
            FROM products p
            LEFT JOIN ratings r ON p.product_id = r.product_id
            WHERE p.archived = 0
            GROUP BY p.product_id
            ORDER BY RAND()
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        products = cur.fetchall()

        # Get total product count for pagination controls
        cur.execute("SELECT COUNT(*) AS total FROM products WHERE archived = 0")
        total_products = cur.fetchone()['total']
        total_pages = (total_products + per_page - 1) // per_page

        # Fetch recommended products based on their average ratings
        cur.execute("""
            SELECT p.*, 
                   COALESCE(AVG(r.rating), 0) AS avg_rating 
            FROM products p
            LEFT JOIN ratings r ON p.product_id = r.product_id
            WHERE p.archived = 0
            GROUP BY p.product_id
            ORDER BY avg_rating DESC, p.product_id ASC
            LIMIT 5
        """)
        recommended_products = cur.fetchall()

        # Fetch the latest promotion image from the promotions table
        cur.execute("SELECT image_url FROM promotions ORDER BY updated_at DESC LIMIT 1")
        latest_promotion = cur.fetchone()
        promotion_image = latest_promotion['image_url'] if latest_promotion else None

        cur.close()

        # Render the homepage with all required data
        return render_template(
            'homepage.html',
            products=products,
            recommended_products=recommended_products,
            promotion_image=promotion_image,
            page=page,
            total_pages=total_pages
        )
    else:
        return redirect(url_for('login'))



@app.route('/best-seller')
def best_seller():
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if session['role'] == 'seller':
            return render_template('seller-homepage.html')

        # Fetch all products that are not archived
        cur.execute("SELECT * FROM products WHERE archived = 0")
        products = cur.fetchall()

        # Define a query template to get top 8 best-sellers for each category
        best_seller_query = """
            SELECT p.*, COALESCE(SUM(o.quantity), 0) AS total_quantity_sold,
                COALESCE(AVG(r.rating), 0) AS avg_rating
            FROM products p
            LEFT JOIN orders o ON p.product_id = o.product_id
            LEFT JOIN ratings r ON p.product_id = r.product_id
            WHERE p.archived = 0 AND p.category = %s
            GROUP BY p.product_id
            ORDER BY total_quantity_sold DESC
            LIMIT 7
        """


        # Fetch best sellers by category
        cur.execute(best_seller_query, ('Books',))
        best_sellers_books = cur.fetchall()

        cur.execute(best_seller_query, ('Games',))
        best_sellers_games = cur.fetchall()

        cur.execute(best_seller_query, ('Movies',))
        best_sellers_movies = cur.fetchall()

        # Fetch the latest promotion image from the promotions table
        cur.execute("SELECT image_url FROM promotions ORDER BY updated_at DESC LIMIT 1")
        latest_promotion = cur.fetchone()
        promotion_image = latest_promotion['image_url'] if latest_promotion else None

        cur.close()

        return render_template(
            'best-sellers.html',
            books=best_sellers_books,
            promotion_image=promotion_image,
            games=best_sellers_games,
            movies=best_sellers_movies
        )
    else:
        return redirect(url_for('login'))
    

# @app.route('/admin/upload-promotion', methods=['GET', 'POST'])
# def upload_promotion():
#     if 'admin_id' not in session:  # Ensure the admin is logged in
#         return redirect(url_for('login'))  # Redirect to login page if unauthorized

#     if request.method == 'POST':
#         # Check if the post request has the file part
#         if 'file' not in request.files:
#             return jsonify({"success": False, "error": "No file part"}), 400

#         file = request.files['file']

#         # If the user does not select a file
#         if file.filename == '':
#             return jsonify({"success": False, "error": "No selected file"}), 400

#         # Check if the file is allowed
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)  # Secure the file name
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)  # Save the file to the upload folder

#             try:
#                 cursor = mysql.connection.cursor()
#                 # Insert only the file name into the database
#                 cursor.execute('INSERT INTO promotions (image_url) VALUES (%s)', (filename,))
#                 mysql.connection.commit()
#                 cursor.close()
#                 return jsonify({"success": True, "message": "Promotion uploaded successfully"})
#             except Exception as e:
#                 print(f"Error uploading promotion: {e}")
#                 return jsonify({"success": False, "error": "Error uploading promotion"}), 500
#         else:
#             return jsonify({"success": False, "error": "Invalid file type"}), 400

#     # Fetch all promotions to display in the template
#     try:
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute("SELECT * FROM promotions ORDER BY updated_at DESC")
#         promotions = cursor.fetchall()
#         cursor.close()
#     except Exception as e:
#         print(f"Error fetching promotions: {e}")
#         promotions = []

#     # Render the admin promotions template
#     return render_template('admin_promotions.html', promotions=promotions)


@app.route('/admin/upload-promotion', methods=['GET', 'POST'])
def upload_promotion():
    if 'admin_id' not in session:  # Ensure the admin is logged in
        return redirect(url_for('login'))  # Redirect to login page if unauthorized

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file
        if file.filename == '':
            flash("No selected file", "danger")
            return redirect(request.url)

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Secure the file name
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the file to the upload folder

            try:
                cursor = mysql.connection.cursor()
                # Insert only the file name into the database
                cursor.execute('INSERT INTO promotions (image_url) VALUES (%s)', (filename,))
                mysql.connection.commit()
                cursor.close()
                flash("Promotion uploaded successfully", "success")
                return redirect(url_for('upload_promotion'))
            except Exception as e:
                print(f"Error uploading promotion: {e}")
                flash("Error uploading promotion", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file type", "danger")
            return redirect(request.url)

    # Fetch all promotions, with the latest one being shown separately
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch the latest promotion
        cursor.execute("SELECT * FROM promotions ORDER BY updated_at DESC LIMIT 1")
        current_promotion = cursor.fetchone()

        # Fetch all other promotions excluding the latest
        cursor.execute("SELECT * FROM promotions ORDER BY updated_at DESC LIMIT 100 OFFSET 1")
        promotions = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Error fetching promotions: {e}")
        current_promotion, promotions = None, []

    # Render the admin promotions template
    return render_template(
        'admin_promotions.html', 
        current_promotion=current_promotion, 
        promotions=promotions
    )

@app.route('/admin/promotion-action', methods=['POST'])
def promotion_action():
    if 'admin_id' not in session:  # Ensure the admin is logged in
        return redirect(url_for('login'))  # Redirect to login page if unauthorized

    # Retrieve action and promotion_id from the form
    action = request.form.get('action')
    promotion_id = request.form.get('promotion_id')

    if not action or not promotion_id:
        flash("Invalid request.", "danger")
        return redirect(url_for('upload_promotion'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        if action == 'delete':
            # Fetch the promotion to delete its image
            cursor.execute("SELECT image_url FROM promotions WHERE id = %s", (promotion_id,))
            promotion = cursor.fetchone()

            if not promotion:
                flash("Promotion not found.", "danger")
                return redirect(url_for('upload_promotion'))

            # Remove the image from the file system
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], promotion['image_url'])
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete the promotion from the database
            cursor.execute("DELETE FROM promotions WHERE id = %s", (promotion_id,))
            mysql.connection.commit()
            flash("Promotion deleted successfully.", "success")

        elif action == 'reupload':
            # Mark the promotion as the most recent
            cursor.execute("UPDATE promotions SET updated_at = NOW() WHERE id = %s", (promotion_id,))
            mysql.connection.commit()
            flash("Promotion set as current successfully.", "success")

        else:
            flash("Invalid action.", "danger")

    except Exception as e:
        print(f"Error performing promotion action: {e}")
        flash("An error occurred while processing your request.", "danger")

    finally:
        cursor.close()

    return redirect(url_for('upload_promotion'))


@app.route('/admin/reupload-promotion/<int:promotion_id>', methods=['POST'])
def reupload_promotion(promotion_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE promotions SET updated_at = NOW() WHERE id = %s", (promotion_id,))
        mysql.connection.commit()
        cursor.close()
        flash("Promotion set as current successfully.", "success")
    except Exception as e:
        print(f"Error during reupload: {e}")
        flash("An error occurred while reuploading.", "danger")
    return redirect(url_for('upload_promotion'))

@app.route('/admin/delete-promotion/<int:promotion_id>', methods=['POST'])
def delete_promotion(promotion_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT image_url FROM promotions WHERE id = %s", (promotion_id,))
        promotion = cursor.fetchone()

        if promotion:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], promotion['image_url'])
            if os.path.exists(file_path):
                os.remove(file_path)

            cursor.execute("DELETE FROM promotions WHERE id = %s", (promotion_id,))
            mysql.connection.commit()
            flash("Promotion deleted successfully.", "success")
        else:
            flash("Promotion not found.", "danger")
    except Exception as e:
        print(f"Error during delete: {e}")
        flash("An error occurred while deleting.", "danger")
    finally:
        cursor.close()
    return redirect(url_for('upload_promotion'))


# @app.route('/admin/reupload-promotion/<int:promotion_id>', methods=['POST'])
# def reupload_promotion(promotion_id):
#     if 'admin_id' not in session:  # Ensure the admin is logged in
#         return redirect(url_for('login'))  # Redirect to login page if unauthorized

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Fetch the current promotion details
#     cursor.execute("SELECT * FROM promotions WHERE id = %s", (promotion_id,))
#     promotion = cursor.fetchone()

#     if not promotion:
#         flash("Promotion not found.", "danger")
#         return redirect(url_for('upload_promotion'))

#     try:
#         # Update only the updated_at column to mark this promotion as the most recent
#         cursor.execute(
#             "UPDATE promotions SET updated_at = NOW() WHERE id = %s",
#             (promotion_id,)
#         )
#         mysql.connection.commit()
#         flash("Promotion updated successfully", "success")
#     except Exception as e:
#         print(f"Error updating promotion: {e}")
#         flash("Error updating promotion", "danger")
#     finally:
#         cursor.close()

#     return redirect(url_for('upload_promotion'))


# @app.route('/admin/delete-promotion/<int:promotion_id>', methods=['POST'])
# def delete_promotion(promotion_id):
#     if 'admin_id' not in session:  # Ensure the admin is logged in
#         return redirect(url_for('login'))  # Redirect to login page if unauthorized

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     try:
#         # Fetch the promotion to get its file name
#         cursor.execute("SELECT image_url FROM promotions WHERE id = %s", (promotion_id,))
#         promotion = cursor.fetchone()

#         if not promotion:
#             flash("Promotion not found.", "danger")
#             return redirect(url_for('upload_promotion'))

#         # Delete the file from the server
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], promotion['image_url'])
#         if os.path.exists(file_path):
#             os.remove(file_path)

#         # Delete the promotion from the database
#         cursor.execute("DELETE FROM promotions WHERE id = %s", (promotion_id,))
#         mysql.connection.commit()
#         flash("Promotion deleted successfully.", "success")

#     except Exception as e:
#         print(f"Error deleting promotion: {e}")
#         flash("Error deleting promotion.", "danger")
#     finally:
#         cursor.close()

#     return redirect(url_for('upload_promotion'))




@app.route('/new-products')
def new_products():
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get the current date and calculate the date 2 weeks ago
        two_weeks_ago = datetime.now() - timedelta(days=14)

        # Fetch the 5 most recent products created within the last 2 weeks
        cur.execute("""
            SELECT p.*, 
                   COALESCE(AVG(r.rating), 0) AS avg_rating 
            FROM products p
            LEFT JOIN ratings r ON p.product_id = r.product_id
            WHERE p.archived = 0 AND p.created_at >= %s
            GROUP BY p.product_id
            ORDER BY p.created_at DESC
            LIMIT 5
        """, (two_weeks_ago,))
        new_products = cur.fetchall()

        # If there are no new arrivals, fetch the 5 latest products overall
        if not new_products:
            cur.execute("""
                SELECT p.*, 
                       COALESCE(AVG(r.rating), 0) AS avg_rating 
                FROM products p
                LEFT JOIN ratings r ON p.product_id = r.product_id
                WHERE p.archived = 0
                GROUP BY p.product_id
                ORDER BY p.created_at DESC
                LIMIT 5
            """)
            new_products = cur.fetchall()

        # Pagination logic for "All Products"
        per_page = 30  # Number of products per page
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * per_page

        # Fetch all products newest to oldest
        cur.execute("""
            SELECT p.*, 
                COALESCE(AVG(r.rating), 0) AS avg_rating 
            FROM products p
            LEFT JOIN ratings r ON p.product_id = r.product_id
            WHERE p.archived = 0
            GROUP BY p.product_id
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        products = cur.fetchall()

        # Fetch the latest promotion image from the promotions table
        cur.execute("SELECT image_url FROM promotions ORDER BY updated_at DESC LIMIT 1")
        latest_promotion = cur.fetchone()
        promotion_image = latest_promotion['image_url'] if latest_promotion else None

        # Get total product count for pagination controls
        cur.execute("SELECT COUNT(*) AS total FROM products WHERE archived = 0")
        total_products = cur.fetchone()['total']
        total_pages = (total_products + per_page - 1) // per_page

        cur.close()

        # Render the new-products.html with the required data
        return render_template(
            'new-products.html',
            new_products=new_products,
            products=products,
            page=page,
            promotion_image=promotion_image,
            total_pages=total_pages
        )
    else:
        return redirect(url_for('login'))

# @app.route('/on-sale', methods=['GET'])
# def on_sale():
#     try:
#         cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#         # Fetch recommended products based on their average ratings
#         cur.execute("""
#             SELECT p.product_id, p.product_name, p.image_path, p.price, 
#                    COALESCE(AVG(r.rating), 0) AS avg_rating
#             FROM products p
#             LEFT JOIN ratings r ON p.product_id = r.product_id
#             WHERE p.archived = 0
#             GROUP BY p.product_id
#             ORDER BY avg_rating DESC, p.product_id ASC
#             LIMIT 5
#         """)
#         recommended_products = cur.fetchall()

#         # Fetch all vouchers
#         cur.execute("""
#             SELECT voucher_code, description, voucher_image
#             FROM vouchers
#         """)
#         vouchers = cur.fetchall()

#         # Render the on-sale.html template with data
#         return render_template(
#             'on-sale.html',
#             recommended_products=recommended_products,
#             vouchers=vouchers
#         )
#     except Exception as e:
#         flash(f"Error loading On Sale page: {e}", "error")
#         return render_template('on-sale.html', recommended_products=[], vouchers=[])
#     finally:
#         cur.close()

@app.route('/on-sale', methods=['GET'])
def on_sale():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch recommended products based on their average ratings
        cur.execute("""
            SELECT p.product_id, p.product_name, p.image_path, p.price, 
                   COALESCE(AVG(r.rating), 0) AS avg_rating
            FROM products p
            LEFT JOIN ratings r ON p.product_id = r.product_id
            WHERE p.archived = 0
            GROUP BY p.product_id
            ORDER BY avg_rating DESC, p.product_id ASC
            LIMIT 5
        """)
        recommended_products = cur.fetchall()
        
        # Fetch the latest promotion image from the promotions table
        cur.execute("SELECT image_url FROM promotions ORDER BY updated_at DESC LIMIT 1")
        latest_promotion = cur.fetchone()
        promotion_image = latest_promotion['image_url'] if latest_promotion else None


        # Fetch all vouchers
        cur.execute("""
            SELECT voucher_code, description, voucher_image
            FROM vouchers
        """)
        vouchers = cur.fetchall()

        # Process voucher image paths to be compatible with Flask
        vouchers_list = [
            {
                "voucher_code": row["voucher_code"],
                "description": row["description"],
                "voucher_image": row["voucher_image"].split("static/")[-1]  # Extract the relative path
            }
            for row in vouchers
        ]

        # Render the on-sale.html template with data
        return render_template(
            'on-sale.html',
            recommended_products=recommended_products,
            promotion_image= promotion_image, 
            vouchers=vouchers_list
        )
    except Exception as e:
        flash(f"Error loading On Sale page: {e}", "error")
        return render_template('on-sale.html', recommended_products=[], vouchers=[])
    finally:
        cur.close()



#================================Seller Dashboard=====================================================================================

@app.route('/seller-homepage')
def seller_homepage():
    if 'seller_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    # Initialize default values
    total_sales = 0
    new_orders = 0
    product_count = 0
    returns_refunds = 0
    on_delivery = 0
    daily_sales = 0
    low_stock_count = 0
    out_of_stock_count = 0
    store_name = "Your Store"
    top_products = []

    # Get data from MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    seller_id = session['seller_id']

    # Query for store_name from sellers table
    cursor.execute('''
        SELECT store_name 
        FROM sellers 
        WHERE seller_id = %s
    ''', (seller_id,))
    result = cursor.fetchone()
    if result and result['store_name']:
        store_name = result['store_name']

    # Query for Total Sales
    cursor.execute('''
        SELECT SUM(o.total_price) AS total_sales 
        FROM orders o 
        JOIN products p ON o.product_id = p.product_id 
        WHERE p.seller_id = %s AND o.order_status = %s
    ''', (seller_id, 'completed'))
    result = cursor.fetchone()
    if result and result['total_sales'] is not None:
        total_sales = result['total_sales']

    # Query for Daily Sales (Sales made today)
    cursor.execute('''
        SELECT SUM(o.total_price) AS daily_sales 
        FROM orders o 
        JOIN products p ON o.product_id = p.product_id 
        WHERE p.seller_id = %s AND o.order_status = %s AND DATE(o.updated_at) = CURDATE()
    ''', (seller_id, 'completed'))
    result = cursor.fetchone()
    if result and result['daily_sales'] is not None:
        daily_sales = result['daily_sales']

    # Query for New Orders
    cursor.execute('''
        SELECT COUNT(*) AS new_orders 
        FROM orders o 
        JOIN products p ON o.product_id = p.product_id 
        WHERE p.seller_id = %s AND o.order_status = %s
    ''', (seller_id, 'pending'))
    result = cursor.fetchone()
    if result:
        new_orders = result['new_orders']

    # Query for Product Count
    cursor.execute('''
        SELECT COUNT(*) AS product_count 
        FROM products 
        WHERE seller_id = %s AND archived = 0
    ''', (seller_id,))
    result = cursor.fetchone()
    if result:
        product_count = result['product_count']

    # Query for Returns/Refunds
    cursor.execute('''
        SELECT COUNT(*) AS returns_refunds 
        FROM orders o 
        JOIN products p ON o.product_id = p.product_id 
        WHERE p.seller_id = %s AND o.order_status = %s
    ''', (seller_id, 'returned/refunded'))
    result = cursor.fetchone()
    if result:
        returns_refunds = result['returns_refunds']

    # Query for On Delivery
    cursor.execute('''
        SELECT COUNT(*) AS on_delivery 
        FROM orders o 
        JOIN products p ON o.product_id = p.product_id 
        WHERE p.seller_id = %s AND o.order_status = %s
    ''', (seller_id, 'on_the_way'))
    result = cursor.fetchone()
    if result:
        on_delivery = result['on_delivery']

    # Query for Low Stock Products (Stocks <= 20)
    cursor.execute('''
        SELECT COUNT(*) AS low_stock_count
        FROM products
        WHERE seller_id = %s AND stocks > 0 AND stocks <= 20
    ''', (seller_id,))
    result = cursor.fetchone()
    if result and result['low_stock_count'] is not None:
        low_stock_count = result['low_stock_count']

    # Query for Daily Sales (Sales made today)
    cursor.execute('''
        SELECT SUM(o.total_price) AS daily_sales 
        FROM orders o 
        JOIN products p ON o.product_id = p.product_id 
        WHERE p.seller_id = %s AND o.order_status = %s AND DATE(o.updated_at) = CURDATE()
    ''', (seller_id, 'completed'))
    result = cursor.fetchone()
    if result and result['daily_sales'] is not None:
        daily_sales = result['daily_sales']

    # Query for Out-of-Stock Products (Stocks = 0)
    cursor.execute('''
        SELECT COUNT(*) AS out_of_stock_count
        FROM products
        WHERE seller_id = %s AND stocks = 0
    ''', (seller_id,))
    result = cursor.fetchone()
    if result and result['out_of_stock_count'] is not None:
        out_of_stock_count = result['out_of_stock_count']

    # # Query for Top Selling Products
    # cursor.execute('''
    #    SELECT 
    #         p.product_id, 
    #         p.product_name, 
    #         p.image_path, 
    #         p.stocks,
    #         SUM(o.total_price) AS total_sales, 
    #         COALESCE(AVG(r.rating), 0) AS average_rating
    #     FROM products p
    #     LEFT JOIN orders o ON p.product_id = o.product_id
    #     LEFT JOIN ratings r ON p.product_id = r.product_id
    #     WHERE p.seller_id = %s
    #     GROUP BY p.product_id, p.product_name, p.image_path, p.stocks
    #     ORDER BY total_sales DESC
    #     LIMIT 5
    # ''', (seller_id,))
    # top_products = cursor.fetchall()

    # Query for Top Selling Products by Quantities and Total Sales
    cursor.execute('''
        SELECT 
            p.product_id, 
            p.product_name, 
            p.image_path, 
            p.stocks,
            SUM(o.quantity) AS total_quantity_sold, 
            SUM(o.total_price) AS total_sales,
            COALESCE(AVG(r.rating), 0) AS average_rating
        FROM products p
        LEFT JOIN orders o ON p.product_id = o.product_id
        LEFT JOIN ratings r ON p.product_id = r.product_id
        WHERE p.seller_id = %s
        GROUP BY p.product_id, p.product_name, p.image_path, p.stocks
        ORDER BY total_quantity_sold DESC
        LIMIT 5
    ''', (seller_id,))
    top_products = cursor.fetchall()

    # Query for Unread Chat Notifications
    cursor.execute('''
        SELECT DISTINCT u.email AS sender_email, MAX(m.timestamp) AS latest_message_time
        FROM messages m
        JOIN users u ON m.sender_id = u.user_id
        WHERE m.receiver_id = %s AND m.seen_status = 0
        GROUP BY u.email
        ORDER BY latest_message_time DESC
    ''', (seller_id,))
    unread_chat_notifications = cursor.fetchall()

    # Close the cursor
    cursor.close()

    # Pass the values to the template
    return render_template(
        'seller-homepage.html',
        total_sales=total_sales,
        new_orders=new_orders,
        product_count=product_count,
        returns_refunds=returns_refunds,
        on_delivery=on_delivery,
        store_name=store_name,
        top_products=top_products,
        unread_chat_notifications=unread_chat_notifications,
        daily_sales=daily_sales,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count
    )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch product details
    cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cur.fetchone()

    # Fetch seller details if the product exists
    seller = None
    if product:
        cur.execute("SELECT * FROM sellers WHERE seller_id = %s", (product['seller_id'],))
        seller = cur.fetchone()

    # Fetch customer reviews from the ratings table
    cur.execute("SELECT * FROM ratings WHERE product_id = %s ORDER BY created_at DESC", (product_id,))
    reviews = cur.fetchall()

    # Fetch product ratings summary (average and total reviews)
    cur.execute(
        """
        SELECT 
            AVG(rating) as average_rating, 
            COUNT(*) as total_reviews 
        FROM ratings 
        WHERE product_id = %s
        """, 
        (product_id,)
    )
    rating_summary = cur.fetchone()

    # Handle case when there are no ratings
    if not rating_summary['average_rating']:
        rating_summary['average_rating'] = 0
        rating_summary['total_reviews'] = 0

    # Fetch total quantity sold for the product
    cur.execute(
        """
        SELECT COALESCE(SUM(quantity), 0) as total_sold 
        FROM orders
        WHERE product_id = %s
        """,
        (product_id,)
    )
    total_sold = cur.fetchone()['total_sold']

    cur.close()

    if product:
        return render_template(
            'product-details.html',
            product=product,
            seller=seller,
            reviews=reviews,
            rating_summary=rating_summary,
            total_sold=total_sold  # Pass total_sold to the template
        )
    else:
        flash('Product not found.', 'danger')
        return redirect(url_for('homepage'))

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    if 'user_id' not in session:
        flash("Please log in to submit a rating.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    product_id = request.form.get('product_id')
    rating = request.form.get('rating')
    comment = request.form.get('comment')

    if not product_id or not rating:
        flash("Rating and Product ID are required.", "danger")
        return redirect(request.referrer or url_for('user_orders'))

    try:
        cursor = mysql.connection.cursor()

        # Insert the rating into the ratings table
        cursor.execute("""
            INSERT INTO ratings (user_id, product_id, rating, comment, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (user_id, product_id, rating, comment))

        # Update the order_status to 'delivered'
        cursor.execute("""
            UPDATE orders 
            SET order_status = 'delivered'
            WHERE product_id = %s AND user_id = %s AND order_status = 'on_the_way'
        """, (product_id, user_id))

        mysql.connection.commit()
        cursor.close()

        flash("Thank you for your feedback! Order status updated to 'delivered'.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"An error occurred: {e}", "danger")

    return redirect(request.referrer or url_for('user_orders'))




#==================================================== User Account Settings ==================================================================

@app.route('/user-account', methods=['GET'])
def user_account():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Create a cursor to interact with the MySQL database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to get the user information, including the profile image URL
        cursor.execute('''
            SELECT first_name, last_name, email, phone_number, profile_image_url
            FROM users WHERE user_id = %s
        ''', (user_id,))
        
        user = cursor.fetchone()
        
        # Set the correct path for profile_image_url
        if user and user['profile_image_url']:
            # Use the uploads folder for user-uploaded profile images
            user['profile_image_url'] = 'uploads/' + user['profile_image_url']
        else:
            # Use the default image if no profile image is found
            user['profile_image_url'] = 'images/default-user.png'

        # Render the profile with user data if found
        if user:
            return render_template('user-account.html', user=user)
        else:
            flash('User not found', 'error')
            return redirect(url_for('login'))
    else:
        flash('Please log in to access your account', 'warning')
        return redirect(url_for('login'))

@app.route('/user-privacy')
def user_privacy():
    user_id = session.get('user_id')
    user = None

    if user_id:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()

        # Set default profile image if none exists
        if user and not user.get('profile_image_url'):
            user['profile_image_url'] = 'images/default-user.png'
        else:
            # Use the uploads folder for user-uploaded profile images if available
            user['profile_image_url'] = 'uploads/' + user['profile_image_url'] if user.get('profile_image_url') else 'images/default-user.png'

    return render_template('user-privacy.html', user=user)

@app.route('/user-address')
def user_address():
    # Get the user ID from the session (assuming the user is logged in)
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('login')) 
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch default address from the users table
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))

    # Fetch additional addresses from the new_addresses table
    cursor.execute("SELECT * FROM new_addresses WHERE user_id = %s", (user_id,))
    additional_addresses = cursor.fetchall()

    cursor.close()

    # Set the correct path for profile_image_url
    if user and user['profile_image_url']:
        user['profile_image_url'] = 'uploads/' + user['profile_image_url']
    else:
        user['profile_image_url'] = 'images/default-user.png'

    # Render the template with user and additional addresses data
    return render_template(
        'user-address.html',
        user=user,
        additional_addresses=additional_addresses
    )


@app.route('/edit-address/<int:user_id>', methods=['GET', 'POST'])
def edit_address(user_id):
    session_user_id = session.get('user_id')
    
    if not session_user_id or session_user_id != user_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'GET':
        # Fetch user details
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('user_address'))

        # Fetch all provinces for the dropdown
        provinces = fetch_location_data('provinces/')

        # Prepopulate user details with readable names
        user['province_name'] = get_location_name(user['province'], 'province')
        user['city_name'] = get_location_name(user['city'], 'municipality')
        user['barangay_name'] = get_location_name(user['barangay'], 'barangay')

        # Set profile image
        user['profile_image_url'] = (
            f"uploads/{user['profile_image_url']}" if user.get('profile_image_url') else "images/default-user.png"
        )

        return render_template('edit-address.html', user=user, provinces=provinces)

    if request.method == 'POST':
        # Collect form data
        street = request.form['street']
        barangay_code = request.form['barangay']
        city_code = request.form['city']
        province_code = request.form['province']
        zip_code = request.form['zip_code']

        # Get the names for province, city, and barangay
        province_name = get_location_name(province_code, 'province')
        city_name = get_location_name(city_code, 'municipality')
        barangay_name = get_location_name(barangay_code, 'barangay')

        # Validate input
        if not street or not barangay_name or not city_name or not province_name or not zip_code:
            flash('All fields are required', 'error')
            return redirect(url_for('edit_address', user_id=user_id))

        try:
            # Update the user's address in the database
            cursor.execute(""" 
                UPDATE users 
                SET street = %s, barangay = %s, city = %s, province = %s, zip_code = %s
                WHERE user_id = %s
            """, (street, barangay_name, city_name, province_name, zip_code, user_id))
            mysql.connection.commit()

            flash('Address updated successfully', 'success')
            return redirect(url_for('user_address'))  # Redirect to address page
        except Exception as e:
            print(f"Database error: {e}")
            flash('Failed to update address', 'error')
            return redirect(url_for('edit_address', user_id=user_id))


def fetch_location_data(endpoint):
    """
    Fetches a list of location data (provinces, municipalities, or barangays) 
    from the PSGC API.
    
    :param endpoint: The API endpoint to fetch data from (e.g., "provinces/").
    :return: A list of location data or an empty list on error.
    """
    base_url = "https://psgc.gitlab.io/api/"
    try:
        response = requests.get(f"{base_url}{endpoint}")
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return the JSON response as a list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from endpoint '{endpoint}': {e}")
        return []  # Return an empty list on error


@app.route('/get-cities/<province_code>', methods=['GET'])
def get_cities(province_code):
    municipalities = fetch_location_data(f"provinces/{province_code}/municipalities/")
    return jsonify(municipalities)

@app.route('/get-barangays/<city_code>', methods=['GET'])
def get_barangays(city_code):
    barangays = fetch_location_data(f"municipalities/{city_code}/barangays/")
    return jsonify(barangays)


@app.route('/add-address', methods=['GET', 'POST'])
def add_address():
    user_id = session.get('user_id')  # Get the user ID from the session

    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found", "error")
        return redirect(url_for('login'))  # Redirect if user doesn't exist

    # Set a default profile image if not provided
    user['profile_image_url'] = (
        f"uploads/{user['profile_image_url']}" if user.get('profile_image_url') else "images/default-user.png"
    )

    if request.method == 'POST':
        # Collect form data
        street = request.form['street']
        barangay_code = request.form['barangay']
        city_code = request.form['city']
        province_code = request.form['province']
        zip_code = request.form['zip_code']

        # Get the names for province, city, and barangay
        province_name = get_location_name(province_code, 'province')
        city_name = get_location_name(city_code, 'municipality')
        barangay_name = get_location_name(barangay_code, 'barangay')

        # Insert the new address into the database
        cursor.execute("""
            INSERT INTO new_addresses (user_id, street, barangay, city, province, zip_code)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, street, barangay_name, city_name, province_name, zip_code))
        mysql.connection.commit()

        flash('Address added successfully', 'success')
        return redirect(url_for('user_address'))

    # Fetch provinces for the dropdown
    provinces = fetch_location_data("provinces/")

    return render_template('add-address.html', user=user, provinces=provinces)


@app.route('/edit-new-address/<int:address_id>', methods=['GET', 'POST']) 
def edit_new_address(address_id):
    session_user_id = session.get('user_id')
    
    if not session_user_id:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'GET':
        # Fetch the specific address from the new_addresses table
        cursor.execute("SELECT * FROM new_addresses WHERE id = %s AND user_id = %s", (address_id, session_user_id))
        address = cursor.fetchone()

        if not address:
            flash('Address not found', 'error')
            return redirect(url_for('user_address'))

        # Fetch user details for the template
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (session_user_id,))
        user = cursor.fetchone()

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('login'))

        # Fetch all provinces for the dropdown
        provinces = fetch_location_data('provinces/')

        # Prepopulate address details with readable names
        address['province_name'] = get_location_name(address['province'], 'province')
        address['city_name'] = get_location_name(address['city'], 'municipality')
        address['barangay_name'] = get_location_name(address['barangay'], 'barangay')

        return render_template('edit-new-address.html', address=address, user=user, provinces=provinces)

    if request.method == 'POST':
        # Collect form data
        street = request.form['street']
        barangay_code = request.form['barangay']
        city_code = request.form['city']
        province_code = request.form['province']
        zip_code = request.form['zip_code']

        # Get the names for province, city, and barangay
        province_name = get_location_name(province_code, 'province')
        city_name = get_location_name(city_code, 'municipality')
        barangay_name = get_location_name(barangay_code, 'barangay')

        # Validate input
        if not street or not barangay_name or not city_name or not province_name or not zip_code:
            flash('All fields are required', 'error')
            return redirect(url_for('edit_new_address', address_id=address_id))

        try:
            # Update the address in the new_addresses table
            cursor.execute(""" 
                UPDATE new_addresses 
                SET street = %s, barangay = %s, city = %s, province = %s, zip_code = %s, created_at = NOW()
                WHERE id = %s AND user_id = %s
            """, (street, barangay_name, city_name, province_name, zip_code, address_id, session_user_id))
            mysql.connection.commit()

            flash('Address updated successfully', 'success')
            return redirect(url_for('user_address'))  # Redirect to address page
        except Exception as e:
            print(f"Database error: {e}")
            flash('Failed to update address', 'error')
            return redirect(url_for('edit_new_address', address_id=address_id))




#====================================================UPDATE USER ACCOUNT=================================================================
# Route to update email
@app.route('/update_email', methods=['POST'])
def update_email():
    if 'user_id' in session:
        user_id = session['user_id']
        new_email = request.form['new_email']
        
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE users SET email = %s WHERE user_id = %s', (new_email, user_id))
        mysql.connection.commit()
        cursor.close()
        
        flash("Email updated successfully!", "success")
    return redirect(url_for('user_privacy'))

# Route to update phone number
@app.route('/update_phone', methods=['POST'])
def update_phone():
    if 'user_id' in session:
        user_id = session['user_id']
        new_phone = request.form['new_phone']
        
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE users SET phone_number = %s WHERE user_id = %s', (new_phone, user_id))
        mysql.connection.commit()
        cursor.close()
        
        flash("Phone number updated successfully!", "success")
    return redirect(url_for('user_privacy'))

# Route to update password
@app.route('/update_password', methods=['POST'])
def update_password():
    if 'user_id' in session:
        user_id = session['user_id']
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET password = %s WHERE user_id = %s', (hashed_password, user_id))
        mysql.connection.commit()
        cursor.close()
        
        flash("Password updated successfully!")
    return redirect(url_for('user_privacy'))

# Route to update profile picture
@app.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    if 'user_id' in session:
        user_id = session['user_id']
        file = request.files['profile_picture']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE users SET profile_image_url = %s WHERE user_id = %s', (filename, user_id))
            mysql.connection.commit()
            cursor.close()
            
            flash("Profile picture updated successfully!", "success")
        else:
            flash("Invalid file format. Please upload a PNG, JPG, or JPEG file.", "error")
    return redirect(url_for('user_privacy'))

#============================================== Cart routes ============================================================================    
# @app.route('/cart', methods=['GET'])
# def cart():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch cart items with product and seller information
        cur.execute('''
            SELECT cart.*, 
                   (quantity * price) AS total_price, 
                   products.product_name, 
                   products.price, 
                   products.image_path,
                   sellers.store_name
            FROM cart
            JOIN products ON cart.product_id = products.product_id
            JOIN sellers ON products.seller_id = sellers.seller_id
            WHERE cart.user_id = %s
        ''', (user_id,))
        
        cart_items = cur.fetchall()
        
        # Calculate total price of cart items
        total_price_cart = sum(item['total_price'] for item in cart_items)
        cur.close()
        
        return render_template('cart.html', cart=cart_items, total_price_cart=total_price_cart)
    else:
        return redirect(url_for('login'))


@app.route('/cart', methods=['GET'])
def cart():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch cart items with product and seller information, including stocks
        cur.execute('''
            SELECT cart.*, 
                   (quantity * price) AS total_price, 
                   products.product_name, 
                   products.price, 
                   products.image_path, 
                   products.stocks, 
                   sellers.store_name
            FROM cart
            JOIN products ON cart.product_id = products.product_id
            JOIN sellers ON products.seller_id = sellers.seller_id
            WHERE cart.user_id = %s
        ''', (user_id,))
        
        cart_items = cur.fetchall()
        
        # Calculate total price of cart items
        total_price_cart = sum(item['total_price'] for item in cart_items)
        cur.close()
        
        return render_template('cart.html', cart=cart_items, total_price_cart=total_price_cart)
    else:
        return redirect(url_for('login'))


@app.route('/proceedCheckout', methods=['POST'])
def proceedCheckout():
    if 'user_id' not in session:
        return jsonify({"success": False, "redirect": url_for('login')})

    user_id = session['user_id']
    selected_item_ids = request.form.getlist('selected_items[]')

    if not selected_item_ids:
        return jsonify({"success": False, "message": "Please select at least one item to checkout."})

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        invalid_items = []

        # Fetch selected cart items with product details and validate stock
        cur.execute(f'''
            SELECT cart.cart_id, 
                   cart.quantity AS cart_quantity, 
                   products.product_name, 
                   products.stocks, 
                   products.price
            FROM cart
            JOIN products ON cart.product_id = products.product_id
            WHERE cart.cart_id IN ({','.join(['%s'] * len(selected_item_ids))})
              AND cart.user_id = %s
        ''', (*selected_item_ids, user_id))

        selected_items = cur.fetchall()

        for item in selected_items:
            cart_id = item['cart_id']
            selected_quantity = int(request.form.get(f'quantities[{cart_id}]', 0))

            # Check if the selected quantity exceeds stock
            if selected_quantity > item['stocks']:
                invalid_items.append({
                    "product_name": item['product_name'],
                    "available_stock": item['stocks'],
                    "requested_quantity": selected_quantity
                })

        if invalid_items:
            return jsonify({
                "success": False,
                "invalid_items": invalid_items,
                "message": "Some items have quantities exceeding their available stock."
            })

        # Store selected item IDs in session for checkout
        session['checkout_items'] = selected_item_ids
        return jsonify({"success": True, "redirect": url_for('checkout')})

    finally:
        cur.close()


#============================================== Add to cart ========================================================================
@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' in session:
        user_id = session['user_id']
        quantity_to_add = int(request.form.get('quantity', 1))  # Get the quantity from the form

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if the product is already in the cart for the user
        cur.execute("SELECT * FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        existing_cart_item = cur.fetchone()

        if existing_cart_item:
            # Product already exists in the cart, update the quantity
            new_quantity = existing_cart_item['quantity'] + quantity_to_add
            cur.execute("UPDATE cart SET quantity = %s WHERE cart_id = %s", (new_quantity, existing_cart_item['cart_id']))
        else:
            # Product is not in the cart, insert a new entry
            cur.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity_to_add))

        mysql.connection.commit()
        cur.close()

        flash('Product added to cart successfully!', 'success')
        return redirect(url_for('cart'))
    else:
        return redirect(url_for('login'))


@app.route('/delete_item/<int:cart_id>', methods=['POST'])
def delete_item(cart_id):
    if 'user_id' not in session:
        return jsonify(success=False, message="User not logged in"), 403

    user_id = session['user_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Delete the item from the cart
    cur.execute("DELETE FROM cart WHERE cart_id = %s AND user_id = %s", (cart_id, user_id))
    mysql.connection.commit()
    cur.close()

    if cur.rowcount > 0:
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Item not found or delete failed"), 400

@app.route('/update_quantity/<int:cart_id>', methods=['POST'])
def update_quantity(cart_id):
    if 'user_id' not in session:
        return jsonify(success=False, message="User not logged in"), 403

    user_id = session['user_id']
    data = request.get_json()
    new_quantity = data.get('quantity', 1)

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Update the quantity in the cart
    cur.execute(
        "UPDATE cart SET quantity = %s WHERE cart_id = %s AND user_id = %s",
        (new_quantity, cart_id, user_id)
    )
    mysql.connection.commit()

    # Fetch the updated total price for the item
    cur.execute("""
        SELECT (cart.quantity * products.price) AS total_price 
        FROM cart 
        JOIN products ON cart.product_id = products.product_id 
        WHERE cart.cart_id = %s AND cart.user_id = %s
    """, (cart_id, user_id))
    result = cur.fetchone()
    cur.close()

    if result:
        return jsonify(success=True, new_total_price=result['total_price'])
    else:
        return jsonify(success=False, message="Item not found or update failed"), 400

#=================================================PRODUCT VIEWS =====================================================
# book products view
@app.route('/book-products')
def books_products():
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        subcategory = request.args.get('subcategory')

        if subcategory:
            # Use LIKE operator for partial matching
            cur.execute(
                "SELECT * FROM products WHERE category = %s AND subcategory LIKE %s AND archived = 0",
                ('books', f"%{subcategory}%")
            )
        else:
            cur.execute("SELECT * FROM products WHERE category = %s AND archived = 0", ('books',))
        products = cur.fetchall()

        cur.execute("SELECT DISTINCT subcategory FROM products WHERE category = %s AND archived = 0", ('books',))
        subcategories = cur.fetchall()
        cur.close()

        return render_template('book-products.html', products=products, subcategories=subcategories)
    else:
        return redirect(url_for('login'))


@app.route('/game-products')
def games_products():
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        subcategory = request.args.get('subcategory')

        if subcategory:
            # Use LIKE operator for partial matching
            cur.execute(
                "SELECT * FROM products WHERE category = %s AND subcategory LIKE %s AND archived = 0",
                ('games', f"%{subcategory}%")
            )
        else:
            cur.execute("SELECT * FROM products WHERE category = %s AND archived = 0", ('games',))
        products = cur.fetchall()

        cur.execute("SELECT DISTINCT subcategory FROM products WHERE category = %s AND archived = 0", ('games',))
        subcategories = cur.fetchall()
        cur.close()

        return render_template('game-products.html', products=products, subcategories=subcategories)
    else:
        return redirect(url_for('login'))

    
# Movie products view
@app.route('/movie-products')
def movie_products():
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        subcategory = request.args.get('subcategory')

        if subcategory:
            # Use LIKE operator for partial matching
            cur.execute(
                "SELECT * FROM products WHERE category = %s AND subcategory LIKE %s AND archived = 0",
                ('movies', f"%{subcategory}%")
            )
        else:
            cur.execute("SELECT * FROM products WHERE category = %s AND archived = 0", ('movies',))
        products = cur.fetchall()

        cur.execute("SELECT DISTINCT subcategory FROM products WHERE category = %s AND archived = 0", ('movies',))
        subcategories = cur.fetchall()
        cur.close()

        return render_template('movie-products.html', products=products, subcategories=subcategories)
    else:
        return redirect(url_for('login'))
    
#======================================================checkout====================================================================


@app.route('/checkout', methods=['GET'])
def checkout():
    if 'checkout_items' not in session or not session['checkout_items']:
        flash('No items selected for checkout.', 'error')
        return redirect(url_for('cart'))

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Fetch user details
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            flash('User not found. Please log in again.', 'error')
            return redirect(url_for('login'))

        # Fetch additional addresses
        cur.execute("SELECT * FROM new_addresses WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        new_addresses = cur.fetchall()

        # Fetch cart items
        selected_item_ids = session['checkout_items']
        if not selected_item_ids:
            flash('No items selected for checkout.', 'error')
            return redirect(url_for('cart'))

        placeholders = ', '.join(['%s'] * len(selected_item_ids))
        query = f"""
        SELECT cart.cart_id, cart.quantity, 
               (cart.quantity * products.price) AS total_price, 
               products.product_name, products.price, products.category, 
               products.image_path, products.seller_id, sellers.store_name 
        FROM cart 
        JOIN products ON cart.product_id = products.product_id 
        JOIN sellers ON products.seller_id = sellers.seller_id
        WHERE cart.cart_id IN ({placeholders}) AND cart.user_id = %s
        """
        cur.execute(query, selected_item_ids + [user_id])
        checkout_items = cur.fetchall()

        if not checkout_items:
            flash('Selected items could not be found.', 'error')
            return redirect(url_for('cart'))

        # Calculate total price
        total_price = sum(item['total_price'] for item in checkout_items)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
        return redirect(url_for('cart'))

    finally:
        cur.close()

    # Render the checkout page
    return render_template(
        'checkout.html', 
        user=user, 
        new_addresses=new_addresses, 
        cart_items=checkout_items, 
        total_price=total_price
    )


#===DONT DELETE===
# @app.route('/checkoutPost', methods=['POST'])
# def checkoutPost():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     user_id = session['user_id']
#     cart_items = request.form.getlist('cart_ids[]')

#     if not cart_items:
#         flash('No items selected for checkout.', 'error')
#         return redirect(url_for('cart'))

#     placeholders = ', '.join(['%s'] * len(cart_items))
#     delivery_fee = Decimal(60.00)

#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Get voucher code and fetch details if provided
#     voucher_code = request.form.get('voucher')
#     voucher = None
#     if voucher_code:
#         cur.execute(
#             "SELECT * FROM vouchers WHERE voucher_code = %s",
#             (voucher_code,)
#         )
#         voucher = cur.fetchone()
#         if not voucher:
#             flash('Invalid or non-existing voucher.', 'error')
#             return redirect(url_for('checkout'))

#     # Fetch cart items with product details
#     query = f"""
#     SELECT cart.*, products.category, products.product_name, products.price, 
#            products.image_path, products.seller_id, products.stocks, 
#            (cart.quantity * products.price) AS total_price 
#     FROM cart 
#     JOIN products ON cart.product_id = products.product_id 
#     WHERE cart.cart_id IN ({placeholders}) AND cart.user_id = %s
#     """
#     cur.execute(query, cart_items + [user_id])
#     checkout_items = cur.fetchall()

#     if not checkout_items:
#         flash('No valid items found in your cart.', 'error')
#         return redirect(url_for('cart'))

#     total_price = Decimal(0)
#     applicable = False

#     for item in checkout_items:
#         item_total = Decimal(item['total_price'])

#         # Apply voucher discount if applicable
#         if voucher and voucher['category'].lower() == item['category'].lower():
#             applicable = True
#             discount = Decimal(voucher['discount']) / 100
#             item_total *= (1 - discount)

#         total_price += item_total

#         # Check stock availability
#         if item['quantity'] > item['stocks']:
#             flash(f"Not enough stock for {item['product_name']}.", 'danger')
#             return redirect(url_for('cart'))

#         # Insert the order into the database with order_status as 'pending'
#         try:
#             cur.execute(
#                 '''
#                 INSERT INTO orders (user_id, product_id, seller_id, order_status, quantity, total_price)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#                 ''',
#                 (user_id, item['product_id'], item['seller_id'], 'pending', item['quantity'], item_total)
#             )
#             print("Order inserted for product_id:", item['product_id'])
#         except Exception as e:
#             print("Error inserting into orders:", str(e))
#             flash(f"Error placing order for {item['product_name']}.", 'danger')
#             return redirect(url_for('cart'))

#         # Update product stock
#         try:
#             new_stock = item['stocks'] - item['quantity']
#             cur.execute(
#                 "UPDATE products SET stocks = %s WHERE product_id = %s",
#                 (new_stock, item['product_id'])
#             )
#             print("Stock updated for product_id:", item['product_id'])
#         except Exception as e:
#             print("Error updating stock for product_id:", item['product_id'], str(e))
#             flash("Error updating product stock.", 'danger')
#             return redirect(url_for('cart'))

#     # Add delivery fee to the total price
#     total_price += delivery_fee

#     # Notify if voucher was not applicable
#     if voucher and not applicable:
#         flash('Voucher not applicable. No matching items for the selected category.', 'warning')

#     # Clear the cart
#     try:
#         cur.execute(
#             f"DELETE FROM cart WHERE cart_id IN ({placeholders}) AND user_id = %s",
#             cart_items + [user_id]
#         )
#         print("Cart cleared for user_id:", user_id)
#     except Exception as e:
#         print("Error clearing cart:", str(e))
#         flash("Error clearing the cart.", 'danger')
#         return redirect(url_for('cart'))

#     mysql.connection.commit()
#     cur.close()

#     flash(f'Order placed successfully! Total paid: ₱{total_price}', 'success')
#     return redirect(url_for('orders_ship'))

@app.route('/checkoutPost', methods=['POST'])
def checkoutPost():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = request.form.getlist('cart_ids[]')

    if not cart_items:
        flash('No items selected for checkout.', 'error')
        return redirect(url_for('cart'))

    # Retrieve the delivery address selected by the user
    delivery_address = request.form.get('address')
    if not delivery_address:
        flash('No delivery address selected.', 'error')
        return redirect(url_for('checkout'))

    placeholders = ', '.join(['%s'] * len(cart_items))
    delivery_fee = Decimal(60.00)

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get voucher code and fetch details if provided
    voucher_code = request.form.get('voucher')
    voucher = None
    if voucher_code:
        cur.execute(
            "SELECT * FROM vouchers WHERE voucher_code = %s",
            (voucher_code,)
        )
        voucher = cur.fetchone()
        if not voucher:
            flash('Invalid or non-existing voucher.', 'error')
            return redirect(url_for('checkout'))

    # Fetch cart items with product details
    query = f"""
    SELECT cart.*, products.category, products.product_name, products.price, 
           products.image_path, products.seller_id, products.stocks, 
           (cart.quantity * products.price) AS total_price 
    FROM cart 
    JOIN products ON cart.product_id = products.product_id 
    WHERE cart.cart_id IN ({placeholders}) AND cart.user_id = %s
    """
    cur.execute(query, cart_items + [user_id])
    checkout_items = cur.fetchall()

    if not checkout_items:
        flash('No valid items found in your cart.', 'error')
        return redirect(url_for('cart'))

    total_price = Decimal(0)
    applicable = False

    for item in checkout_items:
        item_total = Decimal(item['total_price'])

        # Apply voucher discount if applicable
        if voucher and voucher['category'].lower() == item['category'].lower():
            applicable = True
            discount = Decimal(voucher['discount']) / 100
            item_total *= (1 - discount)

        total_price += item_total

        # Check stock availability
        if item['quantity'] > item['stocks']:
            flash(f"Not enough stock for {item['product_name']}.", 'danger')
            return redirect(url_for('cart'))

        # Insert the order into the database with delivery_address included
        try:
            cur.execute(
                '''
                INSERT INTO orders (user_id, product_id, seller_id, order_status, quantity, total_price, delivery_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''',
                (user_id, item['product_id'], item['seller_id'], 'pending', item['quantity'], item_total, delivery_address)
            )
            print("Order inserted for product_id:", item['product_id'])
        except Exception as e:
            print("Error inserting into orders:", str(e))
            flash(f"Error placing order for {item['product_name']}.", 'danger')
            return redirect(url_for('cart'))

        # Update product stock
        try:
            new_stock = item['stocks'] - item['quantity']
            cur.execute(
                "UPDATE products SET stocks = %s WHERE product_id = %s",
                (new_stock, item['product_id'])
            )
            print("Stock updated for product_id:", item['product_id'])
        except Exception as e:
            print("Error updating stock for product_id:", item['product_id'], str(e))
            flash("Error updating product stock.", 'danger')
            return redirect(url_for('cart'))

    # Add delivery fee to the total price
    total_price += delivery_fee

    # Notify if voucher was not applicable
    if voucher and not applicable:
        flash('Voucher not applicable. No matching items for the selected category.', 'warning')

    # Clear the cart
    try:
        cur.execute(
            f"DELETE FROM cart WHERE cart_id IN ({placeholders}) AND user_id = %s",
            cart_items + [user_id]
        )
        print("Cart cleared for user_id:", user_id)
    except Exception as e:
        print("Error clearing cart:", str(e))
        flash("Error clearing the cart.", 'danger')
        return redirect(url_for('cart'))

    mysql.connection.commit()
    cur.close()

    flash(f'Order placed successfully! Total paid: ₱{total_price}', 'success')
    return redirect(url_for('orders_ship'))


@app.route('/get_vouchers', methods=['GET'])
def get_vouchers():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM vouchers")
        vouchers = cur.fetchall()
        cur.close()
        return jsonify(vouchers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#==========================================seller-shipping center======================================================================

@app.route('/seller-shipping-center', methods=['GET'])
def seller_shipping_center():
    if 'seller_id' in session and session['role'] == 'seller':
        seller_id = session['seller_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch orders for this seller ordered by latest first
        cur.execute('''
            SELECT orders.order_id, products.product_name, users.first_name, users.last_name, users.email, 
                   orders.quantity, orders.order_status, orders.reason, orders.additional_reason, orders.created_at
            FROM orders 
            JOIN products ON orders.product_id = products.product_id 
            JOIN users ON orders.user_id = users.user_id 
            WHERE products.seller_id = %s
            ORDER BY orders.created_at DESC
        ''', (seller_id,))
        orders = cur.fetchall()
        cur.close()

        return render_template('seller-shipping-center.html', orders=orders)
    else:
        return redirect(url_for('login'))


#=============================================== Update order======================================================================
def send_email_to_buyer(subject, recipient_email, body):
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/update-order-status/<int:order_id>/<string:status>', methods=['POST'])
def update_order_status(order_id, status):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    reason = request.form.get('reason')
    additional_reason = request.form.get('additional_reason')

    redirect_url = ''  # Initialize redirect_url to prevent UnboundLocalError

    # Seller's status update logic
    if 'seller_id' in session and session['role'] == 'seller':
        valid_statuses = ['approved', 'cancelled', 'on_the_way', 'completed', 'refund_approved', 'refund_denied', 'return_picked_up']
        if status in valid_statuses:
            try:
                if status == 'refund_approved':
                    cur.execute(
                        """
                        UPDATE orders 
                        SET order_status = 'refund_approved', reason = %s, additional_reason = %s 
                        WHERE order_id = %s AND seller_id = %s
                        """,
                        (reason, additional_reason, order_id, session['seller_id'])
                    )
                    flash('Refund approved! Order marked as returned/refunded.', 'success')
                    # Send email to buyer
                    cur.execute("SELECT email FROM users WHERE user_id = (SELECT user_id FROM orders WHERE order_id = %s)", (order_id,))
                    buyer_email = cur.fetchone()['email']
                    send_email_to_buyer(
                        "Refund Approved",
                        buyer_email,
                        f"Your refund request for Order ID {order_id} has been approved. The order has been marked as refunded. Reason: {reason}"
                    )
                elif status == 'refund_denied':
                    cur.execute(
                        """
                        UPDATE orders 
                        SET order_status = 'on_the_way', reason = %s, additional_reason = %s 
                        WHERE order_id = %s AND seller_id = %s
                        """,
                        (reason, additional_reason, order_id, session['seller_id'])
                    )
                    flash('Refund denied! Order is on the way.', 'success')
                    # Send email to buyer
                    cur.execute("SELECT email FROM users WHERE user_id = (SELECT user_id FROM orders WHERE order_id = %s)", (order_id,))
                    buyer_email = cur.fetchone()['email']
                    send_email_to_buyer(
                        "Refund Denied",
                        buyer_email,
                        f"Your refund request for Order ID {order_id} has been denied. The order is on the way. Reason: {reason}"
                    )

                elif status == 'cancel_requested':
                    cur.execute(
                        """
                        UPDATE orders 
                        SET order_status = 'cancel_requested', reason = %s, additional_reason = %s 
                        WHERE order_id = %s AND seller_id = %s
                        """,
                        (reason, additional_reason, order_id, session['seller_id'])
                    )
                    flash('Cancellation requested.', 'warning')
                    # Send email to buyer
                    cur.execute("SELECT email FROM users WHERE user_id = (SELECT user_id FROM orders WHERE order_id = %s)", (order_id,))
                    buyer_email = cur.fetchone()['email']
                    send_email_to_buyer(
                        "Cancellation Requested",
                        buyer_email,
                        f"Your cancellation request for Order ID {order_id} has been received. Reason: {reason}"
                    )
                else:
                    cur.execute(
                        """
                        UPDATE orders 
                        SET order_status = %s, reason = %s, additional_reason = %s 
                        WHERE order_id = %s AND seller_id = %s
                        """,
                        (status, reason, additional_reason, order_id, session['seller_id'])
                    )
                    flash(f'Order status updated to {status}.', 'success')
                    # Send email to buyer
                    cur.execute("SELECT email FROM users WHERE user_id = (SELECT user_id FROM orders WHERE order_id = %s)", (order_id,))
                    buyer_email = cur.fetchone()['email']
                    send_email_to_buyer(
                        f"Order Status Updated to {status}",
                        buyer_email,
                        f"Your order (Order ID: {order_id}) status has been updated to {status}. Reason: {reason}"
                    )

                mysql.connection.commit()

            except Exception as e:
                mysql.connection.rollback()
                flash('Error updating order status.', 'danger')
                print(e)
            finally:
                cur.close()

            redirect_url = 'seller_shipping_center'  # Set redirect URL to seller shipping center after update
        else:
            flash('Invalid status update attempt.', 'danger')
            redirect_url = 'seller_shipping_center'  # Redirect to seller shipping center in case of invalid status

    # Buyer's status update logic (in case the buyer updates order status)
    elif 'user_id' in session and session['role'] == 'buyer':
        valid_buyer_statuses = ['delivered', 'refund_requested', 'cancel_requested']
        if status in valid_buyer_statuses:
            try:
                cur.execute(
                    """
                    UPDATE orders 
                    SET order_status = %s, reason = %s, additional_reason = %s 
                    WHERE order_id = %s AND user_id = %s
                    """,
                    (status, reason, additional_reason, order_id, session['user_id'])
                )
                mysql.connection.commit()

                if status == 'delivered':
                    flash('Delivery confirmed!', 'success')
                elif status == 'refund_requested':
                    flash(f'Refund request sent with reason: {reason}.', 'warning')
                elif status == 'cancel_requested':
                    flash(f'Cancellation request sent with reason: {reason}.', 'warning')

                # Send email to seller about buyer's status update
                cur.execute("SELECT email FROM users WHERE user_id = (SELECT seller_id FROM orders WHERE order_id = %s)", (order_id,))
                seller_email = cur.fetchone()['email']
                send_email_to_buyer(
                    f"Buyer updated order status to {status}",
                    seller_email,
                    f"The buyer has updated the order (Order ID: {order_id}) status to {status}. Reason: {reason}"
                )

            except Exception as e:
                mysql.connection.rollback()
                flash('Error updating order status.', 'danger')
                print(e)
            finally:
                cur.close()

            redirect_url = 'user_orders'  # Redirect to user orders page after status update
        else:
            flash('Invalid status update attempt.', 'danger')
            redirect_url = 'user_orders'  # Redirect to user orders in case of invalid status

    return redirect(url_for(redirect_url))




@app.route('/approve-cancel/<int:order_id>', methods=['POST'])
def approve_cancel(order_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'seller_id' in session and session['role'] == 'seller':
        try:
            cur.execute(
                "UPDATE orders SET order_status = 'cancelled' WHERE order_id = %s AND seller_id = %s",
                (order_id, session['seller_id'])
            )
            mysql.connection.commit()
            flash('Cancellation approved.', 'success')

            # Send email to buyer
            cur.execute("SELECT email FROM users WHERE user_id = (SELECT user_id FROM orders WHERE order_id = %s)", (order_id,))
            buyer_email = cur.fetchone()['email']
            send_email_to_buyer(
                "Order Cancelled",
                buyer_email,
                f"Your order (Order ID: {order_id}) has been cancelled as per your request."
            )
        except Exception as e:
            mysql.connection.rollback()
            flash('Error approving cancellation.', 'danger')
            print(e)
        finally:
            cur.close()
    return redirect(url_for('seller_shipping_center'))


@app.route('/deny-cancel/<int:order_id>', methods=['POST'])
def deny_cancel(order_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    reason = request.form.get('reason')
    additional_reason = request.form.get('additional_reason', '')

    if 'seller_id' in session and session['role'] == 'seller':
        try:
            cur.execute(
                """
                UPDATE orders 
                SET order_status = 'on_the_way', reason = %s, additional_reason = %s
                WHERE order_id = %s AND seller_id = %s
                """,
                (reason, additional_reason, order_id, session['seller_id'])
            )
            mysql.connection.commit()
            flash('Cancellation denied! Order is on the way.', 'danger')

            # Send email to buyer
            cur.execute("SELECT email FROM users WHERE user_id = (SELECT user_id FROM orders WHERE order_id = %s)", (order_id,))
            buyer_email = cur.fetchone()['email']
            send_email_to_buyer(
                "Order Cancellation Denied",
                buyer_email,
                f"Your order (Order ID: {order_id}) cancellation request has been denied. The order is on its way. Reason: {reason} {additional_reason}"
            )
        except Exception as e:
            mysql.connection.rollback()
            flash('Error denying cancellation.', 'danger')
            print(e)
        finally:
            cur.close()
    return redirect(url_for('seller_shipping_center'))



# ===========================================puorchases-rders routes==============================================================
@app.route('/user-orders')
def user_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT orders.order_id, orders.quantity, orders.total_price, orders.order_status, 
               products.product_name, products.image_path, orders.created_at
        FROM orders
        JOIN products ON orders.product_id = products.product_id
        WHERE orders.user_id = %s
        ORDER BY orders.created_at DESC
    """, (user_id,))
    orders = cur.fetchall()

    # Map statuses to human-readable labels
    status_mapping = {
        'pending': 'Pending Approval',
        'approved': 'For Delivery',
        'on_the_way': 'Parcel on Delivery',
        'delivered': 'Delivered',
        'cancel_requested': 'Order Cancellation Requested',
        'cancelled': 'Order Canceled',
        'refund_requested': 'Refund Requested',
        'refund_approved': 'Refund Approved',
        'refund_denied': 'Refund Denied',
        'returned/refunded': 'Order Returned/Refunded'
    }

    for order in orders:
        order['status_label'] = status_mapping.get(order['order_status'], 'Unknown Status')
    
    cur.close()
    return render_template('user-orders.html', orders=orders)


# Seller marks the order as 'on the way'
@app.route('/ship-order/<int:order_id>', methods=['POST'])
def ship_order(order_id):
    if 'user_id' in session and session['role'] == 'seller':
        cur = mysql.connection.cursor()
        try:
            # Check if the order exists
            cur.execute("SELECT order_status FROM orders WHERE order_id = %s", (order_id,))
            order = cur.fetchone()

            if order:
                print(f"Current order status: {order[0]}")
                
                # Check if the order status is 'approved'
                if order[0] == 'approved':
                    # Update the order status to 'on_the_way'
                    cur.execute("UPDATE orders SET order_status = 'on_the_way' WHERE order_id = %s", (order_id,))
                    mysql.connection.commit() 
                    flash('Order marked as on the way!', 'success')
                    print(f"Order {order_id} marked as 'on the way'")
                else:
                    flash('Order must be approved before it can be marked as on the way.', 'warning')
                    print(f"Order status is not 'approved'. Current status: {order[0]}")
            else:
                flash('Order not found.', 'danger')
                print(f"Order {order_id} not found in the database.")

        except Exception as e:
            mysql.connection.rollback()  # Rollback if there's an error
            flash('Error updating shipping status.', 'danger')
            print(f"Error updating order {order_id}: {e}")
        finally:
            cur.close()

    return redirect(url_for('seller_shipping_center'))

# Seller marks the order as complete
@app.route('/complete-order/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Ensure the seller can only complete their own orders
    if 'seller_id' in session and session['role'] == 'seller':
        try:
            cur.execute(
                "UPDATE orders SET order_status = 'completed' WHERE order_id = %s AND seller_id = %s",
                (order_id, session['seller_id'])
            )
            mysql.connection.commit()
            flash('Order marked as completed.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash('Error completing the order.', 'danger')
            print(e)
        finally:
            cur.close()
    
    return redirect(url_for('seller_shipping_center'))

# Buyer requests an order cancellation
# @app.route('/cancel-order/<int:order_id>', methods=['POST'])
# def cancel_order(order_id):
    if 'user_id' in session and session['role'] == 'buyer':
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE orders SET order_status = 'cancel_requested' WHERE order_id = %s", (order_id,))
            mysql.connection.commit()
            flash('Cancellation request has been sent!', 'warning')
        except Exception as e:
            flash('Error requesting cancellation.', 'danger')
            print(e)
        finally:
            cur.close()

    return redirect(url_for('order_cancelled'))

@app.route('/cancel-order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'user_id' in session and session['role'] == 'buyer':
        reason = request.form.get('reason')  # Get the selected reason
        additional_reason = request.form.get('additional_reason', '').strip()  # Get the additional reason (if any)

        cur = mysql.connection.cursor()
        try:
            # Update the order status and include the cancellation reason
            cur.execute('''
                UPDATE orders 
                SET order_status = 'cancel_requested', 
                    reason = %s, 
                    additional_reason = %s 
                WHERE order_id = %s
            ''', (reason, additional_reason, order_id))
            mysql.connection.commit()
            flash('Cancellation request has been sent with your reason!', 'warning')
        except Exception as e:
            flash('Error requesting cancellation.', 'danger')
            print(f"Error: {e}")
        finally:
            cur.close()

    return redirect(url_for('order_cancelled'))


#==================================================== Orders Display Routes ======================================================
# Route to display orders that are approved and ready to ship
@app.route('/orders-ship', methods=['GET'])
def orders_ship():
    if 'user_id' in session and session['role'] == 'buyer':
        user_id = session['user_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch orders with 'pending' or 'approved' status for the buyer
        cur.execute('''
            SELECT * FROM orders
            JOIN products ON orders.product_id = products.product_id
            WHERE orders.user_id = %s AND (orders.order_status = 'pending' OR orders.order_status = 'approved')
                                ORDER BY orders.updated_at DESC

        ''', (user_id,))
        orders = cur.fetchall()

        # Map statuses to human-readable labels
        status_mapping = {
            'pending': 'Pending Approval',
            'approved': 'For Delivery',
            'on_the_way': 'Parcel on Delivery',
            'delivered': 'Delivered',
            'cancel_requested': 'Order Cancellation Requested',
            'cancelled': 'Order Canceled',
            'refund_requested': 'Refund Requested',
            'refund_approved': 'Refund Approved',
            'refund_denied': 'Refund Denied',
            'returned/refunded': 'Order Returned/Refunded'
        }

        for order in orders:
            order['status_label'] = status_mapping.get(order['order_status'], 'Unknown Status')

        # Close the cursor after the loop
        cur.close()

        return render_template('orders-ship.html', orders=orders)
    else:
        return redirect(url_for('login'))


@app.route('/orders-receive', methods=['GET'])
def orders_receive():
    if 'user_id' in session and session['role'] == 'buyer':
        user_id = session['user_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch orders with 'on_the_way' status for the buyer
        cur.execute('''
            SELECT * FROM orders
            JOIN products ON orders.product_id = products.product_id
            WHERE orders.user_id = %s AND orders.order_status = 'on_the_way'
                                ORDER BY orders.updated_at DESC

        ''', (user_id,))
        orders = cur.fetchall()  # Ensure this fetches valid data
        cur.close()

        # Map statuses to human-readable labels
        status_mapping = {
            'pending': 'Pending Approval',
            'approved': 'For Delivery',
            'on_the_way': 'Parcel on Delivery',
            'delivered': 'Delivered',
            'cancel_requested': 'Order Cancellation Requested',
            'cancelled': 'Order Canceled',
            'refund_requested': 'Refund Requested',
            'refund_approved': 'Refund Approved',
            'refund_denied': 'Refund Denied',
            'returned/refunded': 'Order Returned/Refunded'
        }

        # Add status labels to each order
        for order in orders:
            order['status_label'] = status_mapping.get(order['order_status'], 'Unknown Status')

        return render_template('orders-receive.html', orders=orders)
    
    # Redirect if the user is not logged in or is not a buyer
    return redirect(url_for('login'))




# Route to display completed orders for the seller
@app.route('/orders-completed')
def order_complete():
    if 'user_id' in session and session['role'] == 'buyer':
        seller_id = session['user_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            '''SELECT * FROM orders 
               JOIN products ON orders.product_id = products.product_id 
               WHERE orders.user_id = %s AND orders.order_status = 'completed' OR orders.order_status = 'delivered' ORDER BY orders.updated_at DESC

            ''', (seller_id,))
        orders = cur.fetchall()
        cur.close()
        return render_template('orders-completed.html', orders=orders)
    return redirect(url_for('login'))

# Route to display canceled orders
@app.route('/orders-cancelled')
def order_cancelled():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch orders with 'cancelled' or 'cancel_requested' status
        cur.execute('''
            SELECT * FROM orders
            JOIN products ON orders.product_id = products.product_id
            WHERE orders.user_id = %s AND (orders.order_status = 'cancelled' OR orders.order_status = 'cancel_requested')
            ORDER BY orders.updated_at DESC
        ''', (user_id,))
        orders = cur.fetchall()
        cur.close()

        # Map statuses to human-readable labels
        status_mapping = {
            'pending': 'Pending Approval',
            'approved': 'For Delivery',
            'on_the_way': 'Parcel on Delivery',
            'delivered': 'Delivered',
            'cancel_requested': 'Order Cancellation Requested',
            'cancelled': 'Order Cancelled',
            'refund_requested': 'Refund Requested',
            'refund_approved': 'Refund Approved',
            'refund_denied': 'Refund Denied',
            'returned/refunded': 'Order Returned/Refunded'
        }

        # Add status labels to each order
        for order in orders:
            order['status_label'] = status_mapping.get(order['order_status'], 'Unknown Status')

        return render_template('orders-cancelled.html', orders=orders)

    # Redirect to login if the user is not authenticated
    return redirect(url_for('login'))


#=================================REFUND LOGIC CODE=======================================================================================
# Buyer requests a refund
@app.route('/request_refund/<int:order_id>', methods=['POST'])
def request_refund(order_id):
    if 'user_id' in session and session['role'] == 'buyer':
        # Fetch the reason and additional reason from the form
        reason = request.form.get('reason')
        additional_reason = request.form.get('additional_reason', '').strip()

        # Update the order with refund_requested status and reasons
        cur = mysql.connection.cursor()
        try:
            cur.execute('''
                UPDATE orders 
                SET order_status = 'refund_requested', 
                    reason = %s, 
                    additional_reason = %s 
                WHERE order_id = %s
            ''', (reason, additional_reason, order_id))
            mysql.connection.commit()
            flash('Refund request submitted successfully!', 'info')
        except Exception as e:
            flash('Error processing refund request.', 'danger')
            print(f"Error: {e}")
        finally:
            cur.close()

    return redirect(url_for('order_refund'))


# Seller approves or denies refund
@app.route('/approve-refund/<int:order_id>', methods=['POST'])
def approve_refund(order_id):
    if 'user_id' in session and session['role'] == 'seller':
        cur = mysql.connection.cursor()
        try:
            # Update the order status to 'refund_approved'
            cur.execute("UPDATE orders SET order_status = 'refund_approved' WHERE order_id = %s AND seller_id = %s", 
                        (order_id, session['user_id']))
            mysql.connection.commit()
            flash('Refund has been approved.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash('Error approving the refund.', 'danger')
            print(e)
        finally:
            cur.close()

    return redirect(url_for('seller_shipping_center'))

@app.route('/deny-refund/<int:order_id>', methods=['POST'])
def deny_refund(order_id):
    if 'user_id' in session and session['role'] == 'seller':
        cur = mysql.connection.cursor()
        try:
            # Update the order status to 'refund_denied'
            cur.execute("UPDATE orders SET order_status = 'on_the_way' WHERE order_id = %s AND seller_id = %s", 
                        (order_id, session['user_id']))
            mysql.connection.commit()
            flash('Refund request has been denied.', 'danger')
        except Exception as e:
            mysql.connection.rollback()
            flash('Error denying the refund.', 'danger')
            print(e)
        finally:
            cur.close()

    return redirect(url_for('seller_shipping_center'))


@app.route('/orders-refund')
def order_refund():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            '''SELECT * FROM orders 
               JOIN products ON orders.product_id = products.product_id 
               WHERE orders.user_id = %s AND orders.order_status = 'returned/refunded' OR orders.order_status = 'refund_requested'
               ORDER BY orders.order_id DESC''', (user_id,))
        orders = cur.fetchall()
        cur.close()
        return render_template('orders-refund.html', orders=orders)
    return redirect(url_for('login'))


#========================================================== SALES REPORT ==================================================================
def execute_query(query, params=None):
    """Helper function to execute SQL queries with error handling."""
    conn = mysql.connection
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()


def sanitize_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# @app.route('/download-sales-report')
# def download_sales_report():
    """Generate and download the seller's sales report as a PDF."""
    if 'seller_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    seller_id = session['seller_id']

    # Fetch sales data and store name for the seller (excluding stocks and order_date)
    sales_data = execute_query('''
        SELECT o.order_id, p.product_name, o.quantity, o.total_price, 
               ROUND(o.total_price - (o.total_price * 0.05), 2) AS net_profit,
               s.store_name
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN sellers s ON p.seller_id = s.seller_id  -- Assuming the sellers table stores the store name
        WHERE p.seller_id = %s AND o.order_status = 'completed'
        ORDER BY o.order_id DESC
    ''', (seller_id,))

    # Ensure sales_data is not None
    if not sales_data:
        sales_data = [] 

    # Debug: Print sales data to see if anything was returned
    print(sales_data)

    # Initialize PDF (A4 paper size in mm: 210 x 297)
    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Sales Report", ln=True, align='C')
    pdf.ln(10)  # Line break

    # Store Name and Date
    store_name = sales_data[0]['store_name'] if sales_data else "Unknown Store"
    current_date = datetime.now().strftime("%B %d, %Y")  # Current date in format: "Month day, Year"
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Store Name: {store_name}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Date Generated: {current_date}", ln=True, align='L')
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", style="B", size=12)
    headers = ['Order No', 'Product Name', 'Quantity Sold', 'Total Price', 'Net Profit']
    header_widths = [28, 75, 30, 30, 30]  # Adjusted widths
    for i, header in enumerate(headers):
        pdf.cell(header_widths[i], 10, txt=header, border=1, align='C')
    pdf.ln()

    # Variables for summation
    total_quantity = 0
    total_price = 0
    total_net_profit = 0

    # Table Content
    pdf.set_font("Arial", size=12)
    for row in sales_data:
        # Sanitize product name to remove non-latin characters
        product_name = sanitize_text(row['product_name'])

        # Print each row of the table
        pdf.cell(28, 10, txt=str(row['order_id']), border=1, align='C')
        pdf.cell(75, 10, txt=product_name, border=1, align='L')
        pdf.cell(30, 10, txt=str(row['quantity']), border=1, align='C')
        pdf.cell(30, 10, txt=f"Php {row['total_price']:.2f}", border=1, align='C')
        pdf.cell(30, 10, txt=f"Php {row['net_profit']:.2f}", border=1, align='C')
        pdf.ln()

        # Accumulate the totals for summation
        total_quantity += row['quantity']
        total_price += row['total_price']
        total_net_profit += row['net_profit']

    # Print the totals at the bottom of the table
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(28, 10, txt="Total", border=1, align='C')
    pdf.cell(75, 10, txt="", border=1)  # Empty cell for product name
    pdf.cell(30, 10, txt=str(total_quantity), border=1, align='C')
    pdf.cell(30, 10, txt=f"Php {total_price:.2f}", border=1, align='C')
    pdf.cell(30, 10, txt=f"Php {total_net_profit:.2f}", border=1, align='C')
    pdf.ln()

    # Serve the PDF
    response = Response(pdf.output(dest='S').encode('latin1'))  # PDF output as string with 'latin1' encoding
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=sales_report.pdf'
    return response

@app.route('/sales-report', methods=['GET', 'POST'])
def sales_report():
    """Render the sales report page with filtering by date."""
    if 'seller_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    seller_id = session['seller_id']

    # Initialize default values
    total_sales, net_profit, total_items_sold, total_stocks = 0, 0, 0, 0
    order_details = []

    # Get filter values from the request
    filter_type = request.args.get('filter_type', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Convert dates to proper format if provided
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    except ValueError:
        start_date, end_date = None, None
        print("Invalid date format received.")

    # Build date condition based on the filter type
    date_condition = ''
    params = [seller_id]
    if filter_type == 'today':
        date_condition = "AND DATE(o.updated_at) = CURDATE()"
    elif filter_type == 'this_week':
        date_condition = "AND YEARWEEK(o.updated_at, 1) = YEARWEEK(CURDATE(), 1)"
    elif filter_type == 'this_month':
        date_condition = "AND MONTH(o.updated_at) = MONTH(CURDATE()) AND YEAR(o.updated_at) = YEAR(CURDATE())"
    elif start_date and end_date:
        date_condition = "AND o.updated_at BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    # Fetch data from the database with filtering
    result_sales = execute_query(f'''
        SELECT SUM(o.total_price) AS total_sales
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE p.seller_id = %s AND o.order_status = 'completed' {date_condition}
    ''', params)
    total_sales = result_sales[0]['total_sales'] if result_sales and result_sales[0]['total_sales'] else 0

    result_profit = execute_query(f'''
        SELECT ROUND(SUM(o.total_price - (o.total_price * 0.05)), 2) AS net_profit
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE p.seller_id = %s AND o.order_status = 'completed' {date_condition}
    ''', params)
    net_profit = result_profit[0]['net_profit'] if result_profit and result_profit[0]['net_profit'] else 0

    result_items_sold = execute_query(f'''
        SELECT SUM(o.quantity) AS total_items_sold
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE p.seller_id = %s AND o.order_status = 'completed' {date_condition}
    ''', params)
    total_items_sold = result_items_sold[0]['total_items_sold'] if result_items_sold and result_items_sold[0]['total_items_sold'] else 0

    order_details = execute_query(f'''
        SELECT o.order_id, p.product_name, o.quantity, o.total_price,
               ROUND(o.total_price - (o.total_price * 0.05), 2) AS net_profit
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE p.seller_id = %s AND o.order_status = 'completed' {date_condition}
        ORDER BY o.order_id DESC
    ''', params)

    return render_template(
        'sales-report.html',
        total_sales=total_sales,
        net_profit=net_profit,
        total_items_sold=total_items_sold,
        total_stocks=total_stocks,
        order_details=order_details,
        filter_type=filter_type,
        start_date=start_date.isoformat() if start_date else '',
        end_date=end_date.isoformat() if end_date else ''
    )


@app.route('/download-sales-report')
def download_sales_report():
    """Generate and download the filtered sales report as a PDF."""
    if 'seller_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    seller_id = session['seller_id']

    # Get filter values from the request
    filter_type = request.args.get('filter_type', 'all')  # Default to 'all'
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Build date condition based on the filter type
    date_condition = ''
    params = [seller_id]
    if filter_type == 'today':
        date_condition = "AND DATE(o.updated_at) = CURDATE()"
    elif filter_type == 'this_week':
        date_condition = "AND YEARWEEK(o.updated_at, 1) = YEARWEEK(CURDATE(), 1)"
    elif filter_type == 'this_month':
        date_condition = "AND MONTH(o.updated_at) = MONTH(CURDATE()) AND YEAR(o.updated_at) = YEAR(CURDATE())"
    elif start_date and end_date:
        date_condition = "AND o.updated_at BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    # Fetch sales data from the database
    sales_data = execute_query(f'''
        SELECT o.order_id, p.product_name, o.quantity, o.total_price, 
               ROUND(o.total_price - (o.total_price * 0.05), 2) AS net_profit,
               s.store_name
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN sellers s ON p.seller_id = s.seller_id
        WHERE p.seller_id = %s AND o.order_status = 'completed' {date_condition}
        ORDER BY o.order_id DESC
    ''', params)

    # Ensure sales_data is not None
    if not sales_data:
        sales_data = []

    # Debug: Print sales data to verify it includes the filter
    print(sales_data)

    # Initialize PDF (A4 paper size: 210 x 297 mm)
    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Filtered Sales Report", ln=True, align='C')
    pdf.ln(10)

    # Store Name and Date
    store_name = sales_data[0]['store_name'] if sales_data else "Unknown Store"
    current_date = datetime.now().strftime("%B %d, %Y")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Store Name: {store_name}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Date Generated: {current_date}", ln=True, align='L')

    # Filter information
    filter_label = f"Filter: {filter_type.replace('_', ' ').capitalize()}"
    if filter_type == 'custom' and start_date and end_date:
        filter_label = f"Filter: Custom ({start_date} to {end_date})"
    pdf.cell(200, 10, txt=filter_label, ln=True, align='L')
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", style="B", size=12)
    headers = ['Order No', 'Product Name', 'Quantity Sold', 'Total Price', 'Net Profit']
    header_widths = [28, 75, 30, 30, 30]
    for i, header in enumerate(headers):
        pdf.cell(header_widths[i], 10, txt=header, border=1, align='C')
    pdf.ln()

    # Variables for summation
    total_quantity = 0
    total_price = 0
    total_net_profit = 0

    # Table Content
    pdf.set_font("Arial", size=11)
    for row in sales_data:
        product_name = sanitize_text(row['product_name'])

        pdf.cell(28, 10, txt=str(row['order_id']), border=1, align='C')
        pdf.cell(75, 10, txt=product_name, border=1, align='L')
        pdf.cell(30, 10, txt=str(row['quantity']), border=1, align='C')
        pdf.cell(30, 10, txt=f"Php {row['total_price']:.2f}", border=1, align='C')
        pdf.cell(30, 10, txt=f"Php {row['net_profit']:.2f}", border=1, align='C')
        pdf.ln()

        total_quantity += row['quantity']
        total_price += row['total_price']
        total_net_profit += row['net_profit']

    # Totals at the bottom
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(28, 10, txt="Total", border=1, align='C')
    pdf.cell(75, 10, txt="", border=1)  # Empty cell
    pdf.cell(30, 10, txt=str(total_quantity), border=1, align='C')
    pdf.cell(30, 10, txt=f"Php {total_price:.2f}", border=1, align='C')
    pdf.cell(30, 10, txt=f"Php {total_net_profit:.2f}", border=1, align='C')
    pdf.ln()

    # Serve the PDF
    response = Response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=filtered_sales_report.pdf'
    return response



#=====================================================  Update Seller account details ======================================================

# Route to render seller account settings page
@app.route('/seller-account')
def seller_account():
    if 'seller_id' in session:
        return render_template('seller-account.html')
    else:
        return redirect(url_for('login'))

# Update Email
@app.route('/seller_update_email', methods=['POST'])
def seller_update_email():
    if 'seller_id' in session:
        seller_id = session['seller_id']
        new_email = request.form['new_email']
        
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE sellers SET email = %s WHERE seller_id = %s', (new_email, seller_id))
        mysql.connection.commit()
        cursor.close()
        
        flash("Email updated successfully!", "success")
    return redirect(url_for('seller_account'))

# Route to update phone number
@app.route('/seller_update_phone', methods=['POST'])
def seller_update_phone():
    if 'seller_id' in session:
        seller_id = session['seller_id']
        new_phone = request.form['new_phone']
        
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE sellers SET contact_number = %s WHERE seller_id = %s', (new_phone, seller_id))
        mysql.connection.commit()
        cursor.close()
        
        flash("Phone number updated successfully!", "success")
    return redirect(url_for('seller_account'))

# Route to update password
@app.route('/seller_update_password', methods=['POST'])
def seller_update_password():
    if 'seller_id' in session:
        seller_id = session['seller_id']
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE sellers SET password = %s WHERE seller_id = %s', (hashed_password, seller_id))
        mysql.connection.commit()
        cursor.close()
        
        flash("Password updated successfully!")
    return redirect(url_for('seller_account'))
# Route to Update shop info
@app.route('/update_shop_info', methods=['POST'])
def update_shop_info():
    if 'seller_id' in session:
        seller_id = session['seller_id']
        shop_name = request.form['shop_name']
        store_description = request.form['store_description']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Corrected SQL syntax
        cursor.execute('UPDATE sellers SET store_name = %s, store_description = %s WHERE seller_id = %s', (shop_name, store_description, seller_id))
        mysql.connection.commit()
        cursor.close()
        
        flash("Shop information updated successfully!")
    return redirect(url_for('seller_account'))

# Route to update profile picture
@app.route('/update_seller_image', methods=['POST'])
def update_seller_image():
    if 'seller_id' in session:
        seller_id = session['seller_id']
        file = request.files['seller_image']  # Updated to 'seller_image' to match the form

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE sellers SET seller_image = %s WHERE seller_id = %s', (filename, seller_id))
            mysql.connection.commit()
            cursor.close()

            flash("Profile picture updated successfully!", "success")
        else:
            flash("Invalid file format. Please upload a PNG, JPG, or JPEG file.", "error")
    return redirect(url_for('seller_account'))

# Route to update seller ID
@app.route('/update_id', methods=['POST'])
def update_id():
    if 'seller_id' in session:
        seller_id = session['seller_id']
        file = request.files['seller_id_path']  # Ensures correct key for 'seller_id_path'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE sellers SET seller_id_path = %s WHERE seller_id = %s', (filename, seller_id))
            mysql.connection.commit()
            cursor.close()

            flash("ID updated successfully!", "success")  # Corrected flash message
        else:
            flash("Invalid file format. Please upload a PNG, JPG, JPEG, or PDF file.", "error")
    return redirect(url_for('seller_account'))

# Route to update seller Certificate
@app.route('/update_certificate', methods=['POST'])
def update_certificate():
    if 'seller_id' in session:
        seller_id = session['seller_id']
        file = request.files['seller_certificate_path']  # Correct key for 'seller_certificate_path'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE sellers SET seller_certificate_path = %s WHERE seller_id = %s', (filename, seller_id))
            mysql.connection.commit()
            cursor.close()

            flash("Certificate updated successfully!", "success")  # Corrected flash message
        else:
            flash("Invalid file format. Please upload a PNG, JPG, JPEG, or PDF file.", "error")
    return redirect(url_for('seller_account'))

#=============================================== Buyers-Homepage shop page =========================================================================

# Route for shop page to display seller information and products
@app.route('/shop/<int:seller_id>', methods=['GET'])
def shop_page(seller_id):
    # Connect to MySQL and create a cursor
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Query to get seller information
    cursor.execute('SELECT * FROM sellers WHERE seller_id = %s', (seller_id,))
    seller = cursor.fetchone()

    if not seller:
        flash('Seller not found', 'danger')
        return redirect(url_for('homepage'))

    # Query to get all products for this seller
    cursor.execute('SELECT * FROM products WHERE seller_id = %s', (seller_id,))
    products = cursor.fetchall()

    # Close the cursor
    cursor.close()

    # Render the template with seller and product data
    return render_template('store_page.html', seller=seller, products=products)

#========================== PER CATEGORY SEARCH =======================================
@app.route('/shop/<int:seller_id>/books', methods=['GET'])
def store_page_books(seller_id):
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the seller's details
        cur.execute("SELECT * FROM sellers WHERE seller_id = %s", (seller_id,))
        seller = cur.fetchone()

        if not seller:
            return "Seller not found", 404

        # Fetch the seller's products where category is 'books'
        cur.execute("""
            SELECT * 
            FROM products 
            WHERE seller_id = %s AND category = 'books' AND archived = 0
        """, (seller_id,))
        products = cur.fetchall()

        cur.close()

        # Render the store_page_books.html template
        return render_template(
            'store_page_books.html',
            seller=seller,
            products=products
        )
    else:
        return redirect(url_for('login'))
    
@app.route('/shop/<int:seller_id>/games', methods=['GET'])
def store_page_games(seller_id):
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the seller's details
        cur.execute("SELECT * FROM sellers WHERE seller_id = %s", (seller_id,))
        seller = cur.fetchone()

        if not seller:
            return "Seller not found", 404

        # Fetch the seller's products where category is 'books'
        cur.execute("""
            SELECT * 
            FROM products 
            WHERE seller_id = %s AND category = 'games' AND archived = 0
        """, (seller_id,))
        products = cur.fetchall()

        cur.close()

        # Render the store_page_books.html template
        return render_template(
            'store_page_games.html',
            seller=seller,
            products=products
        )
    else:
        return redirect(url_for('login'))

@app.route('/shop/<int:seller_id>/movies', methods=['GET'])
def store_page_movies(seller_id):
    if 'user_id' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the seller's details
        cur.execute("SELECT * FROM sellers WHERE seller_id = %s", (seller_id,))
        seller = cur.fetchone()

        if not seller:
            return "Seller not found", 404

        # Fetch the seller's products where category is 'books'
        cur.execute("""
            SELECT * 
            FROM products 
            WHERE seller_id = %s AND category = 'movies' AND archived = 0
        """, (seller_id,))
        products = cur.fetchall()

        cur.close()

        # Render the store_page_books.html template
        return render_template(
            'store_page_movies.html',
            seller=seller,
            products=products
        )
    else:
        return redirect(url_for('login'))

#=========================================================== CHAT FUNCTIONALITY =======================================================

@app.route('/chat-management')
def chat_management():
    if 'seller_id' not in session:  # Ensure the seller is logged in
        return redirect(url_for('login'))

    seller_id = session['seller_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor

    # Fetch inbox data for users
    cursor.execute("""
        SELECT 
            u.user_id, 
            u.email, 
            u.profile_image_url,
            COALESCE(
                (SELECT message FROM messages WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), '') as last_message,
            COALESCE(
                (SELECT timestamp FROM messages WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), NULL) as last_message_time,
            COALESCE(
                (SELECT seen_status FROM messages WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), 1) as seen_status
        FROM users u
        WHERE u.archived = 0 AND u.approved = 1
    """, (seller_id, seller_id, seller_id, seller_id, seller_id, seller_id))
    inbox = cursor.fetchall()

    # Process the profile image path
    for chat in inbox:
        if chat['profile_image_url']:
            chat['profile_image_url'] = 'uploads/' + chat['profile_image_url'] 
        else:
            chat['profile_image_url'] = '/images/default-user.png'

        # Ensure timestamps are correctly handled
        if chat['last_message_time']:
            if not isinstance(chat['last_message_time'], datetime):
                try:
                    chat['last_message_time'] = datetime.strptime(chat['last_message_time'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    chat['last_message_time'] = None

    return render_template('chat-management.html', inbox=inbox)


@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
def chat(user_id):
    if 'seller_id' not in session:  # Ensure the seller is logged in
        return redirect(url_for('login'))

    seller_id = session['seller_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        # Send a message
        message = request.form['message']
        attachment = request.files.get('attachment_url')
        attachment_url = None

        if attachment:
            filename = secure_filename(attachment.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(filepath)
            # Ensure static folder path compatibility
            attachment_url = os.path.join('uploads', filename).replace('\\', '/')



        # Insert new message into the database
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, attachment_url, timestamp, seen_status)
            VALUES (%s, %s, %s, %s, NOW(), 0)
        """, (seller_id, user_id, message, attachment_url))
        mysql.connection.commit()

        # Mark all messages from the recipient as seen
        cursor.execute("""
            UPDATE messages
            SET seen_status = 1
            WHERE sender_id = %s AND receiver_id = %s AND seen_status = 0
        """, (user_id, seller_id))
        mysql.connection.commit()

        flash('Message sent successfully!', 'success')

    # Mark all messages from the recipient as seen when viewing the chat
    cursor.execute("""
        UPDATE messages
        SET seen_status = 1
        WHERE sender_id = %s AND receiver_id = %s AND seen_status = 0
    """, (user_id, seller_id))
    mysql.connection.commit()

    # Fetch inbox data
    cursor.execute("""
        SELECT 
            u.user_id, 
            u.email, 
            u.profile_image_url,
            COALESCE(
                (SELECT message FROM messages WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), '') as last_message,
            COALESCE(
                (SELECT timestamp FROM messages WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), NULL) as last_message_time,
            COALESCE(
                (SELECT seen_status FROM messages WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), 1) as seen_status
        FROM users u
        WHERE u.archived = 0 AND u.approved = 1
    """, (seller_id, seller_id, seller_id, seller_id, seller_id, seller_id))
    inbox = cursor.fetchall()

    # Process the profile image path
    for chat in inbox:
        if chat['profile_image_url']:
            chat['profile_image_url'] = 'uploads/' + chat['profile_image_url']
        else:
            chat['profile_image_url'] = 'images/default-user.png'

        if chat['last_message_time']:
            if not isinstance(chat['last_message_time'], datetime):
                try:
                    chat['last_message_time'] = datetime.strptime(chat['last_message_time'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    chat['last_message_time'] = None

    # Fetch chat messages between the seller and the selected user
    cursor.execute("""
        SELECT 
            sender_id, receiver_id, message, attachment_url, timestamp, seen_status
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp ASC
    """, (seller_id, user_id, user_id, seller_id))
    messages = cursor.fetchall()

    # Fetch user details for the selected chat
    cursor.execute("""
        SELECT user_id, email, first_name, last_name, profile_image_url
        FROM users
        WHERE user_id = %s
    """, (user_id,))
    user = cursor.fetchone()

    if user and user['profile_image_url']:
        user['profile_image_url'] = 'uploads/' + user['profile_image_url']
    else:
        user['profile_image_url'] = 'images/default-user.png'

    return render_template(
        'chat-management.html',
        inbox=inbox,
        messages=messages,
        receiver_email=user['email'] if user else 'Unknown User',
        receiver_image=user['profile_image_url'] if user else 'static/images/default-user.png',
        selected_user_id=user_id
    )


@app.route('/chat/send/<int:user_id>', methods=['POST'])
def send_message_to_user(user_id):
    if 'seller_id' not in session:
        return redirect(url_for('login'))

    seller_id = session['seller_id']
    message = request.form.get('message')
    attachment = request.files.get('attachment_url')

    if not message and not attachment:
        flash("Message or attachment is required.", "warning")
        return redirect(url_for('chat', user_id=user_id))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Process file upload if present
        attachment_url = None
        if attachment:
            filename = secure_filename(attachment.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(filepath)
            attachment_url = f"uploads/{filename}"

        # Insert message into database
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, attachment_url, timestamp, seen_status)
            VALUES (%s, %s, %s, %s, NOW(), 0)
        """, (seller_id, user_id, message, attachment_url))
        mysql.connection.commit()

        # Mark previous messages from the recipient as seen
        cursor.execute("""
            UPDATE messages
            SET seen_status = 1
            WHERE sender_id = %s AND receiver_id = %s AND seen_status = 0
        """, (user_id, seller_id))
        mysql.connection.commit()

        cursor.close()
        return redirect(url_for('chat', user_id=user_id))

    except Exception as e:
        print(f"Error sending message: {e}")
        flash("An error occurred while sending the message.", "danger")
        return redirect(url_for('chat', user_id=user_id))


#=================== BUYER CHAT MANAGEMENT ======================

# Helper function to format timestamps
def format_timestamp(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(timestamp, str):
        try:
            parsed_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            return parsed_time.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None
    return None

@app.route('/user-chat', methods=['GET'])
def user_chat():
    if 'user_id' not in session:  # Ensure the user is logged in
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch inbox data for sellers
    cursor.execute("""
        SELECT 
            s.seller_id AS user_id, 
            s.store_name AS display_name,
            CONCAT('/static/uploads/', s.seller_image) AS profile_image_url,
            COALESCE(
                (SELECT message FROM messages WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), '') as last_message,
            COALESCE(
                (SELECT timestamp FROM messages WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), NULL) as last_message_time,
            COALESCE(
                (SELECT seen_status FROM messages WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), 1) as seen_status
        FROM sellers s
        WHERE s.archived = 0 AND s.approved = 1
    """, (user_id, user_id, user_id, user_id, user_id, user_id))
    inbox = cursor.fetchall()

    # Format timestamps
    for chat in inbox:
        chat['last_message_time'] = format_timestamp(chat['last_message_time'])

    return render_template('user-chat.html', inbox=inbox, selected_user_id=None)


@app.route('/user-chat/<int:seller_id>', methods=['GET', 'POST'])
def user_chat_with_seller(seller_id):
    if 'user_id' not in session:  # Ensure the user is logged in
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Handle sending a message
    if request.method == 'POST':
        message = request.form['message']
        attachment = request.files.get('attachment_url')
        attachment_url = None

        if attachment:
            filename = secure_filename(attachment.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(filepath)
            # Ensure static folder compatibility for serving files
            attachment_url = os.path.join('uploads', filename).replace('\\', '/')


        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message, attachment_url, timestamp, seen_status)
            VALUES (%s, %s, %s, %s, NOW(), 0)
        """, (user_id, seller_id, message, attachment_url))
        mysql.connection.commit()

        cursor.execute("""
            UPDATE messages
            SET seen_status = 1
            WHERE sender_id = %s AND receiver_id = %s AND seen_status = 0
        """, (seller_id, user_id))
        mysql.connection.commit()

        flash('Message sent successfully!', 'success')

    # Mark messages from the seller as seen
    cursor.execute("""
        UPDATE messages
        SET seen_status = 1
        WHERE sender_id = %s AND receiver_id = %s AND seen_status = 0
    """, (seller_id, user_id))
    mysql.connection.commit()

    # Fetch inbox data
    cursor.execute("""
        SELECT 
            s.seller_id AS user_id, 
            s.store_name AS display_name,
            CONCAT('/static/uploads/', s.seller_image) AS profile_image_url,
            COALESCE(
                (SELECT message FROM messages WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), '') as last_message,
            COALESCE(
                (SELECT timestamp FROM messages WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), NULL) as last_message_time,
            COALESCE(
                (SELECT seen_status FROM messages WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                 AND (sender_id = %s OR receiver_id = %s) 
                 ORDER BY timestamp DESC LIMIT 1), 1) as seen_status
        FROM sellers s
        WHERE s.archived = 0 AND s.approved = 1
    """, (user_id, user_id, user_id, user_id, user_id, user_id))
    inbox = cursor.fetchall()

    # Fetch chat messages
    cursor.execute("""
        SELECT sender_id, receiver_id, message, attachment_url, timestamp, seen_status
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp ASC
    """, (user_id, seller_id, seller_id, user_id))
    messages = cursor.fetchall()

    # Format timestamps for chat messages
    for message in messages:
        message['timestamp'] = format_timestamp(message['timestamp'])

    # Fetch seller details
    cursor.execute("""
        SELECT seller_id AS user_id, store_name AS display_name,
        CONCAT('/static/uploads/', seller_image) AS profile_image_url
        FROM sellers
        WHERE seller_id = %s
    """, (seller_id,))
    seller = cursor.fetchone()

    for chat in inbox:
        chat['last_message_time'] = format_timestamp(chat['last_message_time'])

    return render_template(
        'user-chat.html',
        inbox=inbox,
        messages=messages,
        selected_user_id=seller_id,
        receiver_name=seller['display_name'] if seller else 'Unknown Seller'
    )


# # live chat functionallity
# @app.route('/api/messages/<int:recipient_id>', methods=['GET'])
# def fetch_messages(recipient_id):
#     # Check if the request comes from a logged-in seller or user
#     seller_id = session.get('seller_id')  # Check seller session
#     user_id = session.get('user_id')  # Check user session

#     if not seller_id and not user_id:
#         return jsonify({'error': 'Unauthorized'}), 401

#     # Determine the current user's ID and role
#     current_id = seller_id or user_id
#     role = 'seller' if seller_id else 'user'

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Fetch chat messages for the current user/seller and recipient
#     cursor.execute("""
#         SELECT sender_id, receiver_id, message, attachment_url, timestamp
#         FROM messages
#         WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
#         ORDER BY timestamp ASC
#     """, (current_id, recipient_id, recipient_id, current_id))
#     messages = cursor.fetchall()

#     # Format timestamps for JSON response
#     for message in messages:
#         message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

#     return jsonify({'messages': messages, 'role': role})


@app.route('/api/messages/<int:recipient_id>', methods=['GET'])
def fetch_messages(recipient_id):
    seller_id = session.get('seller_id')
    user_id = session.get('user_id')

    if not seller_id and not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    current_id = seller_id or user_id

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT sender_id, receiver_id, message, attachment_url, timestamp
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp ASC
    """, (current_id, recipient_id, recipient_id, current_id))
    messages = cursor.fetchall()

    for message in messages:
        # Format timestamp and attachment URL for JSON response
        message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        if message['attachment_url']:
            message['attachment_url'] = url_for('static', filename=message['attachment_url'])

    return jsonify({'messages': messages})


#================================================= chat with admin ===============================================================================

#admin
from flask import send_file, abort

@app.route('/serve_attachment/<path:filename>')
def serve_attachment(filename):
    """Serve file from Flask uploads or fallback to XAMPP uploads folder"""
    flask_path = os.path.join(app.root_path, 'uploads', filename)
    xampp_path = os.path.join('D:/xampp/htdocs/bbb_api/uploads', filename)

    if os.path.isfile(flask_path):
        return send_file(flask_path)
    elif os.path.isfile(xampp_path):
        return send_file(xampp_path)
    else:
        abort(404, description="Attachment not found")


@app.route('/admin_user_chat_management', methods=['GET', 'POST'])
def admin_user_chat_management():
    if 'admin_id' not in session:  # Ensure the admin is logged in
        return redirect(url_for('login'))

    admin_id = session['admin_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Fetch inbox data for buyers (users with a 'buyer' role or condition matching buyers)
        query = """
            SELECT 
                u.user_id, 
                u.email, 
                u.profile_image_url,
                COALESCE(
                    (SELECT message FROM chats 
                     WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), '') as last_message,
                COALESCE(
                    (SELECT timestamp FROM chats 
                     WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), NULL) as last_message_time,
                COALESCE(
                    (SELECT is_read FROM chats 
                     WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), 1) as seen_status
            FROM users u
            WHERE u.role = 'buyer'  -- Example condition to filter only buyers
              AND u.archived = 0
            ORDER BY 
                COALESCE(
                    (SELECT timestamp FROM chats 
                     WHERE (sender_id = u.user_id OR receiver_id = u.user_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), '1970-01-01 00:00:00') DESC
        """
        cursor.execute(query, (admin_id, admin_id, admin_id, admin_id, admin_id, admin_id, admin_id, admin_id))
        inbox = cursor.fetchall()

        # Process profile image paths
        for chat in inbox:
            if chat['profile_image_url']:
                chat['profile_image_url'] = 'uploads/' + chat['profile_image_url']
            else:
                chat['profile_image_url'] = 'images/default-user.png'

            if chat['last_message_time']:
                chat['last_message_time'] = chat['last_message_time'].strftime('%Y-%m-%d %H:%M:%S')

        # Render the chat management template
        return render_template('admin_user_chat_management.html', inbox=inbox, messages=None, selected_user_id=None)
    except Exception as e:
        print(f"Error fetching inbox: {e}")
        return "Error loading chat management", 500



# @app.route('/admin/chat/<int:user_id>', methods=['GET', 'POST'])
# def admin_chat_with_user(user_id):
#     """Admin Chat Logic embedded in chat management."""
#     if 'admin_id' not in session:  # Ensure the admin is logged in
#         return redirect(url_for('login'))

#     admin_id = session['admin_id']
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Handle sending a message
#     if request.method == 'POST':
#         message = request.form.get('message')
#         attachment = request.files.get('attachment_url')
#         attachment_url = None

#         if attachment:
#             filename = secure_filename(attachment.filename)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             attachment.save(filepath)
#             attachment_url = f"serve_attachment/{filename}"

#         # Insert the new message into the chats table
#         cursor.execute("""
#             INSERT INTO chats (sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, timestamp, is_read)
#             VALUES (%s, 'admin', %s, 'user', %s, %s, NOW(), 0)
#         """, (admin_id, user_id, message, attachment_url))
#         mysql.connection.commit()

#         # Mark older messages from the user to admin as read
#         cursor.execute("""
#             UPDATE chats
#             SET is_read = 1
#             WHERE sender_id = %s AND receiver_id = %s AND sender_role = 'user' AND receiver_role = 'admin' AND is_read = 0
#         """, (user_id, admin_id))
#         mysql.connection.commit()

#     # Fetch chat messages between admin and user
#     cursor.execute("""
#         SELECT sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, timestamp, is_read
#         FROM chats
#         WHERE (sender_id = %s AND receiver_id = %s AND sender_role = 'admin' AND receiver_role = 'user')
#            OR (sender_id = %s AND receiver_id = %s AND sender_role = 'user' AND receiver_role = 'admin')
#         ORDER BY timestamp ASC
#     """, (admin_id, user_id, user_id, admin_id))
#     messages = cursor.fetchall()

#     for message in messages:
#         message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

#     cursor.execute("""
#         SELECT email 
#         FROM users 
#         WHERE user_id = %s
#     """, (user_id,))
#     user = cursor.fetchone()

#     return jsonify({'messages': messages, 'receiver_name': user['email'] if user else 'Unknown User'})

@app.route('/admin/chat/<int:user_id>', methods=['GET', 'POST'])
def admin_chat_with_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    admin_id = session['admin_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        message = request.form.get('message')
        attachment = request.files.get('attachment_url')
        attachment_url = None

        if attachment:
            filename = secure_filename(attachment.filename)
            save_dir = os.path.join(app.root_path, 'uploads')
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(save_dir, filename)
            attachment.save(filepath)
            attachment_url = f"uploads/{filename}"

        cursor.execute("""
            INSERT INTO chats (sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, timestamp, is_read)
            VALUES (%s, 'admin', %s, 'user', %s, %s, NOW(), 0)
        """, (admin_id, user_id, message, attachment_url))
        mysql.connection.commit()

        cursor.execute("""
            UPDATE chats
            SET is_read = 1
            WHERE sender_id = %s AND receiver_id = %s AND sender_role = 'user' AND receiver_role = 'admin' AND is_read = 0
        """, (user_id, admin_id))
        mysql.connection.commit()

    cursor.execute("""
        SELECT sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, timestamp, is_read
        FROM chats
        WHERE (sender_id = %s AND receiver_id = %s AND sender_role = 'admin' AND receiver_role = 'user')
           OR (sender_id = %s AND receiver_id = %s AND sender_role = 'user' AND receiver_role = 'admin')
        ORDER BY timestamp ASC
    """, (admin_id, user_id, user_id, admin_id))
    messages = cursor.fetchall()

    for message in messages:
        message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    if message['attachment_url']:
        filename_only = os.path.basename(message['attachment_url'])
        message['attachment_url'] = url_for('serve_attachment', filename=filename_only, _external=True)


    cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    return jsonify({'messages': messages, 'receiver_name': user['email'] if user else 'Unknown User'})

@app.route('/admin_seller_chat_management', methods=['GET', 'POST'])
def admin_seller_chat_management():
    if 'admin_id' not in session:  # Ensure the admin is logged in
        return redirect(url_for('login'))

    admin_id = session['admin_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Fetch inbox data for sellers
        query = """
            SELECT 
                s.seller_id, 
                s.email, 
                s.seller_image,
                s.store_name,
                COALESCE(
                    (SELECT message FROM chats 
                     WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), '') as last_message,
                COALESCE(
                    (SELECT timestamp FROM chats 
                     WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), NULL) as last_message_time,
                COALESCE(
                    (SELECT is_read FROM chats 
                     WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), 1) as seen_status
            FROM sellers s
            WHERE s.archived = 0 AND s.rejected = 0
            ORDER BY 
                COALESCE(
                    (SELECT timestamp FROM chats 
                     WHERE (sender_id = s.seller_id OR receiver_id = s.seller_id) 
                     AND (sender_id = %s OR receiver_id = %s) 
                     ORDER BY timestamp DESC LIMIT 1), '1970-01-01 00:00:00') DESC
        """
        cursor.execute(query, (admin_id, admin_id, admin_id, admin_id, admin_id, admin_id, admin_id, admin_id))
        inbox = cursor.fetchall()

        # Process profile image paths
        for chat in inbox:
            if chat['seller_image']:
                chat['seller_image'] = 'uploads/' + chat['seller_image']

            if chat['last_message_time']:
                chat['last_message_time'] = chat['last_message_time'].strftime('%Y-%m-%d %H:%M:%S')

        # Render the seller chat management template
        return render_template('admin_seller_chat_management.html', inbox=inbox, messages=None, selected_user_id=None)
    except Exception as e:
        print(f"Error fetching inbox: {e}")
        return "Error loading seller chat management", 500


@app.route('/admin/chat/seller/<int:seller_id>', methods=['GET', 'POST'])
def admin_chat_with_seller(seller_id):
    if 'admin_id' not in session:  # Ensure the admin is logged in
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    admin_id = session['admin_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Handle sending a message
    if request.method == 'POST':
        message = request.form.get('message')
        attachment = request.files.get('attachment_url')
        attachment_url = None

        if attachment:
            filename = secure_filename(attachment.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(filepath)
            attachment_url = f"uploads/{filename}"

        # Insert the admin's new message with is_read = 0
        cursor.execute("""
            INSERT INTO chats (sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, timestamp, is_read)
            VALUES (%s, 'admin', %s, 'seller', %s, %s, NOW(), 0)
        """, (admin_id, seller_id, message, attachment_url))
        mysql.connection.commit()

        # Update all previous messages sent by the seller to the admin as is_read = 1
        cursor.execute("""
            UPDATE chats
            SET is_read = 1
            WHERE sender_id = %s AND receiver_id = %s AND is_read = 0
        """, (seller_id, admin_id))
        mysql.connection.commit()

    # Fetch chat messages between admin and seller
    cursor.execute("""
        SELECT sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, timestamp, is_read
        FROM chats
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp ASC
    """, (admin_id, seller_id, seller_id, admin_id))
    messages = cursor.fetchall()

    for message in messages:
        message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    # Fetch seller email for display
    cursor.execute("SELECT email FROM sellers WHERE seller_id = %s", (seller_id,))
    seller = cursor.fetchone()

    return jsonify({'success': True, 'messages': messages, 'receiver_name': seller['email'] if seller else 'Unknown User'})

#=== USER ===

@app.route('/customer-service', methods=['GET'])
def get_chat_history():
    if 'user_id' not in session:  # Ensure the user is logged in
        return redirect(url_for('login'))

    user_id = session['user_id']
    admin_id = 2  # Admin's fixed ID
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return "User not found", 404

        if user.get('profile_image_url'):  
            user['profile_image_url'] = f"uploads/{user['profile_image_url']}"
        else:  
            user['profile_image_url'] = "images/default-user.png"

        query = """
            SELECT sender_id, receiver_id, message, attachment_url, timestamp, is_read
            FROM chats
            WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (user_id, admin_id, admin_id, user_id))
        messages = cursor.fetchall()


        cursor.execute("""
            UPDATE chats
            SET is_read = TRUE
            WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE
        """, (admin_id, user_id))
        mysql.connection.commit()
        cursor.close()

        # Render the template with chat history and user details
        return render_template('user_customer_service.html', user=user, messages=messages)
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return "Error fetching chat history", 500



@app.route('/chat/send', methods=['POST'])
def send_message_to_admin_user():
    if 'user_id' not in session:  # Ensure the user is logged in
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    user_id = session['user_id']
    admin_id = 2  # Admin's fixed ID
    message = request.form.get('message')
    attachment = request.files.get('attachment_url')

    if not message and not attachment:
        return jsonify({"success": False, "error": "Message or attachment is required"}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Handle file upload if an attachment is provided
        attachment_url = None
        if attachment:
            filename = secure_filename(attachment.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(file_path)
            attachment_url = f"uploads/{filename}"

        # Insert the message into the database with is_read = 0
        query = """
            INSERT INTO chats (sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, is_read, timestamp)
            VALUES (%s, 'user', %s, 'admin', %s, %s, FALSE, NOW())
        """
        cursor.execute(query, (user_id, admin_id, message, attachment_url))
        mysql.connection.commit()

        # Mark all past chats from the admin to the user as read, leaving the new message unread
        mark_read_query = """
            UPDATE chats
            SET is_read = TRUE
            WHERE (sender_id = %s AND receiver_id = %s)
               AND sender_role = 'admin'
               AND receiver_role = 'user'
        """
        cursor.execute(mark_read_query, (admin_id, user_id))
        mysql.connection.commit()

        cursor.close()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({"success": False, "error": "Error sending message"}), 500



@app.route('/chat/send/seller', methods=['POST'])
def send_message_to_admin():
    if 'seller_id' not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    seller_id = session['seller_id']
    admin_id = 2  # Fixed admin ID
    message = request.form.get('message')
    attachment = request.files.get('attachment_url')

    if not message and not attachment:
        return jsonify({"success": False, "error": "Message or attachment is required"}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Handle file upload if an attachment is provided
        attachment_url = None
        if attachment:
            filename = secure_filename(attachment.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(file_path)
            attachment_url = f"uploads/{filename}"

        # Insert the seller's message with is_read = 0
        cursor.execute("""
            INSERT INTO chats (sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, is_read, timestamp)
            VALUES (%s, 'seller', %s, 'admin', %s, %s, 0, NOW())
        """, (seller_id, admin_id, message, attachment_url))
        mysql.connection.commit()

        # Update all previous chats to is_read = 1 (both directions)
        cursor.execute("""
            UPDATE chats
            SET is_read = 1
            WHERE (sender_id = %s AND receiver_id = %s)
               OR (sender_id = %s AND receiver_id = %s)
        """, (admin_id, seller_id, seller_id, admin_id))
        mysql.connection.commit()

        cursor.close()
        return redirect(url_for('chat_management'))
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({"success": False, "error": "Error sending message"}), 500


# ======= SELLER ================
@app.route('/seller-service', methods=['GET'])
def get_chat_history_for_seller():
    if 'seller_id' not in session:  
        return redirect(url_for('login'))

    seller_id = session['seller_id']
    admin_id = 2  # Admin's fixed ID
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute("SELECT * FROM sellers WHERE seller_id = %s", (seller_id,))
        seller = cursor.fetchone()

        if not seller:
            return "Seller not found", 404

        if seller.get('seller_image'):  
            seller['seller_image'] = f"uploads/{seller['seller_image']}"


        query = """
            SELECT sender_id, receiver_id, message, attachment_url, timestamp, is_read
            FROM chats
            WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (seller_id, admin_id, admin_id, seller_id))
        messages = cursor.fetchall()

        cursor.execute("""
            UPDATE chats
            SET is_read = TRUE
            WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE
        """, (admin_id, seller_id))
        mysql.connection.commit()
        cursor.close()

        # Render the template with chat history and seller details
        return render_template('chat-with-admin.html', seller=seller, messages=messages)
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return "Error fetching chat history", 500
    
@app.route('/chat/send/seller', methods=['POST'])
def send_message_to_admin_from_seller():
    if 'seller_id' not in session:
        return redirect(url_for('login'))

    seller_id = session['seller_id']
    admin_id = 2  # Fixed admin ID
    message = request.form.get('message')
    attachment = request.files.get('attachment_url')

    if not message and not attachment:
        return jsonify({"success": False, "error": "Message or attachment is required"}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        # Handle file upload if an attachment is provided
        attachment_url = None
        if attachment:
            filename = secure_filename(attachment.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(file_path)
            attachment_url = f"uploads/{filename}"

        # Insert the seller's new message with is_read = 0
        cursor.execute("""
            INSERT INTO chats (sender_id, sender_role, receiver_id, receiver_role, message, attachment_url, is_read, timestamp)
            VALUES (%s, 'seller', %s, 'admin', %s, %s, 0, NOW())
        """, (seller_id, admin_id, message, attachment_url))
        mysql.connection.commit()

        # Update all previous messages sent by the admin to the seller as is_read = 1
        cursor.execute("""
            UPDATE chats
            SET is_read = 1
            WHERE sender_id = %s AND receiver_id = %s AND is_read = 0
        """, (admin_id, seller_id))
        mysql.connection.commit()

        cursor.close()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error sending message: {e}")
    flash("Error sending message.", "danger")
    return redirect(url_for('chat_management'))

@app.route('/chat_user/<int:user_id>', methods=['GET', 'POST'])
def chat_user(user_id):
    seller_id = session.get('seller_id')  # assuming seller is logged in

    # Insert message if POST
    if request.method == 'POST':
        message_text = request.form.get('message')
        file = request.files.get('attachment_url')

        attachment_url = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            attachment_url = f'uploads/{filename}'

        # Insert message into DB
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, message, attachment_url) VALUES (%s, %s, %s, %s)",
            (seller_id, user_id, message_text, attachment_url)
        )
        mysql.connection.commit()
        cursor.close()
        # ✅ Do NOT return here — continue to render the page after sending

    # Fetch chat history
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
        ORDER BY timestamp ASC
    """, (seller_id, user_id, user_id, seller_id))
    messages = cursor.fetchall()

    # Fetch inbox list
    cursor.execute("""
        SELECT u.user_id, u.email, u.profile_image_url, m.message AS last_message, m.timestamp AS last_message_time, m.seen_status
        FROM users u
        JOIN (
            SELECT * FROM messages 
            WHERE sender_id = %s OR receiver_id = %s
            ORDER BY timestamp DESC
        ) m ON u.user_id = CASE WHEN m.sender_id = %s THEN m.receiver_id ELSE m.sender_id END
        GROUP BY u.user_id
    """, (seller_id, seller_id, seller_id))
    inbox = cursor.fetchall()
    cursor.close()

    return render_template(
        'chat-management.html',
        messages=messages,
        inbox=inbox,
        selected_user_id=user_id
    )




#================================================= VOUCHER =======================================================================================

@app.route('/admin/vouchers', methods=['GET'])
def admin_marketing_vouchers():
    try:
        # Fetch all vouchers from the database
        cursor = mysql.connection.cursor()
        query = "SELECT id, voucher_code, description, discount, category, voucher_image FROM vouchers"
        cursor.execute(query)
        vouchers = cursor.fetchall()

        # Convert the result to a list of dictionaries for easy handling in the template
        vouchers_list = [
            {
                "id": row[0],
                "voucher_code": row[1],
                "description": row[2],
                "discount": float(row[3]),
                "category": row[4],
                "voucher_image": row[5],
            }
            for row in vouchers
        ]
        return render_template('admin_marketing_vouchers.html', vouchers=vouchers_list)
    except Exception as e:
        flash(f"Error fetching vouchers: {e}", "error")
        return render_template('admin_marketing_vouchers.html', vouchers=[])
    finally:
        cursor.close()

@app.route('/add-voucher', methods=['GET', 'POST'])
def add_voucher():
    show_modal = False  # To control success modal
    error_message = None  # To display the error message

    if request.method == 'POST':
        # Get form data
        voucher_code = request.form.get('voucher_code')
        description = request.form.get('description')
        discount = request.form.get('discount')
        category = request.form.get('category')
        voucher_image = None

        # Handle file upload
        if 'voucher_image' in request.files:
            file = request.files['voucher_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                voucher_image = filename 

        # Validate data
        if not voucher_code or not description or not discount or not category:
            error_message = 'All fields are required!'
            return render_template('add-voucher.html', show_modal=False, error_message=error_message)

        try:
            # Check if voucher code already exists
            cursor = mysql.connection.cursor()
            query_check = "SELECT * FROM vouchers WHERE voucher_code = %s"
            cursor.execute(query_check, (voucher_code,))
            existing_voucher = cursor.fetchone()

            if existing_voucher:
                error_message = 'Voucher code already exists!'
                return render_template('add-voucher.html', show_modal=False, error_message=error_message)

            # Insert into the database
            query = """
                INSERT INTO vouchers (voucher_code, description, discount, category, voucher_image)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (voucher_code, description, Decimal(discount), category, voucher_image)
            cursor.execute(query, values)
            mysql.connection.commit()
            show_modal = True  # Trigger success modal
        except Exception as e:
            error_message = f"An error occurred: {e}"
            mysql.connection.rollback()
        finally:
            cursor.close()

    return render_template('add-voucher.html', show_modal=show_modal, error_message=error_message)

@app.route('/delete-voucher/<int:voucher_id>', methods=['POST', 'GET'])
def delete_voucher(voucher_id):
    try:
        # Connect to the database
        cursor = mysql.connection.cursor()

        # Find and delete the voucher by ID
        # Step 1: Retrieve the voucher image path to delete the file
        cursor.execute("SELECT voucher_image FROM vouchers WHERE id = %s", (voucher_id,))
        voucher = cursor.fetchone()
        if voucher and voucher[0]:
            image_path = voucher[0]  # Path to the image
            # Delete the image file if it exists
            if os.path.exists(image_path):
                os.remove(image_path)

        # Step 2: Delete the voucher from the database
        cursor.execute("DELETE FROM vouchers WHERE id = %s", (voucher_id,))
        mysql.connection.commit()

        flash("Voucher deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting voucher: {e}", "error")
        mysql.connection.rollback()
    finally:
        cursor.close()

    # Redirect to the vouchers management page
    return redirect(url_for('admin_marketing_vouchers'))
from flask import request

# spare delete route(DONT DELETE)
# @app.route('/delete-voucher/<int:voucher_id>', methods=['POST'])
# def delete_voucher(voucher_id):
#     try:
#         # Connect to the database
#         cursor = mysql.connection.cursor()

#         # Step 1: Retrieve the voucher image path to delete the file
#         cursor.execute("SELECT voucher_image FROM vouchers WHERE id = %s", (voucher_id,))
#         voucher = cursor.fetchone()
#         if voucher and voucher[0]:
#             image_path = voucher[0]  # Path to the image
#             # Delete the image file if it exists
#             if os.path.exists(image_path):
#                 os.remove(image_path)

#         # Step 2: Delete the voucher from the database
#         cursor.execute("DELETE FROM vouchers WHERE id = %s", (voucher_id,))
#         mysql.connection.commit()

#         flash("Voucher deleted successfully!", "success")
#     except Exception as e:
#         flash(f"Error deleting voucher: {e}", "error")
#         mysql.connection.rollback()
#     finally:
#         cursor.close()

#     # Redirect to the vouchers management page
#     return redirect(url_for('admin_marketing_vouchers'))





#   ======================================= COURIER ==============================================
# @app.route('/courier-homepage')
# def courier_homepage():
#     if 'courier_id' not in session:
#         flash('Please log in first.')
#         return redirect(url_for('login'))

#     # Initialize default values for dashboard metrics
#     total_sales = 0
#     new_orders = 0
#     delivery_count = 0
#     returns_refunds = 0
#     on_delivery = 0
#     daily_sales = 0
#     # For couriers, stock metrics may not apply
#     low_stock_count = 0
#     out_of_stock_count = 0
#     courier_name = "Your Courier"
#     top_deliveries = []  # Placeholder for top delivery metrics (if applicable)

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     courier_id = session['courier_id']

#     # Get courier details (name)
#     cursor.execute('''
#         SELECT first_name, last_name 
#         FROM courier 
#         WHERE id = %s
#     ''', (courier_id,))
#     result = cursor.fetchone()
#     if result:
#         courier_name = f"{result['first_name']} {result['last_name']}"

#     # NOTE: Since the orders table doesn't have a column to link orders to couriers,
#     # the following queries use overall orders data rather than courier-specific data.
#     # Once you add a column (e.g., assigned_courier_id) to your orders table,
#     # update these queries to filter by that column.

#     # Query for overall Total Sales (completed orders)
#     cursor.execute('''
#         SELECT SUM(total_price) AS total_sales 
#         FROM orders 
#         WHERE order_status = %s
#     ''', ('completed',))
#     result = cursor.fetchone()
#     if result and result['total_sales'] is not None:
#         total_sales = result['total_sales']

#     # Query for overall Daily Sales (completed orders today)
#     cursor.execute('''
#         SELECT SUM(total_price) AS daily_sales 
#         FROM orders 
#         WHERE order_status = %s AND DATE(updated_at) = CURDATE()
#     ''', ('completed',))
#     result = cursor.fetchone()
#     if result and result['daily_sales'] is not None:
#         daily_sales = result['daily_sales']

#     # Placeholder queries for new orders, delivery count, returns/refunds, and on delivery.
#     # Replace these with courier-specific queries once your orders table includes a courier assignment.
#     new_orders = 0
#     delivery_count = 0
#     returns_refunds = 0
#     on_delivery = 0

#     # Example: Unread Chat Notifications for the courier (assumes messages.receiver_id refers to courier_id)
#     cursor.execute('''
#         SELECT DISTINCT u.email AS sender_email, MAX(m.timestamp) AS latest_message_time
#         FROM messages m
#         JOIN users u ON m.sender_id = u.user_id
#         WHERE m.receiver_id = %s AND m.seen_status = 0
#         GROUP BY u.email
#         ORDER BY latest_message_time DESC
#     ''', (courier_id,))
#     unread_chat_notifications = cursor.fetchall()

#     cursor.close()

#     return render_template(
#         'courier-homepage.html',
#         total_sales=total_sales,
#         new_orders=new_orders,
#         delivery_count=delivery_count,
#         returns_refunds=returns_refunds,
#         on_delivery=on_delivery,
#         courier_name=courier_name,
#         top_deliveries=top_deliveries,
#         unread_chat_notifications=unread_chat_notifications,
#         daily_sales=daily_sales,
#         low_stock_count=low_stock_count,
#         out_of_stock_count=out_of_stock_count
#     )


@app.route('/courier-homepage')
def courier_homepage():
    if 'courier_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    courier_id = session['courier_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get courier name
    cursor.execute('''
        SELECT first_name, last_name 
        FROM courier 
        WHERE id = %s
    ''', (courier_id,))
    result = cursor.fetchone()
    courier_name = f"{result['first_name']} {result['last_name']}" if result else "Your Courier"

    # Query to count most delivered locations (Province, City, Barangay)
    cursor.execute('''
        SELECT 
            SUBSTRING_INDEX(SUBSTRING_INDEX(delivery_address, ',', -3), ',', 1) AS barangay,
            SUBSTRING_INDEX(SUBSTRING_INDEX(delivery_address, ',', -2), ',', 1) AS city,
            SUBSTRING_INDEX(SUBSTRING_INDEX(delivery_address, ',', -1), '-', 1) AS province,
            COUNT(*) AS total_deliveries
        FROM orders
        WHERE courier_id = %s AND (order_status = 'completed' OR order_status = 'delivered')
        GROUP BY barangay, city, province
        ORDER BY total_deliveries DESC
        LIMIT 10;
    ''', (courier_id,))
    most_delivered_locations = cursor.fetchall()

    # Total Orders Today (Packed by the courier, resets at midnight)
    cursor.execute('''
        SELECT COUNT(*) AS total_orders
        FROM orders 
        WHERE courier_id = %s 
        AND (order_status = 'on_the_way' OR order_status = 'delivered' OR order_status = 'completed')
        AND DATE(updated_at) = CURDATE()
    ''', (courier_id,))
    result = cursor.fetchone()
    total_orders = result['total_orders'] if result else 0


    # **Total Commission (₱45 per completed order, resets every 30 days)**
    cursor.execute('''
        SELECT COUNT(*) AS completed_deliveries
        FROM orders 
        WHERE courier_id = %s AND order_status = 'completed'
        AND updated_at >= (NOW() - INTERVAL 30 DAY)
    ''', (courier_id,))
    result = cursor.fetchone()
    completed_deliveries = result['completed_deliveries'] if result else 0
    total_commission = completed_deliveries * 45  # ₱45 per order delivered

    # **Orders In Transit**
    cursor.execute('''
        SELECT COUNT(*) AS on_delivery
        FROM orders 
        WHERE courier_id = %s AND order_status = 'on_the_way'
    ''', (courier_id,))
    result = cursor.fetchone()
    on_delivery = result['on_delivery'] if result else 0

    # **Return/Pickups (Orders picked up by courier, resets at midnight)**
    cursor.execute('''
        SELECT COUNT(*) AS returns_refunds
        FROM orders 
        WHERE courier_id = %s AND order_status = 'returned/refunded'
        AND DATE(updated_at) = CURDATE()
    ''', (courier_id,))
    result = cursor.fetchone()
    returns_refunds = result['returns_refunds'] if result else 0

    # Orders Packed But Not Delivered Today
    cursor.execute('''
        SELECT COUNT(*) AS not_delivered_today
        FROM orders 
        WHERE courier_id = %s AND order_status = 'on_the_way'
        AND DATE(updated_at) = CURDATE()
    ''', (courier_id,))
    result = cursor.fetchone()
    not_delivered_today = result['not_delivered_today'] if result else 0

    # Total Commission Earned Today (₱45 per completed order)
    cursor.execute('''
        SELECT COUNT(*) AS completed_today
        FROM orders 
        WHERE courier_id = %s AND order_status = 'completed'
        AND DATE(updated_at) = CURDATE()
    ''', (courier_id,))
    result = cursor.fetchone()
    completed_today = result['completed_today'] if result else 0
    daily_commission = completed_today * 45  # ₱45 per order

    #  Orders Not Delivered for 15+ Days
    cursor.execute('''
        SELECT COUNT(*) AS overdue_orders
        FROM orders 
        WHERE courier_id = %s 
        AND order_status = 'on_the_way'
        AND DATE(updated_at) <= (CURDATE() - INTERVAL 15 DAY)
    ''', (courier_id,))
    result = cursor.fetchone()
    overdue_orders = result['overdue_orders'] if result else 0

    # Orders Not Delivered for 20+ Days (Trigger Report)
    cursor.execute('''
        SELECT COUNT(*) AS report_needed
        FROM orders 
        WHERE courier_id = %s 
        AND order_status = 'on_the_way'
        AND DATE(updated_at) <= (CURDATE() - INTERVAL 20 DAY)
    ''', (courier_id,))
    result = cursor.fetchone()
    report_needed = result['report_needed'] if result else 0


    cursor.close()

    return render_template(
        'courier-homepage.html',
        courier_name=courier_name,
        total_orders=total_orders,
        total_commission=total_commission,
        daily_commission= daily_commission,
        on_delivery=on_delivery,
        returns_refunds=returns_refunds,
        overdue_orders=overdue_orders,
        report_needed =report_needed,
        not_delivered_today=not_delivered_today,
        most_delivered_locations = most_delivered_locations
    )



# ============================================= ORDERS  ==================================================================

#Courier Get Orders
@app.route('/courier-orders')
def courier_orders():
    if 'courier_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    
    # For now, we do not filter by courier_id since orders are not yet assigned.
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Retrieve orders with status 'approved' along with user details.
    cur.execute("""
        SELECT o.order_id, o.delivery_address, o.quantity, o.order_status, o.total_price, o.created_at,
               u.first_name, u.last_name, u.phone_number
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.order_status IN ('approved')
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()
    cur.close()
    
    return render_template('courier-orders.html', orders=orders)


#Courier Intransit Orders
#@app.route('/courier_in_transit')
#def courier_in_transit():
#    if 'courier_id' not in session:
#        flash("Please log in first.")
#        return redirect(url_for('login'))
#    
#    # For now, we do not filter by courier_id since orders are not yet assigned.
#    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
#    # Retrieve orders with status 'approved' along with user details.
#    cur.execute("""
#        SELECT o.order_id, o.delivery_address, o.quantity, o.order_status, o.total_price, o.created_at,
#               u.first_name, u.last_name, u.phone_number
#        FROM orders o
#        JOIN users u ON o.user_id = u.user_id
#        WHERE o.order_status IN ('on_the_way')
#        ORDER BY o.created_at DESC
#    """)
#    orders = cur.fetchall()
#    cur.close()
#    
#    return render_template('courier-in_transit.html', orders=orders)


@app.route('/assign_courier', methods=['POST'])
def assign_courier():
    """Assigns an order to a courier when it is packed."""
    if 'courier_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in first.'})

    courier_id = session['courier_id']
    order_id = request.form.get('order_id')

    if not order_id:
        return jsonify({'status': 'error', 'message': 'Invalid order ID.'})

    try:
        cur = mysql.connection.cursor()
        
        # Update the order with the courier ID and change status to "on_the_way"
        cur.execute("""
            UPDATE orders 
            SET courier_id = %s, order_status = 'on_the_way'
            WHERE order_id = %s AND courier_id IS NULL
        """, (courier_id, order_id))

        if cur.rowcount == 0:
            return jsonify({'status': 'error', 'message': 'Order already assigned or does not exist.'})

        mysql.connection.commit()
        cur.close()

        return jsonify({'status': 'success', 'message': 'Order packed successfully and assigned to you!'})

    except Exception as e:
        mysql.connection.rollback()
        print(f"Database error: {e}")
        return jsonify({'status': 'error', 'message': 'Database error occurred. Try again later.'})


@app.route('/courier_in_transit')
def courier_in_transit():
    """Shows only orders assigned to the logged-in courier."""
    if 'courier_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    courier_id = session['courier_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Retrieve orders that are assigned to this courier
    cur.execute("""
        SELECT o.order_id, o.delivery_address, o.quantity, o.order_status, o.total_price, o.created_at,
               u.first_name, u.last_name, u.phone_number
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.order_status = 'on_the_way' AND o.courier_id = %s
        ORDER BY o.created_at DESC
    """, (courier_id,))

    orders = cur.fetchall()
    cur.close()

    return render_template('courier-in_transit.html', orders=orders)


#Courier Intransit Orders
@app.route('/courier_returns')
def courier_returns():
    if 'courier_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    
    # For now, we do not filter by courier_id since orders are not yet assigned.
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Retrieve orders with status 'approved' along with user details.
    cur.execute("""
        SELECT o.order_id, o.delivery_address, o.quantity, o.order_status, o.total_price, o.created_at,
               u.first_name, u.last_name, u.phone_number
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.order_status IN ('refund_approved')
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()
    cur.close()
    
    return render_template('courier-returns.html', orders=orders)



# ======================================== COURIER UPDATE ACCOUNT ============================================

# Store OTPs temporarily (in-memory storage)
otp_storage = {}

@app.route('/send_otp', methods=['POST'])
def send_otp():
    if 'courier_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    email = request.form['email']
    otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
    otp_storage[email] = otp  # Store OTP temporarily

    try:
        msg = Message("Verification Code", recipients=[email])
        msg.body = f"Your verification code is: {otp}. Enter this code to confirm your changes."
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'OTP sent successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



@app.route('/courier-account', methods=['GET', 'POST'])
def courier_account():
    if 'courier_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))
    
    courier_id = session['courier_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch courier details
    cur.execute("SELECT * FROM courier WHERE id = %s", (courier_id,))
    courier = cur.fetchone()
    cur.close()

    return render_template('courier-account_settings.html', courier=courier)

@app.route('/courier_update_email', methods=['POST'])
def courier_update_email():
    if 'courier_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))
    
    new_email = request.form['new-email']
    courier_id = session['courier_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute("UPDATE courier SET email = %s WHERE id = %s", (new_email, courier_id))
        mysql.connection.commit()
        flash("Email updated successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error updating email: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('courier_account'))

@app.route('/courier_update_password', methods=['POST'])
def courier_update_password():
    if 'courier_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))
    
    courier_id = session['courier_id']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']
    
    if new_password != confirm_new_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('courier_account'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT password FROM courier WHERE id = %s", (courier_id,))
    courier = cur.fetchone()
    if not courier or not check_password_hash(courier['password'], current_password):
        flash("Current password is incorrect.", "danger")
        cur.close()
        return redirect(url_for('courier_account'))
    
    hashed_new_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    try:
        cur.execute("UPDATE courier SET password = %s WHERE id = %s", (hashed_new_password, courier_id))
        mysql.connection.commit()
        flash("Password updated successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error updating password: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('courier_account'))

@app.route('/courier_update_phone', methods=['POST'])
def courier_update_phone():
    if 'courier_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))
    
    new_phone = request.form['new-phone']
    courier_id = session['courier_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute("UPDATE courier SET phone_number = %s WHERE id = %s", (new_phone, courier_id))
        mysql.connection.commit()
        flash("Phone number updated successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error updating phone number: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('courier_account'))


def get_province_name(province_code):
    try:
        response = requests.get('https://psgc.gitlab.io/api/provinces')
        if response.status_code == 200:
            provinces = response.json()
            for p in provinces:
                if str(p.get('code')) == str(province_code):
                    return p.get('name')
    except Exception as e:
        print("Error fetching province name:", e)
    return province_code  # Return code if name not found

def get_city_name(province_code, city_code):
    try:
        url = f'https://psgc.gitlab.io/api/provinces/{province_code}/municipalities'
        response = requests.get(url)
        if response.status_code == 200:
            cities = response.json()
            for c in cities:
                if str(c.get('code')) == str(city_code):
                    return c.get('name')
    except Exception as e:
        print("Error fetching city name:", e)
    return city_code  # Return code if name not found

def get_barangay_name(city_code, barangay_code):
    try:
        url = f'https://psgc.gitlab.io/api/municipalities/{city_code}/barangays'
        response = requests.get(url)
        if response.status_code == 200:
            barangays = response.json()
            for b in barangays:
                if str(b.get('code')) == str(barangay_code):
                    return b.get('name')
    except Exception as e:
        print("Error fetching barangay name:", e)
    return barangay_code  # Return code if name not found

@app.route('/courier_update_address', methods=['POST'])
def courier_update_address():
    if 'courier_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    # Retrieve numerical codes from form input
    province_code = request.form['province']
    city_code = request.form['city']
    barangay_code = request.form['barangay']
    street = request.form['street']
    zip_code = request.form['zip']

    # Convert codes to full names
    province_name = get_province_name(province_code)
    city_name = get_city_name(province_code, city_code)
    barangay_name = get_barangay_name(city_code, barangay_code)

    courier_id = session['courier_id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cur.execute("""
            UPDATE courier 
            SET province = %s, city = %s, barangay = %s, street = %s, zip_code = %s
            WHERE id = %s
        """, (province_name, city_name, barangay_name, street, zip_code, courier_id))
        mysql.connection.commit()
        flash("Address updated successfully!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error updating address: {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('courier_account'))












if __name__ == "__main__":
    app.run(debug=True)

