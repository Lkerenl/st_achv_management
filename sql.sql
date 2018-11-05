select no,cno,
case when regular_grade+exam_grade=1
then  regular * regular_grade + exam * exam_grade
else regular * regular_grade + exam * exam_grade + (1 - regular_grade - exam_grade) * expr
end
from tmp_score_view where cno=1810666;
