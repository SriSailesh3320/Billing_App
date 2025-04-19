from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox
)
import mysql.connector

# -- Billing App class --
class BillingApp(QWidget):
    def __init__(self):
        super().__init__()

        # -- Window Creation --
        self.setWindowTitle("Billing Application")
        self.setGeometry(0, 0, 1000, 1000)

        layout = QVBoxLayout()

        # -- Form Fields --
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Customer Name")

        self.contact_input = QLineEdit(self)
        self.contact_input.setPlaceholderText("Contact Number")

        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Bill Amount")

        # -- Buttons --
        self.submit_btn = QPushButton("Add Bill(s)")
        self.submit_btn.clicked.connect(self.add_bill)

        self.retrieve_btn = QPushButton("History")
        self.retrieve_btn.clicked.connect(self.retrieve_data)

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close_app)

        # -- Table for Displaying contents. --
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels(["Bill ID","Date", "Customer Name", "Contact", "Amount"])

        # -- Adding Widgets to Layout. --
        layout.addWidget(QLabel("Customer Name"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Contact Number"))
        layout.addWidget(self.contact_input)
        layout.addWidget(QLabel("Bill Amount"))
        layout.addWidget(self.amount_input)
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.retrieve_btn)
        layout.addWidget(self.exit_btn)
        layout.addWidget(self.data_table)


        self.setLayout(layout)

    # -- Connecting DB (billing_db) --
    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="SriSailesh@3320",  
            database="billing_db"
        )
    # -- Adding Bill(s) --
    def add_bill(self):
        name = self.name_input.text()
        contact = self.contact_input.text()
        amount = self.amount_input.text()

        if not name or not contact or not amount:
            QMessageBox.warning(self, "Warning", "All fields are required.")
            return

        try:
            db = self.connect_db()
            cursor = db.cursor()

            # -- Insert customer details. --
            cursor.execute(
                "INSERT INTO customers (name, contact) VALUES (%s, %s)", 
                (name, contact)
            )
            customer_id = cursor.lastrowid

            # -- Insert bill details. --
            cursor.execute(
                "INSERT INTO bills (customer_id, amount, date) VALUES (%s, %s, CURDATE())", 
                (customer_id, amount)
            )

            db.commit()
            db.close()
            # -- Success message --
            QMessageBox.information(self, "Success", "Bill added successfully!")
            self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def retrieve_data(self):
        try:
            db = self.connect_db()
            cursor = db.cursor()
            # -- Query to display the bill and customer tables. --
            query = """
            SELECT bills.bill_id, bills.date, customers.name, customers.contact, bills.amount
            FROM bills
            INNER JOIN customers ON bills.customer_id = customers.customer_id
            """
            cursor.execute(query)
            data = cursor.fetchall()

            self.data_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            db.close()
            

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # -- Exit from the window. --
    def close_app(self):
        self.close()

    # -- Clearing fields after completion of the insertion. --
    def clear_fields(self):
        self.name_input.clear()
        self.contact_input.clear()
        self.amount_input.clear()

    
if __name__ == "__main__":
    app = QApplication([])   # Creates the application
    window = BillingApp()    # Creates main window
    window.show()            # Shows the window
    app.exec()               # Runs the application
