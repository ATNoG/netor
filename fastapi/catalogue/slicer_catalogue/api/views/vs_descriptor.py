# @Author: Daniel Gomes
# @Date:   2022-10-19 14:56:49
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 21:23:18
from flask import Blueprint, request, g
from marshmallow import ValidationError
from http import HTTPStatus
from api.exceptions.utils import handle_exception
from api.serializers.vs_descriptor import VsDescriptorSerializer
from api.views.utils import response_template
from api.exceptions.exceptions import BadVsBlueprintBody
from api.auth import login_required, current_user
import api.queries.vs_descriptor as queries
from oidc import oidc
import api.auth as auth
app = Blueprint('vsdescriptor', __name__)

handle_exception(app)  # Handle errors


@app.route("/vsdescriptor", methods=('GET',))
@oidc.accept_token(True)
def get_vs_descriptors():
    current_user = auth.parse_token_data(g)
    args = {
        'tenant_id': current_user.id,
        'vsd_id': request.args.get('vsd_id'),
        'is_admin': current_user.is_admin()
    }

    serializer = VsDescriptorSerializer(many=True)
    data = serializer.dump(queries.get_vs_descriptors(**args))

    return response_template('Success', data)


@app.route('/vsdescriptor', methods=('DELETE',))
@oidc.accept_token(True)
def delete_vs_descriptor():
    current_user = auth.parse_token_data(g)
    args = {
        'tenant_id': current_user.id,
        'vsd_id': request.args.get('vsd_id'),
        'is_admin': current_user.is_admin()
    }

    queries.delete_vs_descriptor(**args)
    return response_template('Success', status_code=HTTPStatus.NO_CONTENT)


@app.route('/vsdescriptor', methods=('POST',))
@oidc.accept_token(True)
def create_vs_descriptor():
    request_data = request.get_json()
    serializer = VsDescriptorSerializer()
    try:
        validated_data = serializer.load(request_data)
    except ValidationError as error:
        raise BadVsBlueprintBody(error.messages)

    vs_descriptor_id = queries.create_vs_descriptor(validated_data)
    return response_template('Success', data={'vs_descriptor_id': vs_descriptor_id}, status_code=HTTPStatus.CREATED)
