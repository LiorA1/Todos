from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# todos table
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"))  # new column

    # owner = relationship("Users", back_populates="todos")


# INSERT INTO todos(title, description, priority, complete) VALUES('Go to store', 'to pick up eggs', 4, False);
# INSERT INTO todos(title, description, priority, complete) VALUES('Haircut', 'Need to get length 1mm', 3, False);

# SELECT * FROM todos;
# SELECT * FROM todos WHERE id=2;

# UPDATE todos SET complete=True WHERE id=5;
# UPDATE todos SET complete=True WHERE title='Learn something new';

# DELETE FROM todos WHERE id=5;

# One-To-Many Relationship: One User - Many Todos.


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)
    address_id = Column(Integer, ForeignKey("address.id"), nullable=True)
    address = relationship("Address", back_populates="user_address")

    # todos = relationship("Todos", back_populates="owner")


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    address1 = Column(String)
    apt_num = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalcode = Column(String, default=True)

    user_address = relationship("Users", back_populates="address")
