SELECT post_id, title 
FROM student.as_capstone_posts 
WHERE date_created 
BETWEEN :start_date AND :end_date 
ORDER BY score DESC;