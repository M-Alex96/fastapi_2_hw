from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Numeric, Uuid, Table, Boolean
from sqlalchemy.orm import relationship
from typing import Literal


from db import Base

ModelName = Literal["User", "Advertisement", "Role", "Right"]

user_role_relation = Table("user_role_relation", Base.metadata,
                           Column("user_id", ForeignKey("users.id"), primary_key=True),
                           Column("role_id", ForeignKey("role.id"), primary_key=True))

role_right_relation = Table ("role_right_relation", Base.metadata,
                             Column("role_id", ForeignKey("role.id"), primary_key=True),
                             Column("right_id", ForeignKey("right.id"), primary_key=True))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan", lazy="joined")
    roles = relationship(secondary=user_role_relation, lazy="joined")
    advertisements = relationship ("Advertisement", back_populates="author")

    def user_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Role(Base):
    __tablename__= "role"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    rights = relationship(secondary=role_right_relation, lazy="joined")


class Right(Base):
    __tablename__= "right"

    id = Column(Integer, primary_key=True)
    write = Column(Boolean, nullable=False, default=False)
    read = Column(Boolean, nullable=False, default=False)
    only_own = Column(Boolean, nullable=False, default=True)
    model = Column(String, nullable=False)

class Token(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True)
    token = Column (Uuid, server_default=func.get_random_uuid(), unique=True, nullable=False)
    creation_time = Column (DateTime, server_default=func.now(), nullable=False)
    user_id = Column (Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tokens")

    def to_dict(self):
        return{"id": self.id, "token": str(self.token), "creation_time": self.creation_time.isoformat()}


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    author = relationship("User", back_populates="advertisements")

    def advertisement_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author_id": self.author_id,
            "created_at": self.created_at
        }