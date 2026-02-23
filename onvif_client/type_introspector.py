"""Recursive XSD type introspection for dynamic parameter form generation."""

from zeep.xsd.types.complex import ComplexType

MAX_RECURSION_DEPTH = 5


def introspect_operation(client, binding_name: str, operation_name: str) -> list:
    """Extract the input parameter schema for an operation.

    Returns a list of parameter descriptors:
    [
        {
            "name": "ProfileToken",
            "type": "string",
            "required": True,
            "is_complex": False,
            "min_occurs": 1,
            "max_occurs": 1,
        },
        {
            "name": "Configuration",
            "type": "VideoSourceConfiguration",
            "required": False,
            "is_complex": True,
            "children": [ ... ]
        }
    ]
    """
    # Look up binding directly (ONVIF WSDLs don't define <service> elements)
    binding = client.wsdl.bindings.get(binding_name)
    if binding:
        operation = binding._operations.get(operation_name)
        if operation and operation.input and operation.input.body:
            body_type = operation.input.body.type
            if hasattr(body_type, "elements"):
                return _resolve_elements(body_type.elements, depth=0)
    return []


def _resolve_elements(elements, depth: int) -> list:
    """Recursively resolve element list into parameter descriptors."""
    result = []
    for attr_name, element in elements:
        # Skip AnyAttribute / Any elements that lack a .type property
        if not hasattr(element, "type"):
            continue

        param = {
            "name": getattr(element, "name", None) or attr_name,
            "required": getattr(element, "min_occurs", 0) >= 1,
            "min_occurs": getattr(element, "min_occurs", 0),
            "max_occurs": str(getattr(element, "max_occurs", 1)),
        }

        elem_type = element.type
        if isinstance(elem_type, ComplexType) and depth < MAX_RECURSION_DEPTH:
            param["type"] = getattr(elem_type, "name", None) or "complexType"
            param["is_complex"] = True
            if hasattr(elem_type, "elements"):
                param["children"] = _resolve_elements(elem_type.elements, depth + 1)
            else:
                param["children"] = []

            # Check for enum restrictions on attributes
            if hasattr(elem_type, "attributes"):
                for attr_key, attr_val in elem_type.attributes:
                    # Skip AnyAttribute entries that lack a .type property
                    if not hasattr(attr_val, "type"):
                        continue
                    attr_param = {
                        "name": f"@{attr_key}",
                        "type": _get_simple_type_name(attr_val.type),
                        "required": False,
                        "is_complex": False,
                        "min_occurs": 0,
                        "max_occurs": "1",
                    }
                    enum_values = _get_enum_values(attr_val.type)
                    if enum_values:
                        attr_param["enum_values"] = enum_values
                    param["children"].append(attr_param)
        else:
            param["type"] = _get_simple_type_name(elem_type)
            param["is_complex"] = False
            enum_values = _get_enum_values(elem_type)
            if enum_values:
                param["enum_values"] = enum_values

        result.append(param)
    return result


def _get_simple_type_name(xsd_type) -> str:
    """Map zeep XSD type to a friendly name."""
    name = getattr(xsd_type, "name", None) or str(xsd_type)
    type_map = {
        "string": "string",
        "int": "integer",
        "integer": "integer",
        "long": "integer",
        "unsignedInt": "integer",
        "unsignedLong": "integer",
        "short": "integer",
        "float": "float",
        "double": "float",
        "decimal": "float",
        "boolean": "boolean",
        "anyURI": "string",
        "dateTime": "datetime",
        "duration": "string",
        "token": "string",
        "QName": "string",
        "NCName": "string",
        "ReferenceToken": "string",
        "base64Binary": "string",
    }
    return type_map.get(name, name)


def _get_enum_values(xsd_type) -> list:
    """Extract enumeration values from a restricted simple type."""
    if hasattr(xsd_type, "accepted_values") and xsd_type.accepted_values:
        return [str(v) for v in xsd_type.accepted_values]
    return []
