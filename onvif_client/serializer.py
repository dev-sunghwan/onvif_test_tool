"""Convert zeep response objects to JSON-serializable dicts."""

import json
from datetime import date, datetime
from datetime import time as dt_time
from datetime import timedelta
from decimal import Decimal

import zeep.helpers
from lxml import etree


class ONVIFSerializer:
    """Custom JSON serializer that handles zeep-specific types."""

    @staticmethod
    def serialize(zeep_object):
        """Convert zeep response object to a JSON-serializable dict."""
        raw = zeep.helpers.serialize_object(zeep_object, target_cls=dict)
        return ONVIFSerializer._make_json_safe(raw)

    @staticmethod
    def _make_json_safe(obj):
        if isinstance(obj, dict):
            return {k: ONVIFSerializer._make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [ONVIFSerializer._make_json_safe(item) for item in obj]
        elif isinstance(obj, etree._Element):
            return ONVIFSerializer._element_to_dict(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, dt_time):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        return obj

    @staticmethod
    def _element_to_dict(element):
        """Convert an lxml Element to a JSON-friendly dict."""
        # Strip namespace for cleaner keys
        tag = etree.QName(element.tag).localname if "}" in element.tag else element.tag

        children = list(element)
        if not children and element.text and element.text.strip():
            # Leaf element with text content
            return {tag: element.text.strip()}

        if not children and not (element.text and element.text.strip()):
            # Empty element - include attributes if any
            if element.attrib:
                return {tag: dict(element.attrib)}
            return {tag: None}

        # Element with children
        result = {}
        if element.attrib:
            result["@attributes"] = dict(element.attrib)

        for child in children:
            child_data = ONVIFSerializer._element_to_dict(child)
            child_tag = list(child_data.keys())[0]
            child_val = child_data[child_tag]

            if child_tag in result:
                # Multiple children with same tag -> list
                if not isinstance(result[child_tag], list):
                    result[child_tag] = [result[child_tag]]
                result[child_tag].append(child_val)
            else:
                result[child_tag] = child_val

        return {tag: result}

    @staticmethod
    def to_json_string(zeep_object, indent=2):
        """Return a formatted JSON string from a zeep object."""
        data = ONVIFSerializer.serialize(zeep_object)
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
