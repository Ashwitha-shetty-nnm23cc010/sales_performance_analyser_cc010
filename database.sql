-- Create the database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'sales_db')
BEGIN
    CREATE DATABASE sales_db;
END
GO

USE sales_db;
GO

-- Create users table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
BEGIN
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(50) NOT NULL UNIQUE,
        password NVARCHAR(255) NOT NULL
    );
END
GO

-- Create sales table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sales' AND xtype='U')
BEGIN
    CREATE TABLE sales (
        id INT IDENTITY(1,1) PRIMARY KEY,
        product_name NVARCHAR(100) NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        total AS (quantity * price) PERSISTED,
        region NVARCHAR(50) NOT NULL,
        salesperson NVARCHAR(100) NOT NULL,
        sale_date DATE NOT NULL
    );
END
GO

-- Insert default user
IF NOT EXISTS (SELECT * FROM users WHERE username = 'admin')
BEGIN
    INSERT INTO users (username, password) VALUES ('admin', 'admin');
END
GO
