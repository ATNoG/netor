# @Author: Daniel Gomes
# @Date:   2022-10-19 14:56:49
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-29 21:23:25
import api.queries.vs_blueprint as queries
from flask import Blueprint, request, g
from http import HTTPStatus
from marshmallow import ValidationError
from api.serializers.vs_blueprint import VsBlueprintInfoSerializer
from api.serializers.requests import VsBlueprintRequestSerializer
from api.serializers.ns_template import NstSerializer
from api.views.utils import response_template
from api.exceptions.utils import handle_exception
from api.exceptions.exceptions import BadVsBlueprintBody
from oidc import oidc
import logging
import api.auth as auth
# noinspection PyRedeclaration
app = Blueprint('vsblueprint', __name__)

handle_exception(app)  # Handle errors


@app.route('/vsblueprint', methods=('GET',))
@oidc.accept_token(True)
def get_vs_blueprints():
    tenant = auth.parse_token_data(g)
    args = {
        'tenant_id': tenant.id,
        'vsb_id': request.args.get('vsb_id'),
        'vsb_name': request.args.get('vsb_name'),
        'vsb_version': request.args.get('vsb_version'),

    }
    serializer = VsBlueprintInfoSerializer(many=True)
    data = serializer.dump(queries.get_vs_blueprints(**args))

    return response_template('Success', data)


@app.route('/vsblueprint', methods=('DELETE',))
@oidc.accept_token(True)
def delete_vs_blueprint():
    vsb_id = request.args.get('vsb_id')

    queries.delete_vs_blueprint(vsb_id)

    return response_template('Success', status_code=HTTPStatus.NO_CONTENT)


@app.route('/vsblueprint', methods=('POST',))
@oidc.accept_token(True)
def create_vs_blueprint():
    request_data = request.get_json()

    serializer = VsBlueprintRequestSerializer()
    try:
        validated_data = serializer.load(request_data)
    except ValidationError as error:
        raise BadVsBlueprintBody(error.messages)

    vs_blueprint_id = queries.create_vs_blueprint(validated_data)
    
    return response_template('Success', data={'vs_blueprint_id': vs_blueprint_id}, status_code=HTTPStatus.CREATED)


# NST
@app.route('/nst', methods=('GET',))
@oidc.accept_token(True)
def get_nst():
    serializer = NstSerializer(many=True)
    data = serializer.dump(queries.get_nst())
    return response_template('Success', data)


@app.route('/nst', methods=('DELETE',))
@oidc.accept_token(True)
def delete_nst():
    nst_id = request.args.get('nst_id')

    queries.delete_nst(nst_id)
    return response_template('Success', status_code=HTTPStatus.NO_CONTENT)
