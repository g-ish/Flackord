document.addEventListener('DOMContentLoaded', () => {


    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, get message and emit
    socket.on('connect', () => {

        // Sends message when user enters the channel
        socket.emit('join')

        // Gets and sends the message to flask
        $('form#send_message').submit(function (event) {
            message = document.getElementById('message').value
            socket.emit('send_message', {'message': message});


            // Clears input text after sending message
            document.getElementById('message').value = '';
            return false;
        });

        document.getElementById('leave').onclick = function () {
            console.log('Leaving...');
            socket.emit('leave');
            localStorage.removeItem('channel');
            window.location.replace('/');
        };
    });

    // When a new message is received, add to the 'messages' list
    socket.on('relay message', data => {

        const message = document.createElement('div');
        message.style.display = 'inline';
        message.className = 'list-group-item';
        message.innerHTML = `<span style="font-weight:600; font-size: 1.1em; color: #326390">
                   ${data.username} - </span> ${data.message}
                    <span style="font-size: 0.75em; color: #999DA8"> ${data.timestamp}</span>`
        document.querySelector('#chat_messages').append(message);


        // Scrolls to ensure latest message is shown w/o scroll input from user
        const chat_box = document.getElementById('chat_box');
        chat_box.scrollBy(0, 100)
    });

});




