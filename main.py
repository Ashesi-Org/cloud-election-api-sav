# with reference from https://pythonbasics.org/flask-rest-api/  ,
#                     https://github.com/Ashesi-Org/web-tech-2023-2/blob/main/code_more_flask.py

import json
import functions_framework
from flask import Flask, request, jsonify

app = Flask(__name__)

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials.

firebase_admin.initialize_app()
db= firestore.client()


app = Flask(__name__)

@functions_framework.http
def hello_http(request):
    request = json.loads(request)
    request_json = request.get_json()
    # request_args = request.args

    if request.method == 'POST' and 'voterId' in request_json:
        return register_voter()
    
    elif request.method == 'GET' and request.path == "/voters":
        return get_voter(request.args.get("voterId"))
    
    elif request.method == 'DELETE' and 'voterId' in request_json:
        return deregister_voter(request.args.get("voterId"))
    
    elif request.method == 'PUT' and 'voterId' in request_json:
        return update_voter()
    
    elif request.method == 'POST' and 'electionId' in request_json:
        return create_election()
    
    elif request.method == 'GET' and request.path == "/elections":
        return get_election(request.args.get("electionId"))
    
    elif request.method == 'DELETE' and 'electionId' in request_json:
        return delete_election(request.args.get("electionId"))
    
    elif request.method == 'PATCH' and 'electionId' in request_json:
        electionId, candidateId = request.path.split("/")[-2:]
        return vote(electionId, candidateId)
    
    else:
        return "Invalid request"


# Endpoints:
    # Voter endpoints
# @app.route('/')
def index():
    return 'Welcome to the electronic voting system!'

# @app.route('/voters', methods=['POST'])
def register_voter():
    if not request.data:
        return jsonify({"error": "Request body is empty"}), 400
    record = json.loads(request.data)
    voter_ref = db.collection("voters").document(record["voterId"])
    voter = voter_ref.get()
    if voter.exists:
        return jsonify({"error": "Voter already exists"}), 400
    else:
        db.collection("voters").document(record["voterId"]).set(record)
        return jsonify({"success": "Voter successfully added!"}), 200

# @app.route('/voters/<voterId>', methods=['DELETE'])
def deregister_voter(voterId):
    voter_ref = db.collection("voters").document(voterId)
    voter = voter_ref.get()
    if voter.exists:
        voter_ref.delete()
        return jsonify(voter.to_dict()), 200
    else:
        return jsonify({"error": "Voter does not exist"}), 400

# @app.route('/voters/<voterId>', methods=['PUT'])
def update_voter(voterId):
    voter_ref = db.collection("voters").document(voterId)
    voter = voter_ref.get()
    if voter.exists:
        voter_ref.update(json.loads(request.data))
        return jsonify({"success": "Voter details successfully updated!"}), 200
    else:
        return jsonify({"error": "Voter does not exist!"}), 400


# @app.route('/voters/<voterId>', methods=['GET'])
def get_voter(voterId):
    voterId = request.args.get("voterId")
    voter_ref = db.collection("voters").document(voterId)
    voter = voter_ref.get()
    if voter.exists:
        return jsonify(voter.to_dict()), 200
    else:
        return jsonify({"error": "Voter does not exist!"}), 400


    # Election endpoints
# @app.route('/elections', methods=['POST'])
def create_election():
    if not request.data:
        # logging.error(f"Request body empty")
        return jsonify({"error": "Cannot send empty request!"}), 400
    record = json.loads(request.data)
    election_ref = db.collection("elections").document(record["electionId"])
    election = election_ref.get()
    if election.exists:
        return jsonify({"error": "Election already exists!"}), 400
    else:
        db.collection("elections").document(record["electionId"]).set(record)
        return jsonify(record), 200

# @app.route('/elections/<electionId>', methods=['DELETE'])
def delete_election(electionId):
    election_ref = db.collection("elections").document(electionId)
    election = election_ref.get()
    if election.exists:
        election_ref.delete()
        return jsonify(election.to_dict()), 200
    else:
        # logging.error(f"Election {electionId} does not exist")
        return jsonify({"error": "Election does not exist!"}), 400

# @app.route('/elections/<electionId>', methods=['GET'])
def get_election(electionId):
    election_ref = db.collection("elections").document(electionId)
    election = election_ref.get()
    if election.exists:
        return jsonify(election.to_dict()), 200
    else:
        # logging.error(f"Election {electionId} does not exist")
        return jsonify({"error": "Election does not exist!"}), 400   

# @app.route('/elections/<electionId>/<candidateId>', methods=['PATCH'])
def vote(electionId, candidateId):
    try:
        election_ref = db.collection("elections").document(electionId)
        election = election_ref.get()
        if election.exists:
            candidates = election.to_dict().get("candidates")
            if not candidates:
                return jsonify({"error": "No candidates found!"}), 404
            for candidate in candidates:
                # print(candidate)
                if candidate.get("candidateId") == candidateId:
                    candidate["votes"] += 1
                    election_ref.update({"candidates": candidates})
                    return jsonify(election.to_dict()), 200
        else:
            # logging.error(f"Election {electionId} does not exist")
            return jsonify({"error": "Election does not exist!"}), 404
    except ValueError:
        # logging.error(f"Invalid candidate ID {candidateId}")
        return jsonify({"error": "Invalid candidate ID"}), 400
    except Exception as e:
        # logging.error(str(e))
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run()