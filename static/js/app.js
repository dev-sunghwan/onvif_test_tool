/**
 * ONVIF Command Tester - Main Application JavaScript
 */

(function () {
    "use strict";

    // ── State ──────────────────────────────────────────────
    let currentBindings = {};    // { qualifiedName: { local_name, operations } }
    let currentWsdlUrl = "";

    // ── DOM Elements ───────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const cameraIp = $("#camera-ip");
    const cameraPort = $("#camera-port");
    const cameraUser = $("#camera-user");
    const cameraPass = $("#camera-pass");
    const togglePass = $("#toggle-pass");
    const useHttps = $("#use-https");
    const wsdlPreset = $("#wsdl-preset");
    const wsdlUrl = $("#wsdl-url");
    const btnLoadWsdl = $("#btn-load-wsdl");
    const wsdlStatus = $("#wsdl-status");
    const bindingSelect = $("#binding-select");
    const operationSelect = $("#operation-select");
    const paramsContainer = $("#params-container");
    const paramsForm = $("#params-form");
    const btnExecute = $("#btn-execute");
    const btnTestConn = $("#btn-test-connection");
    const btnCopy = $("#btn-copy");
    const loadingOverlay = $("#loading-overlay");
    const loadingText = $("#loading-text");
    const resultJson = $("#result-json");
    const resultReqXml = $("#result-req-xml");
    const resultResXml = $("#result-res-xml");
    const statusBar = $("#status-bar");
    const statusBadge = $("#status-badge");
    const statusTime = $("#status-time");

    // ── Session Storage ────────────────────────────────────
    function saveConnectionInfo() {
        const info = {
            ip: cameraIp.value,
            port: cameraPort.value,
            user: cameraUser.value,
            https: useHttps.checked,
        };
        sessionStorage.setItem("onvif_conn", JSON.stringify(info));
    }

    function loadConnectionInfo() {
        try {
            const info = JSON.parse(sessionStorage.getItem("onvif_conn"));
            if (info) {
                cameraIp.value = info.ip || "";
                cameraPort.value = info.port || "80";
                cameraUser.value = info.user || "";
                useHttps.checked = info.https || false;
            }
        } catch (e) { /* ignore */ }
    }

    // ── Toast Notifications ────────────────────────────────
    function showToast(message, type = "danger") {
        const container = $("#toast-container");
        const id = "toast-" + Date.now();
        const bgClass = type === "success" ? "text-bg-success" : "text-bg-danger";
        const html = `
            <div id="${id}" class="toast align-items-center ${bgClass} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto"
                            data-bs-dismiss="toast"></button>
                </div>
            </div>`;
        container.insertAdjacentHTML("beforeend", html);
        const toastEl = document.getElementById(id);
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
        toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
    }

    // ── Loading ────────────────────────────────────────────
    function showLoading(text = "Loading...") {
        loadingText.textContent = text;
        loadingOverlay.style.display = "flex";
    }

    function hideLoading() {
        loadingOverlay.style.display = "none";
    }

    // ── API Calls ──────────────────────────────────────────
    async function apiCall(url, data) {
        const resp = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        const contentType = resp.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
            const text = await resp.text();
            throw new Error(`Server returned non-JSON response (HTTP ${resp.status}). Check server logs.`);
        }
        return resp.json();
    }

    // ── WSDL Loading ───────────────────────────────────────
    async function loadWsdl() {
        const url = wsdlUrl.value.trim();
        if (!url) {
            showToast("Please enter a WSDL URL.");
            return;
        }

        showLoading("Loading WSDL... (first load may be slow)");
        btnLoadWsdl.disabled = true;

        try {
            const result = await apiCall("/api/load-wsdl", { wsdl_url: url });

            if (!result.success) {
                showToast("Failed to load WSDL: " + result.error);
                showWsdlStatus("Failed: " + result.error, false);
                return;
            }

            currentBindings = result.bindings;
            currentWsdlUrl = url;

            // Populate binding dropdown
            bindingSelect.innerHTML = "";
            const bindingKeys = Object.keys(currentBindings);

            if (bindingKeys.length === 0) {
                bindingSelect.innerHTML = '<option value="">No bindings found</option>';
                bindingSelect.disabled = true;
                return;
            }

            bindingKeys.forEach(key => {
                const opt = document.createElement("option");
                opt.value = key;
                opt.textContent = currentBindings[key].local_name +
                    ` (${currentBindings[key].operations.length} ops)`;
                bindingSelect.appendChild(opt);
            });

            bindingSelect.disabled = false;

            // Auto-select first binding and load its operations
            bindingSelect.selectedIndex = 0;
            onBindingChange();

            const totalOps = bindingKeys.reduce((sum, k) => sum + currentBindings[k].operations.length, 0);
            showWsdlStatus(`Loaded: ${bindingKeys.length} binding(s), ${totalOps} operations`, true);

        } catch (e) {
            showToast("Error loading WSDL: " + e.message);
            showWsdlStatus("Error: " + e.message, false);
        } finally {
            btnLoadWsdl.disabled = false;
            hideLoading();
        }
    }

    function showWsdlStatus(message, success) {
        wsdlStatus.style.display = "block";
        const alert = wsdlStatus.querySelector(".alert");
        alert.className = "alert py-1 px-2 mb-0 small " +
            (success ? "alert-success" : "alert-danger");
        alert.textContent = message;
    }

    // ── Binding Change ─────────────────────────────────────
    function onBindingChange() {
        const bindingName = bindingSelect.value;
        if (!bindingName || !currentBindings[bindingName]) {
            operationSelect.innerHTML = '<option value="">-- Select binding first --</option>';
            operationSelect.disabled = true;
            btnExecute.disabled = true;
            paramsContainer.style.display = "none";
            return;
        }

        const ops = currentBindings[bindingName].operations;
        operationSelect.innerHTML = "";
        ops.forEach(op => {
            const opt = document.createElement("option");
            opt.value = op;
            opt.textContent = op;
            operationSelect.appendChild(opt);
        });

        operationSelect.disabled = false;
        btnExecute.disabled = false;

        // Auto-load params for first operation
        if (ops.length > 0) {
            operationSelect.selectedIndex = 0;
            onOperationChange();
        }
    }

    // ── Operation Change ───────────────────────────────────
    async function onOperationChange() {
        const bindingName = bindingSelect.value;
        const operationName = operationSelect.value;

        if (!bindingName || !operationName) {
            paramsContainer.style.display = "none";
            return;
        }

        try {
            const result = await apiCall("/api/operation-params", {
                wsdl_url: currentWsdlUrl,
                binding_name: bindingName,
                operation_name: operationName,
            });

            if (result.success) {
                paramsContainer.style.display = "block";
                ParamBuilder.buildForm(result.params, paramsForm);
            } else {
                paramsContainer.style.display = "none";
                showToast("Failed to load params: " + result.error);
            }
        } catch (e) {
            paramsContainer.style.display = "none";
        }
    }

    // ── Execute Operation ──────────────────────────────────
    async function executeOperation() {
        const ip = cameraIp.value.trim();
        const port = cameraPort.value.trim();
        const user = cameraUser.value.trim();
        const pass = cameraPass.value;

        if (!ip || !user) {
            showToast("Please enter camera IP and username.");
            return;
        }

        const bindingName = bindingSelect.value;
        const operationName = operationSelect.value;

        if (!bindingName || !operationName) {
            showToast("Please select an operation.");
            return;
        }

        saveConnectionInfo();
        const params = ParamBuilder.collectParams(paramsForm);

        showLoading("Executing " + operationName + "...");
        btnExecute.disabled = true;

        try {
            const result = await apiCall("/api/execute", {
                wsdl_url: currentWsdlUrl,
                binding_name: bindingName,
                operation_name: operationName,
                camera_ip: ip,
                camera_port: parseInt(port) || 80,
                username: user,
                password: pass,
                params: params,
                use_https: useHttps.checked,
            });

            displayResult(result);

        } catch (e) {
            showToast("Execution error: " + e.message);
            displayResult({
                success: false,
                error: e.message,
                result_json: null,
                request_xml: "",
                response_xml: "",
                execution_time_ms: 0,
            });
        } finally {
            btnExecute.disabled = false;
            hideLoading();
        }
    }

    // ── Display Result ─────────────────────────────────────
    function displayResult(result) {
        // JSON
        if (result.result_json !== null && result.result_json !== undefined) {
            const jsonStr = JSON.stringify(result.result_json, null, 2);
            resultJson.innerHTML = highlightJson(jsonStr);
        } else if (result.error) {
            resultJson.innerHTML = `<span style="color:#f44747">Error: ${escapeHtml(result.error)}</span>`;
        } else {
            resultJson.innerHTML = '<span class="text-muted">No result.</span>';
        }

        // Request XML
        resultReqXml.innerHTML = result.request_xml
            ? highlightXml(result.request_xml)
            : '<span class="text-muted">No request captured.</span>';

        // Response XML
        resultResXml.innerHTML = result.response_xml
            ? highlightXml(result.response_xml)
            : '<span class="text-muted">No response captured.</span>';

        // Status bar
        statusBar.style.display = "flex";
        if (result.success) {
            statusBadge.innerHTML = '<span class="badge bg-success">SUCCESS</span>';
        } else {
            statusBadge.innerHTML = '<span class="badge bg-danger">FAILED</span>';
        }
        statusTime.textContent = result.execution_time_ms
            ? `${result.execution_time_ms} ms`
            : "";

        // Show copy button
        btnCopy.style.display = "inline-block";
    }

    // ── Syntax Highlighting ────────────────────────────────
    function highlightJson(json) {
        const escaped = escapeHtml(json);
        return escaped.replace(
            /("(\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g,
            (match) => {
                let cls = "json-number";
                if (/^"/.test(match)) {
                    cls = /:$/.test(match) ? "json-key" : "json-string";
                } else if (/true|false/.test(match)) {
                    cls = "json-boolean";
                } else if (/null/.test(match)) {
                    cls = "json-null";
                }
                return `<span class="${cls}">${match}</span>`;
            }
        );
    }

    function highlightXml(xml) {
        const escaped = escapeHtml(xml);
        return escaped
            // Tags
            .replace(/(&lt;\/?)([\w:-]+)/g, '$1<span class="xml-tag">$2</span>')
            // Attributes
            .replace(/([\w:-]+)(=)(&quot;[^&]*&quot;)/g,
                '<span class="xml-attr-name">$1</span>$2<span class="xml-attr-value">$3</span>');
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    // ── Test Connection ────────────────────────────────────
    async function testConnection() {
        const ip = cameraIp.value.trim();
        const port = cameraPort.value.trim();
        const user = cameraUser.value.trim();
        const pass = cameraPass.value;

        if (!ip || !user) {
            showToast("Please enter camera IP and username.");
            return;
        }

        saveConnectionInfo();
        showLoading("Testing connection...");
        btnTestConn.disabled = true;

        try {
            const result = await apiCall("/api/execute", {
                wsdl_url: "https://www.onvif.org/ver10/device/wsdl/devicemgmt.wsdl",
                binding_name: "{http://www.onvif.org/ver10/device/wsdl}DeviceBinding",
                operation_name: "GetDeviceInformation",
                camera_ip: ip,
                camera_port: parseInt(port) || 80,
                username: user,
                password: pass,
                params: {},
                use_https: useHttps.checked,
            });

            if (result.success) {
                const info = result.result_json;
                showToast(
                    `Connected! ${info.Manufacturer || ""} ${info.Model || ""} (FW: ${info.FirmwareVersion || "N/A"})`,
                    "success"
                );
                displayResult(result);
            } else {
                showToast("Connection failed: " + result.error);
                displayResult(result);
            }
        } catch (e) {
            showToast("Connection error: " + e.message);
        } finally {
            btnTestConn.disabled = false;
            hideLoading();
        }
    }

    // ── Copy to Clipboard ──────────────────────────────────
    function copyResult() {
        // Copy the currently active tab's content
        const activeTab = document.querySelector(".tab-pane.show.active .result-content");
        if (activeTab) {
            navigator.clipboard.writeText(activeTab.textContent).then(() => {
                showToast("Copied to clipboard!", "success");
            });
        }
    }

    // ── Password Toggle ────────────────────────────────────
    function togglePassword() {
        const isPassword = cameraPass.type === "password";
        cameraPass.type = isPassword ? "text" : "password";
        togglePass.querySelector("i").className =
            isPassword ? "bi bi-eye-slash" : "bi bi-eye";
    }

    // ── Event Listeners ────────────────────────────────────
    wsdlPreset.addEventListener("change", () => {
        const selected = wsdlPreset.value;
        if (selected) {
            wsdlUrl.value = selected;
        }
    });

    btnLoadWsdl.addEventListener("click", loadWsdl);
    wsdlUrl.addEventListener("keydown", (e) => {
        if (e.key === "Enter") loadWsdl();
    });

    bindingSelect.addEventListener("change", onBindingChange);
    operationSelect.addEventListener("change", onOperationChange);
    btnExecute.addEventListener("click", executeOperation);
    btnTestConn.addEventListener("click", testConnection);
    btnCopy.addEventListener("click", copyResult);
    togglePass.addEventListener("click", togglePassword);

    // HTTPS toggle: auto-switch port 80 <-> 443
    useHttps.addEventListener("change", () => {
        const current = cameraPort.value;
        if (useHttps.checked && current === "80") {
            cameraPort.value = "443";
        } else if (!useHttps.checked && current === "443") {
            cameraPort.value = "80";
        }
        saveConnectionInfo();
    });

    // Save connection info on input change
    [cameraIp, cameraPort, cameraUser].forEach(el => {
        el.addEventListener("change", saveConnectionInfo);
    });

    // ── Init ───────────────────────────────────────────────
    loadConnectionInfo();

})();
