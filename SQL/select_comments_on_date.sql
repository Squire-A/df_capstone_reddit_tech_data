SELECT comment_id, body
FROM student.as_capstone_comments
WHERE date_created 
BETWEEN :start_date AND :end_date 
ORDER BY score DESC;