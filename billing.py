from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
import mysql.connector
import sys
import json
import os

class BillingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing App")
        self.showFullScreen()  # Launches in full screen

        # Initialize total bill and list of products for the bill
        self.total_amount = 0.0
        self.product_list = []

        # Set up the UI
        self.init_ui()

    def init_ui(self):
        # Main vertical layout for the window
        main_layout = QVBoxLayout()

        # Horizontal layout for input fields
        form_layout = QHBoxLayout()

        # Customer and product input fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Customer Name")
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Contact Number")
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Product Name")
        self.product_cost_input = QLineEdit()
        self.product_cost_input.setPlaceholderText("Product Cost")
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")

        # Add input fields and labels to layout
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Contact:"))
        form_layout.addWidget(self.contact_input)
        form_layout.addWidget(QLabel("Product:"))
        form_layout.addWidget(self.product_name_input)
        form_layout.addWidget(QLabel("Cost:"))
        form_layout.addWidget(self.product_cost_input)
        form_layout.addWidget(QLabel("Qty:"))
        form_layout.addWidget(self.quantity_input)

        # Buttons
        self.add_product_btn = QPushButton("Add Product")
        self.add_product_btn.clicked.connect(self.add_product)

        self.submit_bill_btn = QPushButton("Submit Bill")
        self.submit_bill_btn.clicked.connect(self.submit_bill)

        self.retrieve_btn = QPushButton("Retrieve Bills")
        self.retrieve_btn.clicked.connect(self.retrieve_bills)

        self.end_list_btn = QPushButton("End List")
        self.end_list_btn.clicked.connect(self.end_list)
        self.end_list_btn.hide()  # Hidden until retrieval mode is active

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)

        # Table to show current products being added to bill
        self.current_products_table = QTableWidget()
        self.current_products_table.setColumnCount(3)
        self.current_products_table.setHorizontalHeaderLabels(["Product", "Cost", "Quantity"])
        self.current_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Table to show all bill records when retrieved
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels([
            "Bill ID", "Customer Name", "Contact", "Product", "Cost", "Amount"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.hide()

        # Add widgets and layouts to the main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.add_product_btn)
        main_layout.addWidget(self.current_products_table)
        main_layout.addWidget(self.submit_bill_btn)
        main_layout.addWidget(self.retrieve_btn)
        main_layout.addWidget(self.end_list_btn)
        main_layout.addWidget(self.exit_btn)
        main_layout.addWidget(self.data_table)

        self.setLayout(main_layout)

    def connect_db(self):
        # Establish database connection
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="SriSailesh@3320",  # Replace with your password
            database="billing_db"
        )

    def add_product(self):
        # Retrieve input values
        product = self.product_name_input.text()
        cost = self.product_cost_input.text()
        quantity = self.quantity_input.text()

        # Validate inputs
        if not product or not cost or not quantity:
            QMessageBox.warning(self, "Error", "Please fill product, cost and quantity.")
            return

        try:
            cost = float(cost)
            quantity = int(quantity)
            amount = cost * quantity
            self.total_amount += amount
            self.product_list.append((product, cost, quantity))

            # Add to the current products table
            row_pos = self.current_products_table.rowCount()
            self.current_products_table.insertRow(row_pos)
            self.current_products_table.setItem(row_pos, 0, QTableWidgetItem(product))
            self.current_products_table.setItem(row_pos, 1, QTableWidgetItem(str(cost)))
            self.current_products_table.setItem(row_pos, 2, QTableWidgetItem(str(quantity)))

            # Clear input fields
            self.product_name_input.clear()
            self.product_cost_input.clear()
            self.quantity_input.clear()

        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number for cost or quantity.")

    def submit_bill(self):
        # Get customer details
        name = self.name_input.text()
        contact = self.contact_input.text()

        if not name or not contact:
            QMessageBox.warning(self, "Error", "Please enter name and contact.")
            return

        if not self.product_list:
            QMessageBox.warning(self, "Error", "No products added to the bill.")
            return

        try:
            db = self.connect_db()
            cursor = db.cursor()

            # Insert customer info
            cursor.execute("INSERT INTO customers (name, contact) VALUES (%s, %s)", (name, contact))
            customer_id = cursor.lastrowid

            # Insert bill info
            cursor.execute("INSERT INTO bills (customer_id, amount, date) VALUES (%s, %s, CURDATE())",
                           (customer_id, self.total_amount))
            bill_id = cursor.lastrowid

            # Insert bill items
            for product, cost, quantity in self.product_list:
                cursor.execute(
                    "INSERT INTO bill_items (bill_id, product_name, cost, quantity) VALUES (%s, %s, %s, %s)",
                    (bill_id, product, cost, quantity)
                )

            db.commit()
            db.close()

            # Save record in JSON file
            for product, cost, quantity in self.product_list:
                record = {
                    "bill_id": bill_id,
                    "customer_name": name,
                    "contact": contact,
                    "product": product,
                    "product_cost": cost,
                    "quantity": quantity,
                    "amount": self.total_amount
                }
                self.save_to_json(record)

            QMessageBox.information(self, "Success", "Bill submitted successfully.")
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def save_to_json(self, record):
        # Save a bill record to a local JSON file
        json_file = "bills_data.json"
        data = []
        if os.path.exists(json_file):
            with open(json_file, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
        data.append(record)
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)

    def retrieve_bills(self):
        try:
            # Toggle visibility for retrieval mode
            self.data_table.show()
            self.end_list_btn.show()
            self.current_products_table.hide()
            self.submit_bill_btn.hide()
            self.retrieve_btn.hide()
            self.add_product_btn.hide()

            db = self.connect_db()
            cursor = db.cursor()
            # Join query to show all bill details
            cursor.execute("""
                SELECT b.bill_id, c.name, c.contact, i.product_name, i.cost, (i.cost * i.quantity)
                FROM bills b
                INNER JOIN customers c ON b.customer_id = c.customer_id
                INNER JOIN bill_items i ON b.bill_id = i.bill_id
            """)
            data = cursor.fetchall()
            self.data_table.setRowCount(len(data))
            for row, entry in enumerate(data):
                for col, item in enumerate(entry):
                    self.data_table.setItem(row, col, QTableWidgetItem(str(item)))
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def end_list(self):
        # Return to normal billing mode
        self.data_table.hide()
        self.end_list_btn.hide()
        self.current_products_table.show()
        self.submit_bill_btn.show()
        self.retrieve_btn.show()
        self.add_product_btn.show()

    def clear_form(self):
        # Clear all form fields and table data
        self.name_input.clear()
        self.contact_input.clear()
        self.product_name_input.clear()
        self.product_cost_input.clear()
        self.quantity_input.clear()
        self.current_products_table.setRowCount(0)
        self.product_list = []
        self.total_amount = 0.0

# Launch the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())
