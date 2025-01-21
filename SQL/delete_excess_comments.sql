DELETE FROM student.as_capstone_comments
WHERE post_id = :post_id AND comment_id NOT IN (
    SELECT comment_id FROM student.as_capstone_comments
    WHERE post_id = :post_id
    ORDER BY score DESC
    LIMIT :number_of_comments
);