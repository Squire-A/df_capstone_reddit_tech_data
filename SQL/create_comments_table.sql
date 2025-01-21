CREATE TABLE IF NOT EXISTS student.as_capstone_comments (
    comment_id VARCHAR(10) PRIMARY KEY,
    post_id VARCHAR(10),
    body TEXT,
    score INT,
    date_created TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES student.as_capstone_posts(post_id)
);