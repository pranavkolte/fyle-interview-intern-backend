from core.models.assignments import GradeEnum
from core.models.assignments import Assignment, AssignmentStateEnum
from core import db

def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_success(client, h_teacher_1):
    assignment = Assignment(student_id=1, teacher_id=1, content="Test assignment", state=AssignmentStateEnum.SUBMITTED)
    db.session.add(assignment)
    db.session.commit()

    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": assignment.id,
            "grade": GradeEnum.B.value
        }
    )

    assert response.status_code == 200
    data = response.json['data']
    assert data['grade'] == GradeEnum.B.value
    assert data['state'] == AssignmentStateEnum.GRADED.value


def test_list_assignments_structure(client, h_teacher_1):
    """
    failure case: assignments with missing fields
    """
    response = client.get('/teacher/assignments', headers=h_teacher_1)
    assert response.status_code == 200
    data = response.json['data']

    assert isinstance(data, list)

    for assignment in data:
        assert 'id' in assignment
        assert 'content' in assignment
        assert 'created_at' in assignment
        assert 'grade' in assignment
        assert 'state' in assignment
        assert 'student_id' in assignment
        assert 'teacher_id' in assignment
        assert 'updated_at' in assignment
        assert assignment['teacher_id'] == 1


def test_list_assignments_with_data(client, h_teacher_1):
    """
    Test case: Verify that a newly added assignment appears in the list
    """
    initial_response = client.get('/teacher/assignments', headers=h_teacher_1)
    initial_count = len(initial_response.json['data'])

    new_assignment = Assignment(student_id=1, teacher_id=1, content="Test assignment", state=AssignmentStateEnum.SUBMITTED)
    db.session.add(new_assignment)
    db.session.commit()

    response = client.get('/teacher/assignments', headers=h_teacher_1)
    assert response.status_code == 200
    data = response.json['data']

    assert len(data) == initial_count + 1

    new_assignment_in_response = next((assignment for assignment in data if assignment['content'] == "Test assignment"), None)
    assert new_assignment_in_response is not None
    assert new_assignment_in_response['teacher_id'] == 1
    assert new_assignment_in_response['state'] in [AssignmentStateEnum.SUBMITTED.value, AssignmentStateEnum.GRADED.value]

    db.session.delete(new_assignment)
    db.session.commit()


def test_grade_assignment_not_found(client, h_teacher_1):
    """
    failure case: Attempt to grade a non-existent assignment
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 9999,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'FyleError'
    assert 'no assignment with this id was found' in data['message'].lower()