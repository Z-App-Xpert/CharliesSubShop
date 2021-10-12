# Charlie's Coffee and Sandwich Shop

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This website provides time estimates of inventory delivery for a small food vendor doing business within the city of Boson's subway system.  The vendor delivers the inventory on the subway so it uses Google's direction API to manage inventory arrival times.  Python, Flask, JavaScript, JSON, Socket.IO, HTML5 and CSS will drive the application.  The database is Sqlite and will manage the logins, cart registrations, and inventory tracking.

**User names and passwords**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;User names and passwords are located at the very bottom of this readme document.

**Business functional specification**

**Summary:**
	Charlie has an amazing sandwich shop that serves meals from 5 am to 6 pm. Charlie must keep his inventory storage and shop rental costs low, so he places vendor carts around the city of Boston’s subway system.  He has a shop located at Downtown Crossing that holds the main supply of inventory.  Each cart can only hold a certain amount of product.  Sales at each location range from 30 to 100 sandwiches a day and 20 lbs. of coffee per day.

**Problem:**
	Charlie must use the subway system to deliver inventory to the vendor carts located around the city.  The vendor must know whether his inventory will arrive on time; otherwise, they have to close down, or be able to manage the customer expectations of when the sandwiches or coffee will arrive.

**Requirements for solution:**
* Create a communication system between the vendor carts and shop to monitor inventory.
* It will have a username and login page
* Registration of location for the vendor station
* Python, Flask, JavaScript, JSON, Socket.IO, HTML5 and CSS will drive the application.  Sqlite will manage the logins, cart registrations, and inventory tracking.
* Implementation of Bootstrap 4’s mobile responsiveness allows the vendor carts to use their smart phones to communicate.
* The vendor’s have a simple interface that communicates the total number of meals needed from the shop
* When the inventory of coffee or sandwiches falls to a level where the vendor must order they do so through a simple ordering interface on their smart phone.  Both Coffee and Sandwiches are ordered to bring the cart back up to the highest inventory level.
* Google's directions API is used to communicate to the vender for time of delivery.  The use of this API is key to the communication system.  A message displays to the vendor cart about arrival time.  A countdown then displays on the vendor’s phone to track arrival time. The API information is located at https://developers.google.com/maps/documentation/directions/start
* Once the delivery is made, the vendor marks it complete and the shop's inventory is marked as inventory sold.
* The address used to register the vendor or shop is an autocomplete dropdown found with the 'geocomplete()' package from Google to assure an address is picked from their map services.

## Key Components and Design

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This website consists of several pages: index, layout, login, register, and route. It also has a script.js and style.css in the static folder. It has a Flask framework and an application.py file.  The database name is shop.db and is sqlite.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;At first sign on to the website a database is created with an inventory and user schema.  On subsequent sign-ins, if the database is present, then it will not re-build.  If there are any previous sales in inventory for any vendor, then the data is fetched.  Next the User is presented with a Login and Registration choice on the index page.

**Index.html**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-If the user is not logged in, then the Login and Register buttons appear on the page.  If Login is clicked then the Login page opens, and if Register is clicked, then the Register page opens.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-If the session type is 'shop', then for each vendor in the database the item and value are displayed for sandwiches sold, coffee sold and current deliveries pending delivery.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-If the session type is 'vendor', then the order-div is displayed for the vendor to order sandwiches and coffee.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The index page also is home to the timer which counts down the time for delivery and the button with the ability to mark the order as complete.  These two classes are not displayed until an order is placed or marked complete.

**Login.html**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Login is POST encode the request and assure information is not leaked to the user when submitted, otherwise the login page will display again.  On a successful POST method the User schema is queried to determine if they are a registered user, then the session boolean value for logged_in will be marked as true and the session type will be marked with either 'shop' or 'vendor' and then redirected to the index page.

**Register.html**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Register is POST. User enters their name, email, password, whether a shop or a vendor and then their address.  The current business rule for address is that the vendor must enter a valid subway stop.  In order to help choose the address, the google geocomplete() function is used with the google API to get a valid map address with the 'input2AddressForm' variable. When the user clicks register, then application.py will check if it is a shop type, the name exists in the table, and if it is a new user, then the data is committed to the table, the session is marked 'Registered' and the user redirected back to the login.html page.

**Route.html**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This page shows the MBTA subway routes.

## Interactions between Python and JavaScript

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Once the Shop and the Vendors are in place, an order of inventory is placed for delivery.  The vendor places an order on the order screen, they 'click' the submit order button.  This triggers the orderForm.addEventListener event, and we send the 'order' data to application.py through the web-socket.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Now the socketio.on("order") takes over in application.py, commits the data to the inventory table, and then updates the index.html page through the javascript file at 'socket.on('update_table'...)'. Also in the application.py the time to deliver from the Shop (Downtown Crossing) to the vendor cart is calculated using the Google Directions API, then the 'time' is passed back to the JavaScript file through the socketio.emit("timer", time) and updates the time that it will take to deliver in the JavaScript at 'socket.on('timer', (time) => {.'  This time string is updated in the element with id="timer" for the class = "timer" in the index.html page.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;So depending on whether you are the the vendor or the shop you see two different views.  The vendor sees the clock counting down to their estimated delivery time. The shop sees that there is a current delivery in progress. See Illustration 1.

**Illustration 1**
* Shows the Shop on the left and the Vendor on the right.  The vendor has just ordered 15 Sandwiches and 5 pounds of coffee, so the shop sees this in the Current Delivery line.  The Vendor can see the clock counting down for the time it takes to get from Downtown Crossing to Ashmont.
![IMAGE](RDMEimg/CurrentOrderPendingDelivery.png) 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From here the vendor would mark the the order as delivered, so the 'Current Delivery' is set to NULL, at this point the JaviScript is listening for the 'click' event of the markButton and when it is true the listener named 'markButton.addEventListener('click', (event) =>' is triggered and the 'clearInterval' function is run to stop the timer. The 'timer' and 'mark' areas on the HTML are set to d-none to reset the cart view, and then the 'delivered' message is emitted back to application.py.  In the application.py the 'shop_status' function is run to update and commit the data changes to the inventory schema, and then emits the 'reset_current' back to JavaScript to reset the current line to Null. This shows the vendor there is not a current delivery in progress. See Illustration 2.

 **Illustration 2**
 * Shows the Shop on the left and the Vendor on the right.  The vendor has just clicked the 'Mark as Delivered' button which changes their view back to order mode. The shop view changes to show the inventory change of more product sold and the current delivery in progress is set to Null.
 ![IMAGE](RDMEimg/OrderMarkedasDelivered2.png) 


##  Scalability

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Should this app expand to more subway systems and gain a million users with data in the terabytes, then a valid move is to use postgres/mysql for the database. Heroku can be used for either postgres or mysql. Flask is fine for scalability and move to Django is not required. 

## User names and passwords

## Shop 

- Email - shop@final.com
- Password - shop

## There are 4 Vendors

### Vendor A
- Email - vendor_a@final.com
- Password - vendor_a

### Vendor B
- Email - vendor_b@final.com
- Password - vendor_b

### Vendor C
- Email - vendor_c@final.com
- Password - vendor_c

### Vendor D
- Email - vendor_d@final.com
- Password - vendor_d

**Sources**

https://www.w3schools.com/jsref/met_win_clearinterval.asp
https://developers.google.com/maps/documentation/directions/start
