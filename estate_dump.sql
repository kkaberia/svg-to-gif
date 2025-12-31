-- Create User Table
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(10) DEFAULT 'member',
    house_number VARCHAR(20) NOT NULL,
    family_name VARCHAR(50) NOT NULL,
    balance FLOAT DEFAULT 0.0
);

-- Create Payment Table
CREATE TABLE payment (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_type VARCHAR(50),
    origin_bank VARCHAR(50),
    months VARCHAR(100)
);

-- Create BankTransaction Table
CREATE TABLE bank_transaction (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    narration VARCHAR(255) NOT NULL,
    amount FLOAT NOT NULL,
    payment_mode VARCHAR(50) NOT NULL,
    payee VARCHAR(100) NOT NULL
);

-- Insert Admin User (if needed)
INSERT INTO "user" (username, first_name, last_name, email, password, role, house_number, family_name)
VALUES (
    'kkaberia',
    'Admin',
    'User',
    'kkaberia@example.com',
    'hashed_password_here',  -- Replace with the actual hashed password
    'admin',
    '1',
    'Admin Family'
);

-- Insert Sample Data (Optional)
-- Insert Sample User
INSERT INTO "user" (username, first_name, last_name, email, password, house_number, family_name)
VALUES (
    'testuser',
    'Test',
    'User',
    'test@example.com',
    'hashed_password_here',  -- Replace with the actual hashed password
    '123',
    'Test Family'
);

-- Insert Sample Payment
INSERT INTO payment (user_id, amount, payment_type, origin_bank, months)
VALUES (
    1,  -- Replace with the actual user_id
    3850.0,
    'M-PESA Transfer',
    'Bank A',
    'January,February'
);

-- Insert Sample Bank Transaction
INSERT INTO bank_transaction (date, narration, amount, payment_mode, payee)
VALUES (
    '2023-10-01',
    'Security Payment',
    3850.0,
    'Bank Transfer',
    'John Doe'
);