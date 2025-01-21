INSERT INTO student.as_capstone_posts (post_id, title, date_created, score, comments, url)
    VALUES (:post_id, :title, :date_created, :score, :comments, :url)
    ON CONFLICT (post_id)
    DO UPDATE SET 
        score = EXCLUDED.score, 
        comments = EXCLUDED.comments;