from core.models.assignments import AssignmentStateEnum, GradeEnum

from unittest.mock import patch

from sqlalchemy.exc import SQLAlchemyError


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B


def test_list_teachers(client, h_principal):
    response = client.get('/principal/teachers', headers=h_principal)
    assert response.status_code == 200
    data = response.json['data']
    assert isinstance(data, list)
    if len(data) > 0:
        assert 'id' in data[0]
        assert 'user_id' in data[0]


def test_grade_assignment_database_error(client, h_principal):
    """
    Test case: Database error while grading an assignment
    """
    with patch('core.models.assignments.db.session.commit') as mock_commit:
        mock_commit.side_effect = SQLAlchemyError("Database error")

        response = client.post(
            '/principal/assignments/grade',
            json={
                'id': 4,
                'grade': GradeEnum.B.value
            },
            headers=h_principal
        )

        assert response.status_code == 500
        data = response.json
        assert data['error'] == 'FyleError'
        assert "A database error occurred while grading the assignment" in data['message']


def test_grade_assignment_unknown_error(client, h_principal):
    """
    failure case: Unknown error while grading an assignment
    """
    with patch('core.models.assignments.db.session.commit') as mock_commit:
        mock_commit.side_effect = Exception("Unknown error")

        response = client.post(
            '/principal/assignments/grade',
            json={
                'id': 4,
                'grade': GradeEnum.B.value
            },
            headers=h_principal
        )

        assert response.status_code == 500
        data = response.json
        assert data['error'] == 'FyleError'
        assert "Unknown error" in data['message']
