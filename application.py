import os

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Todo: Figure out best ds for this
# Dict of channels, format:
# channel_name: name
# messages: {
# message:
# user:
# }

# Todo: Ideas: Giphy integration, favorite channels, channel category (nature etc)

# channels[channel_name][username][message]
channels = {}
users = []

@app.route("/", methods=['GET', 'POST'])
def index():
    # Check if user has already created a username, if so redirect to homepage
    if session.get('username') is not None:
        username = session['username']
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            username = request.form.get('username')

            if username not in users:
                users.append(username)
                session['username'] = username
                session.permanent = True
                return redirect(url_for('home'))
            else:
                flash("Username already exists!")
                return render_template('index.html')
        else:
            return render_template('index.html')

@app.route("/home", methods=['GET','POST'])
def home():
    # Locks homepage if no username found in session.
    if session.get('username') is None:
        flash("Please enter a username!")
        return render_template('index.html')

    # Sets scope for username
    username = ''

    # Creates object with channel details including channel list, user count and message count.
    channel_list = []
    for each_channel in channels:
        index = 0
        user_count = len(channels[each_channel].keys())
        for each_user in channels[each_channel].keys():
            message_count = len(channels[each_channel][each_user].keys())
            channel_item = {'index': index,
                        'channel_name': each_channel,
                        'user_count': user_count,
                        'message_count': message_count}
            channel_list.append(channel_item)
        index+=1

    else:
        username = session['username']
        if request.method == 'POST':
            channel_name = request.form.get('channel_name')
            if channel_name in channels.keys():
                flash("Channel name already exists, pick a new one!")
                return redirect(url_for('home'))
            else:
                channels[channel_name] = { username: {}  }

                # Todo: Change message function to socketio
                channels[channel_name][username] = {'message': username + ' has created the room'
                }

                return redirect(url_for('channel', channel_id=channel_name))
    return render_template('home.html', username=username, channel_list=channel_list)

@app.route("/channel/<channel_id>", methods = ['GET'])
def channel(channel_id):
    if session.get('username') is None:
        flash("Please enter a username!")
        return render_template('index.html')
    username = session['username']

    # Adds user to channel, creates dict for user's messages.
    # Todo: change timestamp or switch this entirely over to a web socket message
    if request.method == 'GET':

        channels[channel_id][username] = {'timestamp': username + ' has joined the room'}
    messages = channels[channel_id].keys()
    return render_template('channel.html', channel_id=channel_id, username=username, messages = messages)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@socketio.on("send message")
def message(data):
    aMessage = data['message']
    emit('relay message', aMessage, broadcast=true)
