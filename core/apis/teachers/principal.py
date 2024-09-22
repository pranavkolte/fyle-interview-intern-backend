from flask import Blueprint

from typing import List, Dict

from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.teachers import Teacher

from .schema import TeacherSchema
from ..decorators import AuthPrincipal

principal_teachers_resources = Blueprint('principal_teachers_resources', __name__)


@principal_teachers_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers(auth_principal: AuthPrincipal) -> APIResponse:
    """
    Returns list of teachers
    :auth_principal: Auth Principal
    :return: APIResponse
    """
    all_teachers: List[Teacher] = Teacher.get_all_teachers()
    serialized_teachers: List[Dict] = TeacherSchema().dump(all_teachers, many=True)
    return APIResponse.respond(data=serialized_teachers)
