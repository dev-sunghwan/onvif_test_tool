"""ONVIF Command Tester - Flask Web Application."""

import json
import os
import sys
import threading
import webbrowser
from datetime import date, datetime
from datetime import time as dt_time
from datetime import timedelta
from decimal import Decimal

from flask import Flask, jsonify, render_template, request
from flask.json.provider import DefaultJSONProvider
from lxml import etree

from config import DEFAULT_PORT, ONVIF_PRESETS
from onvif_client.command_executor import CommandExecutor
from onvif_client.serializer import ONVIFSerializer
from onvif_client.type_introspector import introspect_operation
from onvif_client.wsdl_loader import WSDLLoader


def _get_base_path():
    """Return base path for templates/static (handles PyInstaller bundle)."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


class ONVIFJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles zeep-specific types."""

    @staticmethod
    def default(o):
        if isinstance(o, etree._Element):
            return ONVIFSerializer._element_to_dict(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, dt_time):
            return o.isoformat()
        if isinstance(o, timedelta):
            total = int(o.total_seconds())
            h, rem = divmod(total, 3600)
            m, s = divmod(rem, 60)
            return f"PT{h}H{m}M{s}S" if h else f"PT{m}M{s}S" if m else f"PT{s}S"
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, bytes):
            return o.decode("utf-8", errors="replace")
        if isinstance(o, set):
            return list(o)
        return str(o)


_base = _get_base_path()
app = Flask(
    __name__,
    template_folder=os.path.join(_base, "templates"),
    static_folder=os.path.join(_base, "static"),
)
app.json_provider_class = ONVIFJSONProvider
app.json = ONVIFJSONProvider(app)
wsdl_loader = WSDLLoader()
executor = CommandExecutor()


@app.route("/")
def index():
    """Render main page."""
    return render_template("index.html", presets=ONVIF_PRESETS)


@app.route("/api/presets", methods=["GET"])
def api_presets():
    """Return ONVIF WSDL presets."""
    return jsonify(ONVIF_PRESETS)


@app.route("/api/load-wsdl", methods=["POST"])
def api_load_wsdl():
    """Load a WSDL URL and return available bindings + operations."""
    data = request.get_json()
    wsdl_url = data.get("wsdl_url", "").strip()

    if not wsdl_url:
        return jsonify({"success": False, "error": "WSDL URL is required"}), 400

    try:
        result = wsdl_loader.load_wsdl(wsdl_url)
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/operation-params", methods=["POST"])
def api_operation_params():
    """Return the parameter schema for a specific operation."""
    data = request.get_json()
    wsdl_url = data.get("wsdl_url", "").strip()
    binding_name = data.get("binding_name", "").strip()
    operation_name = data.get("operation_name", "").strip()

    if not all([wsdl_url, binding_name, operation_name]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        client = wsdl_loader.get_client(wsdl_url)
        params = introspect_operation(client, binding_name, operation_name)
        return jsonify({"success": True, "params": params})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/execute", methods=["POST"])
def api_execute():
    """Execute an ONVIF operation on the camera."""
    data = request.get_json()

    wsdl_url = data.get("wsdl_url", "").strip()
    binding_name = data.get("binding_name", "").strip()
    operation_name = data.get("operation_name", "").strip()
    camera_ip = data.get("camera_ip", "").strip()
    camera_port = int(data.get("camera_port", 80))
    username = data.get("username", "").strip()
    password = data.get("password", "")
    params = data.get("params", {})
    use_https = data.get("use_https", False)

    if not all([wsdl_url, binding_name, operation_name, camera_ip, username]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        result = executor.execute(
            wsdl_url=wsdl_url,
            binding_name=binding_name,
            operation_name=operation_name,
            camera_ip=camera_ip,
            camera_port=camera_port,
            username=username,
            password=password,
            params=params,
            use_https=use_https,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "result_json": None,
            "request_xml": "",
            "response_xml": "",
            "error": f"Server error: {type(e).__name__}: {e}",
            "execution_time_ms": 0,
        }), 500


if __name__ == "__main__":
    is_frozen = getattr(sys, "frozen", False)
    port = DEFAULT_PORT
    if is_frozen:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(debug=not is_frozen, host="0.0.0.0", port=port)
