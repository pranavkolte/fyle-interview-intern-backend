from core.models.assignments import GradeEnum

def test_fyle_error_handler(client):
    response = client.post(
        '/teacher/assignments/grade',
        headers={},
        json={
            "id": 1,
            "grade": GradeEnum.A.value
        }
    )

    assert response.status_code == 401
    data = response.json
    assert data['error'] == 'FyleError'
    assert 'principal not found' in data['message'].lower()

def test_not_found_error_handler(client):
    response = client.get('/non_existent_route')

    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'NotFound'

def test_unauthorized_error_handler(client):
    response = client.get('/teacher/assignments')

    assert response.status_code == 401
    data = response.json
    assert data['error'] == 'FyleError'
    assert 'principal not found' in data['message'].lower()

def test_validation_error_handler(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "Invalid Grade"
        }
    )

    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError'
