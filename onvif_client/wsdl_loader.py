"""WSDL loading and service/binding/operation discovery using zeep."""

import operator
from zeep.client import CachingClient, Settings


class WSDLLoader:
    """Loads ONVIF WSDL files and discovers available bindings and operations."""

    def __init__(self):
        self._clients = {}  # wsdl_url -> CachingClient

    def _get_settings(self):
        settings = Settings()
        settings.strict = False
        settings.xml_huge_tree = True
        return settings

    def load_wsdl(self, wsdl_url: str) -> dict:
        """Load a WSDL and return its structure.

        Returns:
            {
                "bindings": {
                    "{namespace}BindingName": {
                        "qualified_name": "{namespace}BindingName",
                        "local_name": "BindingName",
                        "operations": ["Op1", "Op2", ...]
                    }
                }
            }
        """
        client = CachingClient(wsdl=wsdl_url, settings=self._get_settings())
        self._clients[wsdl_url] = client

        result = {"bindings": {}}

        # ONVIF WSDLs typically don't define <service> elements,
        # so iterate client.wsdl.bindings directly
        for binding_qname, binding in client.wsdl.bindings.items():
            qname = str(binding_qname)
            local_name = qname.split("}")[-1] if "}" in qname else qname

            ops = sorted(
                binding._operations.values(),
                key=operator.attrgetter("name"),
            )
            op_names = [op.name for op in ops]

            result["bindings"][qname] = {
                "qualified_name": qname,
                "local_name": local_name,
                "operations": op_names,
            }

        return result

    def get_client(self, wsdl_url: str):
        """Return cached CachingClient for the given WSDL URL."""
        if wsdl_url not in self._clients:
            client = CachingClient(wsdl=wsdl_url, settings=self._get_settings())
            self._clients[wsdl_url] = client
        return self._clients[wsdl_url]
