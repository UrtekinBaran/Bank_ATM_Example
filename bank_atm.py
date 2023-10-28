# Database Connection and Table Definition:
from datetime import datetime
from sqlalchemy import create_engine, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


# represents the table named 'clients', where id, name, pin, balance, and created_at represent the columns.
class Client(Base):
    __tablename__ = 'clients'

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, unique=True, index=True)
    pin = mapped_column(String)
    balance = mapped_column(Integer, default=1000)
    created_at = mapped_column(DateTime, default=datetime.now())


# PostgreSQL connection
db_uri = 'postgresql://dbname:your_password@yourhost:/postgres'

# engine is a term in the SQLAlchemy library and is the main tool for managing database operations
engine = create_engine(db_uri)

# metadata object, to define a set of database tables, columns and other structures and to define relationships
# between these structures is used to set up.
Base.metadata.create_all(bind=engine)

# database operations can be performed over the session variable.
Session = sessionmaker(bind=engine)
session = Session()


def initialize_client_balance(clients_data):
    for client_name, client_data in clients_data.items():
        existing_client = session.query(Client).filter_by(name=client_name).first()

        if existing_client:
            # Update if the client already exists
            existing_client.pin = client_data["pin"]
            existing_client.balance = client_data["balance"]
        else:
            # Or add new customer
            client = Client(name=client_name, pin=client_data["pin"], balance=client_data["balance"])
            session.add(client)

    # Commit changes
    session.commit()


def atm_login(id, pin):
    client = session.query(Client).filter_by(name=id).first()
    return client is not None  # if no record is found, its value is None.


def atm_withdraw(id, amount):
    client = session.query(Client).filter_by(name=id).first()
    if client and amount <= client.balance:
        client.balance -= amount
        session.commit()
        return True
    return False


def atm_deposit(id, amount):
    client = session.query(Client).filter_by(name=id).first()
    if client:
        client.balance += amount
        session.commit()
        return True
    return False


def atm_balance(id):
    client = session.query(Client).filter_by(name=id).first()
    return client.balance if client else None


def atm_transfer(id, amount, to):
    sender = session.query(Client).filter_by(name=id).first()
    receiver = session.query(Client).filter_by(name=to).first()

    if sender and receiver and amount <= sender.balance:
        sender.balance -= amount
        receiver.balance += amount
        session.commit()
        return True
    return False


def logout():
    print("You have logged out. Thank you for using our service.")


def main():
    clients_data = {
        "Ali": {"pin": "1234", "balance": 1000},
        "Ece": {"pin": "4321", "balance": 1000}
    }

    initialize_client_balance(clients_data)

    while True:
        print("""
---Welcome to Baran Bank---
1. Login
2. Exit
        """)

        choice = input("Please select an option: ")

        if choice == "1":
            id = input("Please enter your ID: ")
            pin = input("Please enter your PIN: ")

            if atm_login(id, pin):
                print("Login successful!")

                while True:
                    print("""
1. Withdraw Money
2. Deposit Money
3. Transfer Money
4. My Account Information
5. Logout                                  
                    """)
                    choice = input("Please select an option: ")

                    if choice == "1":
                        amount = int(input("Please enter the amount to withdraw: "))

                        if atm_withdraw(id, amount):
                            print("Withdrawal successful!")

                        else:
                            print("Withdrawal failed!")

                    elif choice == "2":
                        amount = int(input("Please enter the amount to deposit: "))

                        if atm_deposit(id, amount):
                            print("Deposit successful!")

                        else:
                            print("Deposit failed!")

                    elif choice == "3":
                        amount = int(input("Please enter the amount to transfer: "))
                        to = input("Please enter the ID of the recipient: ")

                        if atm_transfer(id, amount, to):
                            print("Transfer successful!")

                        else:
                            print("Transfer failed!")

                    elif choice == "4":
                        print("----Baran Bank----")
                        print(datetime.now())
                        print("ID: ", id)
                        print("Your balance is: ", atm_balance(id))

                    elif choice == "5":
                        logout()
                        break

                    else:
                        print("Invalid option!")

            else:
                print("Login failed!\nTry again.")

        elif choice == "2":
            print("Thank you for using our service.")
            break

        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main()
