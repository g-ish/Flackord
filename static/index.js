  document.addEventListener('DOMContentLoaded', () => {

      // Connect to websocket
      var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

      // When connected, configure buttons
      socket.on('connect', () => {

          // Each button should emit a "submit vote" event
          document.querySelectorAll('button').forEach(button => {
              button.onclick = () => {
                  const message = button.dataset.message;
                  socket.emit('send message', {'message': message});

              };
          });
      });

      // When a new vote is announced, add to the unordered list
      socket.on('relay message', data => {
          const li = document.createElement('li');
          li.innerHTML = `Username(test): ${data.message}`;
          document.querySelector('#messages').append(li);
      });
  });