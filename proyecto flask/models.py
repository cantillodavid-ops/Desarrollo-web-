from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column('user_role', db.String(20), nullable=False)
    bio           = db.Column(db.Text, default='')

    events        = db.relationship('Event', backref='organizer', lazy='dynamic',
                                    foreign_keys='Event.organizer_id')
    registrations = db.relationship('Registration', backref='user', lazy='dynamic',
                                    cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_organizer(self):
        return self.role == 'organizer'

    def is_attendee(self):
        return self.role == 'attendee'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Event(db.Model):
    __tablename__ = 'events'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(140), nullable=False)
    description  = db.Column(db.Text,        nullable=False)
    date         = db.Column(db.DateTime,    nullable=False)
    capacity     = db.Column(db.Integer,     nullable=False)
    category     = db.Column(db.String(60),  nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    registrations = db.relationship('Registration', backref='event', lazy='dynamic',
                                    cascade='all, delete-orphan')

    @property
    def spots_taken(self):
        return self.registrations.count()

    @property
    def spots_left(self):
        return self.capacity - self.spots_taken

    @property
    def is_full(self):
        return self.spots_left <= 0

    def __repr__(self):
        return f'<Event {self.title}>'


class Registration(db.Model):
    __tablename__ = 'registrations'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    event_id      = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_registration'),
    )

    def __repr__(self):
        return f'<Registration user={self.user_id} event={self.event_id}>'