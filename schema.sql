CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),
    age SMALLINT CHECK (age BETWEEN 0 AND 120),
    designation VARCHAR(255),
    city VARCHAR(100),
    pin CHAR(6) CHECK (pin ~ '^[0-9]+$'), -- Ensures pin is exactly 6 digits
    fav_food VARCHAR(100),
    fav_movie VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
