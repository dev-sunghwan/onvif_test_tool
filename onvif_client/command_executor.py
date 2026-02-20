"""Execute ONVIF operations on cameras with XML capture."""

import time

from lxml import etree
from zeep.client import CachingClient, Settings
from zeep.plugins import HistoryPlugin
from zeep.wsse.username import UsernameToken

from config import ENDPOINT_MAP
from .serializer import ONVIFSerializer


class CommandExecutor:
    """Creates authenticated service proxies and executes ONVIF operations."""

    def execute(
        self,
        wsdl_url: str,
        binding_name: str,
        operation_name: str,
        camera_ip: str,
        camera_port: int,
        username: str,
        password: str,
        params: dict,
    ) -> dict:
        """Execute an ONVIF operation and return result + raw XML.

        Returns:
            {
                "success": True/False,
                "result_json": { ... },
                "request_xml": "<soap:...>",
                "response_xml": "<soap:...>",
                "error": None or "error message",
                "execution_time_ms": 245,
            }
        """
        history = HistoryPlugin(maxlen=1)

        settings = Settings()
        settings.strict = False
        settings.xml_huge_tree = True

        xaddr = self._resolve_xaddr(binding_name, camera_ip, camera_port)

        try:
            client = CachingClient(
                wsdl=wsdl_url,
                wsse=UsernameToken(username, password, use_digest=True),
                settings=settings,
                plugins=[history],
            )

            service = client.create_service(binding_name, xaddr)
            operation_func = getattr(service, operation_name)

            start_time = time.time()
            if params:
                result = operation_func(**params)
            else:
                result = operation_func()
            elapsed = (time.time() - start_time) * 1000

            result_json = ONVIFSerializer.serialize(result)

            request_xml = self._extract_xml(history, "sent")
            response_xml = self._extract_xml(history, "received")

            return {
                "success": True,
                "result_json": result_json,
                "request_xml": request_xml,
                "response_xml": response_xml,
                "error": None,
                "execution_time_ms": round(elapsed, 1),
            }
        except Exception as e:
            request_xml = self._extract_xml(history, "sent")
            response_xml = self._extract_xml(history, "received")
            return {
                "success": False,
                "result_json": None,
                "request_xml": request_xml,
                "response_xml": response_xml,
                "error": str(e),
                "execution_time_ms": 0,
            }

    def _resolve_xaddr(self, binding_name: str, ip: str, port: int) -> str:
        """Map binding name to the correct ONVIF service endpoint path."""
        local_name = binding_name.split("}")[-1] if "}" in binding_name else binding_name
        path = ENDPOINT_MAP.get(local_name, "/onvif/device_service")
        return f"http://{ip}:{port}{path}"

    def _extract_xml(self, history: HistoryPlugin, direction: str) -> str:
        """Extract and pretty-print XML from history plugin."""
        try:
            if direction == "sent" and history.last_sent:
                envelope = history.last_sent["envelope"]
            elif direction == "received" and history.last_received:
                envelope = history.last_received["envelope"]
            else:
                return ""
            return etree.tostring(envelope, pretty_print=True, encoding="unicode")
        except Exception:
            return ""
