import sqlite3


class User:

    def __init__(self, _id, username, password, phone_number, safe_time_start, safe_time_end, safe_ip, safe_latitude, safe_longitude):
        self._id = _id
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.safe_time_start = safe_time_start
        self.safe_time_end = safe_time_end
        self.safe_ip = safe_ip
        self.safe_latitude = safe_latitude
        self.safe_longitude = safe_longitude

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE username =?"
        result = cursor.execute(query, (username,))
        row = result.fetchone()

        connection.close()

        if row:
            user = cls(*row)
            return user
        return None

