import os

from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from Channel import Channel
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Todo: Ideas: Giphy integration, favo-
#  rite channels, channel category (nature etc)

users = []
channels = {}


@app.route("/", methods=['GET', 'POST'])
def index():
    # Check if user has already created a username, if so redirect to homepage
    if session.get('username') is not None:
        return redirect(url_for('home'))
    else:
        session.clear()
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


@app.route("/home", methods=['GET', 'POST'])
def home():
    # Locks homepage if no username found in session.
    if session.get('username') is None:
        flash("Please enter a username!")
        return render_template('index.html')

    username = session['username']

    # Creates a channel
    if request.method == 'POST':
        channel_name = request.form.get('channel_name')
        if channel_name in channels:
            flash("Channel name already exists, pick a new one!")
            return redirect(url_for('home'))
        new_channel = Channel(channel_name)
        channels[channel_name] = new_channel
        session['channel'] = channel_name
        return redirect(url_for('channel', channel_name=channel_name))


    # Redirects when user leaves channel
    if request.method == 'GET':
        if session.get('channel') is None:
            print("No Channel found")
            return render_template('home.html', username=username, channel_list=channels)
        else:
            channel_name = session.get('channel')
            return redirect(url_for('channel', channel_name=channel_name))

    elif session.get('channel') is not None:
        channel_name = session.get('channel')
        if channel_name in channels:
            return redirect(url_for('channel', channel_name=channel_name))
        else:
            session['channel'] = None
            return redirect(url_for('home'))


# Create a checker function in /home to forward a user to the last channel they were on.
@app.route("/channel/<channel_name>", methods=['GET'])
def channel(channel_name):

    if session.get('username') is None:
        flash("Please enter a username!")
        return render_template('index.html')
    username = session['username']

    try:
        session['channel'] = channel_name
        prev_messages = []
        for i in range(len(channels[channel_name].messages)):
            prev_messages.append(channels[channel_name].messages[i])
            if i == 99:
                break

        return render_template('channel.html', channel_name=channel_name, username=username, prev_messages=prev_messages)

    # Give user opportunity to back to home if they access a channel which has been deleted or doesn't exist.
    except KeyError:
        error = "Channel not found"
        session.pop('channel')
        return render_template('error.html', error=error)


@app.route("/logout")
def logout():
    users.remove(session['username'])
    session.clear()
    return redirect(url_for('index'))


# Prevents users from trying to use /channel as a directory instead of home.
@app.route('/channel')
def channel_direct():
    return redirect(url_for('home'))


######### Socketio functions #######


@socketio.on('send_message')
def handle_message(data):
    message = data['message']
    username = session['username']
    timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M")
    channel_name = session['channel']

    channels[channel_name].new_message(channel_name, username, timestamp, message)
    if len(channels[channels_name].messages) > 100:
        channels[channels_name].messages.popleft()

    emit('relay message', {"username": username, "message": message, "timestamp": timestamp}, broadcast=True)

@socketio.on('join')
def on_join():
    try:
        username = session['username']
        room = session['channel']
        timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M")
        message = "has entered the channel."
        join_room(room)
        channels[room].new_message(room, username, timestamp, message)
        emit('relay message', {"username": username, "message": "has entered the channel.", "timestamp": timestamp}, broadcast=True)
    except KeyError:
        error = "Channel not found"
        return render_template('error.html', error=error)



@socketio.on('leave')
def on_leave():
    username = session['username']
    timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M")

    leave_room(room)
    emit('relay message', {"username": username, "message": " has left the channel.", "timestamp": timestamp}, broadcast=True)





