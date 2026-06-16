from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
import datetime

class Note(db.Model): #UserMixin is not used here. It is only for the User Model (class)
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str]
    date: Mapped[datetime.datetime]
    # user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    def __repr__(self):
        return self.id


class User(UserMixin, db.Model): #UserMixin is used here. It is only for the User Model (class)
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[int] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)

    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    #notes = db.relationship('Note')

    is_admin: Mapped[bool]

    is_confirmed:Mapped[bool]

    # address:Mapped[str]

    def __repr__(self):
        return self.id