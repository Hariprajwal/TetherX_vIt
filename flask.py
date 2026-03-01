# edge_node.py (Flask)
# Run this as a separate process: python flask.py
# It listens on port 5001 (different from Django's 8000)
# Simulates an edge computing node for low-latency ML inference

from flask import Flask, request, jsonify
import sys
import os
import time

# Add project root to path so we can import the LSTM predictor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urbanSecurity_app.utils.RoleLSTM import RolePredictor

app = Flask(__name__)


@app.route('/edge-predict', methods=['POST'])
def edge_predict():
    """Edge node endpoint: runs LSTM role prediction with latency measurement."""
    try:
        start_time = time.time()

        data = request.get_json()
        if not data or 'context' not in data:
            return jsonify({"error": "Missing 'context' in request"}), 400

        context = data['context']
        if not isinstance(context, list) or len(context) != 5:
            return jsonify({"error": "Context must be a list of exactly 5 floats"}), 400

        # Run inference using the loaded LSTM model
        role = RolePredictor.predict(context)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return jsonify({
            "recommended_role": role,
            "status": "success",
            "latency_ms": latency_ms,
            "edge_node": "local_simulation"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check for edge node."""
    return jsonify({"status": "healthy", "node": "edge_local"})


if __name__ == '__main__':
    print("Starting Edge Node on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)