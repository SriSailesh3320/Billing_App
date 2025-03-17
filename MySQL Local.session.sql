CREATE DATABASE billing_db;

USE billing_db;

-- Table for customers

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15) NOT NULL
);


-- Table for storing bills 

CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

SELECT * from bills;
SELECT * from customers;