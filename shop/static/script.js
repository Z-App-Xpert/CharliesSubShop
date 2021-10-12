document.addEventListener('DOMContentLoaded', () => {
    // socket.io connection
    let socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    timer_interval = '';

    // on socket.io load
	socket.on('connect', () => {
        socket.emit('connected', type);

		// handle submission of order form
        let orderForm = document.querySelector('.orderForm');
        let markButton = document.getElementById("mark-button");

        // if order form exist on page i.e it is a vendor and the order form is submitted
        // we send the order data to the python app through the web-socket
        if(orderForm){
            orderForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const vendor = document.querySelector("input[name=vendor]").value;
                const sandwich = document.querySelector("#SandwichInput").value;
                const coffee = document.querySelector("#CoffeeInput").value;
                let data = {'sandwich': sandwich,
                            'coffee': coffee,
                            'vendor': vendor
                };

                socket.emit('order', data);
            });
        }

        // if mark as delivered button exists on page then on clicking the button we stop the timer
        // hide the button and show the order form again. and send the message to python app to clear the
        // current delivery status.
		if(markButton){
		    markButton.addEventListener('click', (event) => {
                event.preventDefault();
                clearInterval(timer_interval);

                document.getElementById("timer").classList.add('d-none');
                document.getElementById("mark").classList.add('d-none');

                document.querySelector('.orderForm').reset();
                document.getElementById("order-div").classList.remove('d-none');

                let data = {'vendor': markButton.getAttribute('data-vendor')};
                socket.emit('delivered', data);
            });
        }
    });

	// When order is submitted python app will emit a update table event with new data
    // So we update the update for the vendor as per the new data
	socket.on('update_table', data => {
        document.querySelector('table[data-vendor="' + data.vendor + '"] .sandwich_row td:last-child').innerHTML = data.sandwich;
        document.querySelector('table[data-vendor="' + data.vendor + '"] .coffee_row td:last-child').innerHTML = data.coffee + ' lbs';
        document.querySelector('table[data-vendor="' + data.vendor + '"] .current_row td:last-child').innerHTML = data.current;
    });

	// When order is delivered python app will emit the reset current event
    // We clear the current delivery status for the vendor.
	socket.on('reset_current', data => {
        document.querySelector('table[data-vendor="' + data.vendor + '"] .current_row td:last-child').innerHTML = '-';
    });

	// When an order is received, python app finds the time it will take for delivery
    // and sends the time by emitting a timer event. We create a timer countdown and
    // hide the order form and show the mark as delivered button
	socket.on('timer', (time) => {
	    if(type === 'vendor') {
            document.getElementById("order-div").classList.add('d-none');
            document.getElementById("timer").classList.remove('d-none');
            document.getElementById("mark").classList.remove('d-none');
            // Set the date we're counting down to
            let countDownDate = new Date(new Date().valueOf() + (time * 1000)).getTime();
		
            // Update the count down every 1 second
            timer_interval = setInterval(function () {
                // Get current date and time
                let now = new Date().getTime();

                // Find the distance between now and the count down date
                let distance = countDownDate - now;

                // Time calculations for days, hours, minutes and seconds
                let days = Math.floor(distance / (1000 * 60 * 60 * 24));
                let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                let seconds = Math.floor((distance % (1000 * 60)) / 1000);

                // building the timer string
                let update_str = "";
                if (days !== 0) {
                    update_str += days + "d "
                }

                if (hours !== 0) {
                    update_str += hours + "h "
                }

                if (minutes !== 0) {
                    update_str += minutes + "m "
                }

                if (seconds !== 0) {
                    update_str += seconds + "s"
                }

                // Display the result in the element with id="timer"
                document.getElementById("timer").innerHTML = update_str;

                // If the count down is finished, hide the timer
                if (distance < 0) {
                    clearInterval(timer_interval);
                    document.getElementById("timer").innerHTML  = '';
                    document.getElementById("timer").classList.add('d-none');
                }
            // this interval runs every 1000 milliseconds i.e every second.
            }, 1000);
        }
    });
});
