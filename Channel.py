class Channel:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.messages = []

    def new_message(self, channel_name, username, timestamp, message):
        aMessage = {"channel_name": channel_name,
                    "username": username,
                    "timestamp": timestamp,
                    "message": message}
        self.messages.append(aMessage)
