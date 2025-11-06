# D:\web_server\app.py
from flask import Flask, render_template, request, jsonify, Response
import requests
import os

# Where the internal App Server listens (set in the Web VM environment)
APP_INTERNAL = os.environ.get("APP_INTERNAL", "http://127.0.0.1:5001")

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    # The frontend JS will call relative /api endpoints, so no cross-origin needed
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', institute_name="V Cube software solution")

# --- Proxy endpoints ---
def forward_request(path):
    """
    Forward the incoming Flask request to the internal App Server and return the App Server response.
    This version logs detailed errors to the Web server console for debugging.
    """
    url = APP_INTERNAL.rstrip('/') + '/' + path.lstrip('/')
    try:
        # prepare headers (omit Host to avoid confusion)
        headers = {}
        for k, v in request.headers.items():
            if k.lower() == 'host':
                continue
            headers[k] = v

        # Use json body if present, otherwise raw data
        json_body = None
        raw_body = None
        try:
            json_body = request.get_json(silent=True)
        except Exception:
            json_body = None
        if json_body is None:
            raw_body = request.get_data()

        # Forward the request with a reasonable timeout
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            json=json_body if json_body is not None else None,
            data=raw_body if json_body is None and raw_body else None,
            timeout=10
        )

        # Try to pass through content-type and status
        response_headers = {}
        for k, v in resp.headers.items():
            # strip hop-by-hop headers that Flask/werkzeug will manage
            if k.lower() in ('content-encoding', 'transfer-encoding', 'connection', 'keep-alive'):
                continue
            response_headers[k] = v

        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except requests.RequestException as e:
        # Detailed debug logging for the console
        print("=== PROXY ERROR ===")
        print("Proxy URL:", url)
        print("Request method:", request.method)
        print("Request path:", request.path)
        try:
            print("Request headers:", dict(request.headers))
            print("Request args:", request.args.to_dict())
            # print small preview of body
            body_preview = request.get_data()[:2000]
            print("Request body preview:", body_preview)
        except Exception as ex:
            print("Error reading incoming request details:", repr(ex))

        print("Requests exception repr:", repr(e))
        # If the requests response object exists on the exception, show it
        resp = getattr(e, 'response', None)
        if resp is not None:
            print("Inner response status:", getattr(resp, 'status_code', None))
            try:
                print("Inner response text:", resp.text[:2000])
            except Exception:
                pass
        print("=== END PROXY ERROR ===")

        # Return user-facing error (keeps previous behaviour)
        return jsonify({"message": "Internal proxy error", "error": str(e)}), 502

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_api(path):
    return forward_request('api/' + path)

# For convenience, also proxy root-level API paths
@app.route('/api', methods=['GET', 'POST'])
def proxy_api_root():
    return forward_request('api')

if __name__ == '__main__':
    # run web server publicly; APP_INTERNAL must point to the App Server (private IP)
    web_host = os.environ.get('WEB_HOST', '0.0.0.0')
    web_port = int(os.environ.get('WEB_PORT', 5000))
    print("Starting web server. APP_INTERNAL =", APP_INTERNAL)
    app.run(host=web_host, port=web_port, debug=True)
