# app.py


from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from config import Config
from forms import ManagerForm, ClientForm, CarForm, ModelForm, DriverForm, RentForm

app = Flask(__name__)
app.config.from_object(Config)

# Function to connect to the database
def get_db_connection():
    conn = psycopg2.connect(
        dbname="taxi_rental_db",
        user="postgres",  
        password="Wrongturn",  
        host="localhost",
        port="5432"
    )
    return conn

# Landing page
@app.route('/')
def index():
    return render_template('index.html')

# Manager login
@app.route('/manager/login', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        ssn = request.form['ssn']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM MANAGER WHERE ssn = %s', (ssn,))
        manager = cur.fetchone()
        cur.close()
        conn.close()

        if manager:
            session['user_type'] = 'manager'
            session['user_id'] = ssn
            flash('Login successful!', 'success')
            return redirect(url_for('manager_dashboard'))
        else:
            flash('Invalid SSN. Please try again or register.', 'error')
    return render_template('manager_login.html')

# Manager registration
@app.route('/manager/register', methods=['GET', 'POST'])
def manager_register():
    form = ManagerForm()
    if form.validate_on_submit():
        ssn = form.ssn.data
        name = form.name.data
        email = form.email.data

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO MANAGER (ssn, name, email) VALUES (%s, %s, %s)',
                (ssn, name, email)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('manager_login'))
        except psycopg2.Error as e:
            conn.rollback()
            flash('Error: SSN already exists or invalid data.', 'error')
        finally:
            cur.close()
            conn.close()
    return render_template('manager_register.html', form=form)

# Manager dashboard
@app.route('/manager/dashboard', methods=['GET', 'POST'])
def manager_dashboard():
    if session.get('user_type') != 'manager':
        flash('Please log in as a manager.', 'error')
        return redirect(url_for('manager_login'))

    # Forms for adding car, model, and driver
    car_form = CarForm()
    model_form = ModelForm()
    driver_form = DriverForm()

    # Handle form submissions
    if request.method == 'POST':
        # Check which form was submitted by validating each form
        if car_form.validate_on_submit():
            carid = car_form.carid.data
            brand = car_form.brand.data
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    'INSERT INTO CAR (carid, brand) VALUES (%s, %s)',
                    (carid, brand)
                )
                conn.commit()
                flash('Car added successfully!', 'success')
            except psycopg2.Error as e:
                conn.rollback()
                flash('Error: Car ID already exists or invalid data.', 'error')
            finally:
                cur.close()
                conn.close()

        elif model_form.validate_on_submit():
            carid = model_form.carid.data
            color = model_form.color.data
            construction_year = model_form.construction_year.data
            transmission = model_form.transmission.data
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    'INSERT INTO MODEL (carid, color, construction_year, transmission) VALUES (%s, %s, %s, %s)',
                    (carid, color, construction_year, transmission)
                )
                conn.commit()
                flash('Model added successfully!', 'success')
            except psycopg2.Error as e:
                conn.rollback()
                flash('Error: Car ID must exist in CAR table or invalid data.', 'error')
            finally:
                cur.close()
                conn.close()

        elif driver_form.validate_on_submit():
            drivername = driver_form.drivername.data
            email = driver_form.email.data
            address_road = driver_form.address_road.data
            address_number = driver_form.address_number.data
            address_city = driver_form.address_city.data

            conn = get_db_connection()
            cur = conn.cursor()
            try:
                # Insert driver
                cur.execute(
                    'INSERT INTO DRIVER (drivername, email) VALUES (%s, %s)',
                    (drivername, email)
                )

                # Insert address
                cur.execute(
                    'INSERT INTO ADDRESS (road, number, city) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
                    (address_road, address_number, address_city)
                )

                # Link driver to address
                cur.execute(
                    'INSERT INTO DRIVER_LIVES_AT (drivername, address_road, address_number, address_city) VALUES (%s, %s, %s, %s)',
                    (drivername, address_road, address_number, address_city)
                )

                conn.commit()
                flash('Driver added successfully!', 'success')
            except psycopg2.Error as e:
                conn.rollback()
                flash(f'Error: {str(e)}', 'error')
            finally:
                cur.close()
                conn.close()

        return redirect(url_for('manager_dashboard'))

    # Fetch all cars, models, and drivers for display
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM CAR')
    cars = cur.fetchall()
    cur.execute('SELECT * FROM MODEL')
    models = cur.fetchall()
    cur.execute('SELECT d.drivername, d.email, dla.address_road, dla.address_number, dla.address_city '
                'FROM DRIVER d LEFT JOIN DRIVER_LIVES_AT dla ON d.drivername = dla.drivername')
    drivers = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('manager_dashboard.html', car_form=car_form, model_form=model_form, 
                           driver_form=driver_form, cars=cars, models=models, drivers=drivers)

# Remove car
@app.route('/manager/remove_car/<int:carid>', methods=['POST'])
def remove_car(carid):
    if session.get('user_type') != 'manager':
        flash('Please log in as a manager.', 'error')
        return redirect(url_for('manager_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM CAR WHERE carid = %s', (carid,))
        conn.commit()
        flash('Car removed successfully!', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error: Cannot remove car due to dependencies.', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('manager_dashboard'))

# Remove model
@app.route('/manager/remove_model/<int:carid>', methods=['POST'])
def remove_model(carid):
    if session.get('user_type') != 'manager':
        flash('Please log in as a manager.', 'error')
        return redirect(url_for('manager_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM MODEL WHERE carid = %s', (carid,))
        conn.commit()
        flash('Model removed successfully!', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error: Cannot remove model due to dependencies.', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('manager_dashboard'))

# Remove driver
@app.route('/manager/remove_driver/<drivername>', methods=['POST'])
def remove_driver(drivername):
    if session.get('user_type') != 'manager':
        flash('Please log in as a manager.', 'error')
        return redirect(url_for('manager_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM DRIVER WHERE drivername = %s', (drivername,))
        conn.commit()
        flash('Driver removed successfully!', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash('Error: Cannot remove driver due to dependencies.', 'error')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('manager_dashboard'))

# Driver report (total rents and average rating)
@app.route('/manager/driver_report')
def driver_report():
    if session.get('user_type') != 'manager':
        flash('Please log in as a manager.', 'error')
        return redirect(url_for('manager_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT d.drivername, COUNT(r.rentid) as total_rents, AVG(rw.rating) as avg_rating '
                'FROM DRIVER d '
                'LEFT JOIN RENT r ON d.drivername = r.drivername '
                'LEFT JOIN REVIEW rw ON d.drivername = rw.drivername '
                'GROUP BY d.drivername')
    driver_stats = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('driver_report.html', driver_stats=driver_stats)

# Model report (number of rents)
@app.route('/manager/model_report')
def model_report():
    if session.get('user_type') != 'manager':
        flash('Please log in as a manager.', 'error')
        return redirect(url_for('manager_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT m.carid, m.color, m.construction_year, m.transmission, COUNT(r.rentid) as total_rents '
                'FROM MODEL m '
                'LEFT JOIN RENT r ON m.carid = r.carid '
                'GROUP BY m.carid, m.color, m.construction_year, m.transmission')
    model_stats = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('model_report.html', model_stats=model_stats)

# Client login
@app.route('/client/login', methods=['GET', 'POST'])
def client_login():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM CLIENT WHERE email = %s', (email,))
        client = cur.fetchone()
        cur.close()
        conn.close()

        if client:
            session['user_type'] = 'client'
            session['user_id'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('client_dashboard'))
        else:
            flash('Invalid email. Please try again or register.', 'error')
    return render_template('client_login.html')

# Client registration
@app.route('/client/register', methods=['GET', 'POST'])
def client_register():
    form = ClientForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        address_road = form.address_road.data
        address_number = form.address_number.data
        address_city = form.address_city.data
        credit_card_number = form.credit_card_number.data
        credit_card_road = form.credit_card_road.data
        credit_card_number_field = form.credit_card_number_field.data
        credit_card_city = form.credit_card_city.data

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Insert client
            cur.execute(
                'INSERT INTO CLIENT (email, name) VALUES (%s, %s)',
                (email, name)
            )

            # Insert address
            cur.execute(
                'INSERT INTO ADDRESS (road, number, city) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
                (address_road, address_number, address_city)
            )

            # Link client to address
            cur.execute(
                'INSERT INTO CLIENT_LIVES_AT (client_email, address_road, address_number, address_city) VALUES (%s, %s, %s, %s)',
                (email, address_road, address_number, address_city)
            )

            # Insert credit card address (if different)
            cur.execute(
                'INSERT INTO ADDRESS (road, number, city) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
                (credit_card_road, credit_card_number_field, credit_card_city)
            )

            # Insert credit card
            cur.execute(
                'INSERT INTO CREDIT_CARD (credit_card_number, client_email, address_road, address_number, address_city) VALUES (%s, %s, %s, %s, %s)',
                (credit_card_number, email, credit_card_road, credit_card_number_field, credit_card_city)
            )

            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('client_login'))
        except psycopg2.Error as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            cur.close()
            conn.close()
    return render_template('client_register.html', form=form)

# Client dashboard (placeholder)
# Client dashboard
@app.route('/client/dashboard', methods=['GET', 'POST'])
def client_dashboard():
    if session.get('user_type') != 'client':
        flash('Please log in as a client.', 'error')
        return redirect(url_for('client_login'))

    form = RentForm()
    available_models = []
    selected_date = None
    client_email = session['user_id']

    # Handle form submission
    if form.validate_on_submit():
        selected_date = form.date.data

        if form.submit_view.data:  # View available models
            conn = get_db_connection()
            cur = conn.cursor()

            # Find models that are not rented on the selected date
            # and have at least one driver who can drive them and is not booked
            cur.execute('''
                SELECT m.carid, m.color, m.construction_year, m.transmission
                FROM MODEL m
                WHERE m.carid NOT IN (
                    SELECT r.carid
                    FROM RENT r
                    WHERE r.date = %s
                )
                AND EXISTS (
                    SELECT 1
                    FROM CAN_DRIVE cd
                    JOIN DRIVER d ON cd.drivername = d.drivername
                    WHERE cd.carid = m.carid
                    AND d.drivername NOT IN (
                        SELECT r2.drivername
                        FROM RENT r2
                        WHERE r2.date = %s
                    )
                )
            ''', (selected_date, selected_date))
            available_models = cur.fetchall()

            # Update the carid choices in the form
            form.carid.choices = [(model[0], f"Car ID: {model[0]} - {model[1]} ({model[2]}, {model[3]})") 
                                  for model in available_models]

            cur.close()
            conn.close()

        elif form.submit_book.data:  # Book a rent
            carid = form.carid.data

            conn = get_db_connection()
            cur = conn.cursor()

            # Check if the selected model is still available
            cur.execute('''
                SELECT m.carid
                FROM MODEL m
                WHERE m.carid = %s
                AND m.carid NOT IN (
                    SELECT r.carid
                    FROM RENT r
                    WHERE r.date = %s
                )
                AND EXISTS (
                    SELECT 1
                    FROM CAN_DRIVE cd
                    JOIN DRIVER d ON cd.drivername = d.drivername
                    WHERE cd.carid = m.carid
                    AND d.drivername NOT IN (
                        SELECT r2.drivername
                        FROM RENT r2
                        WHERE r2.date = %s
                    )
                )
            ''', (carid, selected_date, selected_date))
            model_available = cur.fetchone()

            if not model_available:
                flash('Selected model is no longer available on this date.', 'error')
            else:
                # Find an available driver who can drive the selected model
                cur.execute('''
                    SELECT d.drivername
                    FROM DRIVER d
                    JOIN CAN_DRIVE cd ON d.drivername = cd.drivername
                    WHERE cd.carid = %s
                    AND d.drivername NOT IN (
                        SELECT r.drivername
                        FROM RENT r
                        WHERE r.date = %s
                    )
                    LIMIT 1
                ''', (carid, selected_date))
                driver = cur.fetchone()

                if driver:
                    drivername = driver[0]
                    # Generate a new rentid (simple increment for this example)
                    cur.execute('SELECT COALESCE(MAX(rentid), 0) + 1 FROM RENT')
                    rentid = cur.fetchone()[0]

                    # Book the rent
                    cur.execute(
                        'INSERT INTO RENT (rentid, date, drivername, carid, client_email) VALUES (%s, %s, %s, %s, %s)',
                        (rentid, selected_date, drivername, carid, client_email)
                    )
                    conn.commit()
                    flash('Rent booked successfully!', 'success')
                else:
                    flash('No available drivers for this model on the selected date.', 'error')

            cur.close()
            conn.close()
            return redirect(url_for('client_dashboard'))

    return render_template('client_dashboard.html', form=form, available_models=available_models, selected_date=selected_date)


# Logout
@app.route('/logout')
def logout():
    session.pop('user_type', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)