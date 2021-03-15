from db import db


class UserModel(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    phone_number = db.Column(db.String(10))
    s_ip = db.Column(db.String(40))
    s_lat = db.Column(db.String(40))
    s_long = db.Column(db.String(40))
    s_timestart = db.Column(db.String(10))
    s_timeend = db.Column(db.String(10))

    logs = db.relationship('LogModel', lazy='dynamic')

    def __init__(self, username, password, phone_number, s_ip, s_lat, s_long, s_timestart, s_timeend):
        self.username = username
        self.password = password
        self.phone_number = phone_number
        self.s_ip = s_ip
        self.s_lat = s_lat
        self.s_long = s_long
        self.s_timestart = s_timestart
        self.s_timeend = s_timeend

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def json(self):
        return {'name': self.username, 'logs': [log.json() for log in self.logs.all()]}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
