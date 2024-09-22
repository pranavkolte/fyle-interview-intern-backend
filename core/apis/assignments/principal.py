from flask import Blueprint

from typing import List, Dict

from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment

from .schema import AssignmentSchema, AssignmentGradeSchema
from ..decorators import AuthPrincipal
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def get_assignments(auth_principal: AuthPrincipal) -> APIResponse:
    """
    Lists all submitted and graded assignments
    :auth_principal: Auth Principal
    :return: APIResponse
    """
    all_submitted_and_graded_assignments: List[Assignment] = Assignment.get_all_submitted_and_graded_assignments()
    serialized_assignments: List[Dict] = AssignmentSchema().dump(all_submitted_and_graded_assignments, many=True)
    return APIResponse.respond(data=serialized_assignments)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_or_regrade_assignments(auth_principal: AuthPrincipal, incoming_payload: dict) -> APIResponse:
    """
    Grades or regrades an assignment by the principal
    :param auth_principal: AuthPrincipal
    :param incoming_payload: dict
    :return: APIResponse
    """
    grade_payload = AssignmentGradeSchema().load(incoming_payload)
    graded_assignment = Assignment.mark_grade(
        _id=grade_payload.id,
        grade=grade_payload.grade,
        auth_principal=auth_principal,
    )

    db.session.commit()
    serialized_graded_assignment: List[Dict] = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=serialized_graded_assignment)
