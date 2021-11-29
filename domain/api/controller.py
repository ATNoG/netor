from flask import Flask, jsonify, request
from flasgger import Swagger, validate
import service as domainService
from api.loginConfig import loginManager, login_required
from flask_cors import CORS, cross_origin
import requests
from config import OSM_IP

app = Flask(__name__)
CORS(app)

swagger_config = {
    "openapi": "3.0.3",
    "title": "Domain Management API",
    "swagger_ui": True,
}

swagger = Swagger(app, config=swagger_config, merge=True,template_file='definitions.yaml')

loginManager.init_app(app)

@app.route('/domain', methods=["GET"])
@login_required
def getAllDomains():
    """
    Return all the Domains in the system
    ---
    responses:
        200:
            description: returns a list of all the domains
            content:
                application/json:
                    schema:
                        type: array
                        items:
                            $ref: '#/definitions/Domain'
    """

    try:
        domains=domainService.getAllDomains()
        return jsonify({"message":"Success", "data":domains}),200
    except Exception as e:
        return jsonify({"message":"Error: "+str(e)}),500

@app.route('/domain', methods=["POST"])
@login_required
def createNewDomain():
    """
    Creates a new Domain
    ---
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/definitions/Domain'
        required: true
    responses:
        200:
            description: acknowledges the request
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Acknowledge'
    """

    data=request.json
    validate(data, 'Domain', 'definitions.yaml')

    # check if domain already exists in db
    db_domain = domainService.getOsmDomain(data['ownedLayers'][0]['domainLayerId'])
    if(db_domain['username'] == data['ownedLayers'][0]['username'] and db_domain['password'] == data['ownedLayers'][0]['password'] and db_domain['project'] == data['ownedLayers'][0]['project']):
        return jsonify({"message":"Error: domain already exists"}),500

    r = requests.post(OSM_IP + "/admin/v1/tokens", data = {"username": data['ownedLayers'][0]['username'], "password": data['ownedLayers'][0]['password'], "project_id": data['ownedLayers'][0]['project']})

    if r.status_code != 200:
        return jsonify({"message":"Error: Unauthorized"}),401

    try:
        domainService.createDomain(data)
        return jsonify({"message":"Success"}),200
    except Exception as e:
        return jsonify({"message":"Error: "+str(e)}),500

@app.route('/domain/<domainId>', methods=["GET"])
@login_required
def getDomainById(domainId):
    """
    Returns the Domain requested
    ---
    responses:
        200:
            description: returns the domain indicated
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Domain'
    """

    try:
        domain=domainService.getDomain(domainId)
        return jsonify({"message":"Success", "data":domain}),200
    except Exception as e:
        return jsonify({"message":"Error: "+str(e)}),500

@app.route('/domain/<domainId>', methods=["PUT"])
@login_required
def updateDomain(domainId):
    """
    Updates the Domain indicated
    ---
    responses:
        200:
            description: acknowledges the request
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Acknowledge'
    """

    try:
        domainService.updateDomain(domainId)
        return jsonify({"message":"Success"}),200
    except Exception as e:
        return jsonify({"message":"Error: "+str(e)}),500

@app.route('/domain/<domainId>', methods=["DELETE"])
@login_required
def removeDomain(domainId):
    """
    Remove and deletes the Domain indicated
    ---
    responses:
        200:
            description: acknowledges the request
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Acknowledge'
    """

    try:
        domainService.removeDomain(domainId)
        return jsonify({"message":"Success"}),200
    except Exception as e:
        return jsonify({"message":"Error: "+str(e)}),500