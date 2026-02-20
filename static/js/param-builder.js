/**
 * Dynamic parameter form builder for ONVIF operation parameters.
 * Converts JSON parameter schemas into interactive HTML form fields.
 */

const ParamBuilder = {
    /**
     * Build parameter form from schema returned by /api/operation-params.
     * @param {Array} params - Parameter descriptors
     * @param {HTMLElement} container - DOM container to append fields into
     * @param {string} prefix - Dot-notation prefix for nested params
     */
    buildForm(params, container, prefix = "") {
        container.innerHTML = "";
        if (!params || params.length === 0) {
            container.innerHTML = '<div class="text-muted small fst-italic">No parameters required.</div>';
            return;
        }
        params.forEach(param => {
            if (param.is_complex && param.children && param.children.length > 0) {
                this._buildComplexField(param, container, prefix);
            } else {
                this._buildSimpleField(param, container, prefix);
            }
        });
    },

    /**
     * Build a simple input field (text, number, boolean, enum, etc.)
     */
    _buildSimpleField(param, container, prefix) {
        const fullName = prefix ? `${prefix}.${param.name}` : param.name;

        const group = document.createElement("div");
        group.className = "mb-2";

        const label = document.createElement("label");
        label.className = "form-label" + (param.required ? " param-required" : "");
        label.textContent = param.name;

        const typeHint = document.createElement("span");
        typeHint.className = "text-muted ms-1";
        typeHint.style.fontSize = "0.7rem";
        typeHint.textContent = `(${param.type})`;
        label.appendChild(typeHint);

        group.appendChild(label);

        let input;

        if (param.enum_values && param.enum_values.length > 0) {
            // Enum -> dropdown
            input = document.createElement("select");
            input.className = "form-select form-select-sm";
            const emptyOpt = document.createElement("option");
            emptyOpt.value = "";
            emptyOpt.textContent = "-- select --";
            input.appendChild(emptyOpt);
            param.enum_values.forEach(val => {
                const opt = document.createElement("option");
                opt.value = val;
                opt.textContent = val;
                input.appendChild(opt);
            });
        } else if (param.type === "boolean") {
            input = document.createElement("select");
            input.className = "form-select form-select-sm";
            ["", "true", "false"].forEach(val => {
                const opt = document.createElement("option");
                opt.value = val;
                opt.textContent = val || "-- select --";
                input.appendChild(opt);
            });
        } else if (param.type === "integer") {
            input = document.createElement("input");
            input.type = "number";
            input.step = "1";
            input.className = "form-control form-control-sm";
            input.placeholder = param.name;
        } else if (param.type === "float") {
            input = document.createElement("input");
            input.type = "number";
            input.step = "any";
            input.className = "form-control form-control-sm";
            input.placeholder = param.name;
        } else {
            input = document.createElement("input");
            input.type = "text";
            input.className = "form-control form-control-sm";
            input.placeholder = param.name;
        }

        input.dataset.paramName = fullName;
        input.dataset.paramType = param.type;
        if (param.required) {
            input.required = true;
        }

        group.appendChild(input);
        container.appendChild(group);
    },

    /**
     * Build a collapsible fieldset for complex (nested) types.
     */
    _buildComplexField(param, container, prefix) {
        const fullName = prefix ? `${prefix}.${param.name}` : param.name;

        const fieldset = document.createElement("div");
        fieldset.className = "param-fieldset";

        const legend = document.createElement("div");
        legend.className = "d-flex align-items-center justify-content-between mb-1";

        const legendText = document.createElement("span");
        legendText.className = param.required ? "param-required" : "";
        legendText.innerHTML = `<strong>${param.name}</strong> <span class="text-muted" style="font-size:0.7rem">(${param.type})</span>`;

        const toggleBtn = document.createElement("span");
        toggleBtn.className = "toggle-btn small";
        toggleBtn.innerHTML = '<i class="bi bi-chevron-down"></i>';

        legend.appendChild(legendText);
        legend.appendChild(toggleBtn);
        fieldset.appendChild(legend);

        const childContainer = document.createElement("div");
        childContainer.className = "ps-2";
        childContainer.style.display = "none"; // collapsed by default

        this.buildForm(param.children, childContainer, fullName);
        fieldset.appendChild(childContainer);

        // Toggle expand/collapse
        toggleBtn.addEventListener("click", () => {
            const isHidden = childContainer.style.display === "none";
            childContainer.style.display = isHidden ? "block" : "none";
            toggleBtn.innerHTML = isHidden
                ? '<i class="bi bi-chevron-up"></i>'
                : '<i class="bi bi-chevron-down"></i>';
        });

        container.appendChild(fieldset);
    },

    /**
     * Collect all parameter values from the form into a nested dict.
     * Empty values are omitted (optional params not sent).
     */
    collectParams(container) {
        const result = {};
        const inputs = container.querySelectorAll("[data-param-name]");

        inputs.forEach(input => {
            const value = input.value.trim();
            if (value === "") return; // skip empty optional fields

            const path = input.dataset.paramName.split(".");
            let current = result;

            for (let i = 0; i < path.length - 1; i++) {
                if (!current[path[i]]) {
                    current[path[i]] = {};
                }
                current = current[path[i]];
            }

            const finalKey = path[path.length - 1];
            current[finalKey] = this._castValue(value, input.dataset.paramType);
        });

        return result;
    },

    /**
     * Cast string value to appropriate JS type based on XSD type.
     */
    _castValue(value, type) {
        switch (type) {
            case "integer":
                return parseInt(value, 10);
            case "float":
                return parseFloat(value);
            case "boolean":
                return value === "true";
            default:
                return value;
        }
    }
};
