SELECT body
FROM student.as_capstone_comments
WHERE post_id IN (
    SELECT post_id
    FROM student.as_capstone_posts
    WHERE date_created
    BETWEEN :start_date AND :end_date 
)
ORDER BY score DESC;