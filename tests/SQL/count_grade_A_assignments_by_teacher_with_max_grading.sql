WITH teacher_grading_count AS (
    SELECT teacher_id, COUNT(*) AS graded_count
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
    ORDER BY graded_count DESC
    LIMIT 1
)
SELECT COUNT(*) AS grade_a_count
FROM assignments a
JOIN teacher_grading_count tgc ON a.teacher_id = tgc.teacher_id
WHERE a.grade = 'A';