-- 1. UNITS TABLE (REPRESENTING DEPARTMENTS)
CREATE TABLE units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. USERS TABLE
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255), -- Optional for Google login
    auth_provider ENUM('local', 'google') DEFAULT 'local',
    role ENUM('user', 'manager') DEFAULT 'user',
    unit_id INT,
    validated BOOLEAN DEFAULT FALSE,
    confirmation_token VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE SET NULL
);

-- 3. LEAVE REQUESTS TABLE
CREATE TABLE leave_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    request_type ENUM('timeoff', 'permission') NOT NULL,
    start_date DATE NULL, -- For timeoff (day-based)
    end_date DATE NULL,   -- For timeoff (day-based)
    start_datetime DATETIME NULL, -- For permission (hour-based)
    end_datetime DATETIME NULL,   -- For permission (hour-based)
    reason TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    reviewed_by INT, -- Manager who approved/rejected
    reviewed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 4. INSERT DEFAULT UNIT
INSERT INTO units (name) VALUES ('Default Office');

-- 5. INSERT ADMIN USER WITH PASSWORD 'password'
INSERT INTO users (name, email, password_hash, auth_provider, role, unit_id, validated) VALUES ('Admin', 'admin@example.com', '$2b$12$iDrs7S9nqjA0d/zeocrMLe0RIrY8utFgGxJZ1w1p7PN7HlUZQ31aO', 'local', 'manager', 1, 1);
