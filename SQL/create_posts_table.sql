CREATE TABLE IF NOT EXISTS student.as_capstone_posts (
    post_id VARCHAR(10) PRIMARY KEY,
    title TEXT,
    date_created TIMESTAMP,
    score INT,
    comments INT,
    url TEXT
);