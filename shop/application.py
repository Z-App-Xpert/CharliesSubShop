import os
import json
import urllib.parse as urllib
from flask import Flask, request, session, render_template, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_socketio import SocketIO, emit
import gevent.monkey
gevent.monkey.patch_all()
import requests

app = Flask(__name__)
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "shop.db"))
engine = create_engine(database_file)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# Class to store the user schema
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50), unique=True)
    type = Column(String(50))
    address = Column(String(100))
    password = Column(String(100))

    def __init__(self, name, email, password, user_type, address):
        self.name = name
        self.address = address
        self.email = email
        self.type = user_type
        self.password = password


# Class to store the inventory schema
class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    vendor = Column(String(50), ForeignKey('users.email'))
    sandwich = Column(Integer, default=0)
    coffee = Column(Float, default=0)
    current = Column(String(100), default='-')

    def __init__(self, vendor, sandwich, coffee, current):
        self.vendor = vendor
        self.sandwich = sandwich
        self.coffee = coffee
        self.current = current


# Object that represents a socket connection
class Socket:
    def __init__(self, sid):
        self.sid = sid
        self.connected = True

    # Emits data to a socket's unique room
    def emit(self, event, data):
        emit(event, data, room=self.sid)


# dictionary to hold the inventory
inventory = {}

# holds the socket object for the shop
shop_socket = None


# function to fetch the inventory from the database and initialize it.
def build_inventory():
    vendors = User.query.filter_by(type='vendor')
    for vendor in vendors:
        data = Inventory.query.filter_by(vendor=vendor.email).first()
        if not data:
            data = Inventory(
                vendor=vendor.email,
                sandwich=0,
                coffee=0,
                current='-'
            )
            db_session.add(data)
            db_session.commit()
        else:
            inventory[vendor.email] = {'sandwich': data.sandwich,
                                       'coffee': data.coffee,
                                       'current': data.current}


# route for the index page
@app.route('/')
def index():
    # set the logged in status
    if 'logged_in' not in session:
        session['logged_in'] = False

    # if logged in as shop
    if session['logged_in'] and session['type'] == 'shop':
        # building inventory and vendor data into vendor_list
        vendor_list = []
        vendors = User.query.filter_by(type='vendor')
        for vendor in vendors:
            vendor_list.append({'vendor': vendor, 'inventory': inventory[vendor.email]})
        return render_template("index.html", vendor_list=vendor_list)

    # else render template
    return render_template("index.html")


# route for the subway routes page
@app.route('/route')  
def route():  
    return render_template("route.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if login page is accessed
    if request.method == 'GET':
        session['error'] = ''
        return render_template('login.html')
    # else the form is submitted
    else:
        # get the data
        email = request.form['email']
        passw = request.form['password']

        # login the user
        try:
            data = User.query.filter_by(email=email, password=passw).first()
            if data is not None:
                session['logged_in'] = True
                session['name'] = data.name
                session['type'] = data.type
                session['address'] = data.address
                session['email'] = email
                session['error'] = ''
                return redirect(url_for('index'))
            else:
                session['error'] = 'Invalid credentials'
                return render_template('login.html')
        except OperationalError as e:
            session['error'] = 'Database Error in login'
            print(session['error'], e)
            return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # if register form is submitted
    if request.method == 'POST':
        # get the data
        if request.form['name'] == '' or \
                request.form['email'] == '' or \
                request.form['password'] == '' or \
                request.form['address'] == '' or \
                request.form['type'] == '':
            session['error'] = 'Invalid Parameters'
            return render_template('register.html')

        # register
        try:
            # check if shop already exists
            if request.form['type'] == 'shop':
                shop_exists = User.query.filter_by(type='shop').first()
                if shop_exists:
                    session['error'] = 'Shop already exists'
                    return render_template('register.html')
            # else register
            new_user = User(
                name=request.form['name'],
                email=request.form['email'],
                password=request.form['password'],
                address=request.form['address'],
                user_type=request.form['type'])

            db_session.add(new_user)
            db_session.commit()
            session['success'] = 'Registered'
            return redirect(url_for('login'))
        except OperationalError as e:
            session['error'] = 'Database Error in register'
            print(session['error'], e)
            return render_template('register.html')

    session['error'] = ''
    return render_template('register.html')


# route for logout
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))


# on socket connection if type is shop, store the socket object.
@socketio.on('connected')
def socket_init(user_type):
    global shop_socket
    if user_type == 'shop':
        shop_socket = Socket(request.sid)


# on order, update the inventory calculate the time it will take
# and emit a timer event to create the timer countdown on the vendor page.
@socketio.on("order")
def order(data):
    # get the data from the database
    shop = User.query.filter_by(type='shop').first()
    vendor = User.query.filter_by(email=data['vendor']).first()
    db_inventory = Inventory.query.filter_by(vendor=vendor.email).first()
    shop_address = shop.address

    # build the current order string.
    data['current'] = 'Sandwiches: '+data['sandwich']+', Coffee: '+data['coffee']

    # update inventory as well as data as data is used to update tables in shop
    inventory[data['vendor']]['sandwich'] += int(data['sandwich'])
    data['sandwich'] = inventory[data['vendor']]['sandwich']
    db_inventory.sandwich = data['sandwich']
    db_session.commit()

    inventory[data['vendor']]['coffee'] += float(data['coffee'])
    data['coffee'] = inventory[data['vendor']]['coffee']
    db_inventory.coffee = data['coffee']
    db_session.commit()

    inventory[data['vendor']]['current'] = data['current']
    db_inventory.current = data['current']
    db_session.commit()

    # arguments for the API call to google directions API
    args = {
        'origin': shop_address,
        'destination': vendor.address,
        'mode': 'transit',
        'transit_mode': 'subway',
        'key': 'AIzaSyDOX5D1bG9j6pKTDyGVSVQSv_SLJHL0IUk'
    }
    # url to call
    url = "https://maps.googleapis.com/maps/api/directions/json?" + urllib.urlencode(args)

    # call the API
    resp = requests.get(url)

    # parse the response
    time = json.loads(resp.content)

    # read time from the response
    time = time["routes"][0]["legs"][0]["duration"]["value"]

    # if shop is connected, emit update table to update the data for the vendor
    if shop_socket:
        shop_socket.emit("update_table", data=data)
    socketio.emit("timer", time)


# when mark as delivered button is clicked, we reset the current status in the python app...
# ...and in the database and emit a reset_current event to the shop to update it in the table...
# ...on the shop account as well.
@socketio.on("delivered")
def shop_status(data):
    vendor = User.query.filter_by(email=data['vendor']).first()
    db_inventory = Inventory.query.filter_by(vendor=vendor.email).first()
    db_inventory.current = '-'
    db_session.commit()

    inventory[data['vendor']]['current'] = '-'
    if shop_socket:
        shop_socket.emit("reset_current", data=data)


# Run the app
if __name__ == "__main__":
    # create database
    Base.metadata.create_all(bind=engine)

    # build/fetch inventory
    build_inventory()

    # run the app
    socketio.run(app=app)
