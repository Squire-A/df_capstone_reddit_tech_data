INSERT INTO student.as_capstone_comments (comment_id, post_id, body, score, date_created)
VALUES (:comment_id, :post_id, :body, :score, :date_created)
ON CONFLICT (comment_id) 
DO UPDATE SET 
    body = EXCLUDED.body, 
    score = EXCLUDED.score; 