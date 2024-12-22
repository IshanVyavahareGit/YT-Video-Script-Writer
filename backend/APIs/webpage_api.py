from flask import Blueprint, request, jsonify
from PseudoAgents import WebpageAgent
from utils.exceptions import KeyNotFoundError,ProjectNotFoundError

webpage_blueprint = Blueprint('webpage', __name__)

@webpage_blueprint.route('/fetchWebPagesFromWeb', methods=['POST'])
def fetchWebPagesFromWeb():
    try:
        data = request.get_json()
        userEmail = data.get('userEmail')
        projectID = data.get('projectID')

        if not userEmail:
            return jsonify({"error": "Missing required field: userEmail", "success": False}), 400

        if not projectID:
            return jsonify({"error": "Missing required field: projectID", "success": False}), 400
        
        webagent = WebpageAgent(projectID, userEmail)
        webpage_content = webagent.fetchWebPagesFromWeb()

        return jsonify({"message":"Successfully retrieved webpages", "webpage content":webpage_content, "success": True}), 200
    except (KeyNotFoundError,ProjectNotFoundError) as e:
        return jsonify({"error": e.message, "success": False}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred: " + e.message or e, "success": False}), 500
    
