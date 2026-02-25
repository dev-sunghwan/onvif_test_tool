"""Check ONVIF profile support via GetServices / GetCapabilities fallback."""

import urllib3
import requests
from zeep.client import CachingClient, Settings
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEVICE_WSDL = "https://www.onvif.org/ver10/device/wsdl/devicemgmt.wsdl"
DEVICE_BINDING = "{http://www.onvif.org/ver10/device/wsdl}DeviceBinding"

# Profile key → required service namespace(s)
PROFILE_DEFINITIONS = {
    "S": {
        "name": "Profile S",
        "desc": "Video/audio streaming",
        "required": ["http://www.onvif.org/ver10/media/wsdl"],
        "color": "primary",
    },
    "T": {
        "name": "Profile T",
        "desc": "Advanced streaming (H.264/H.265, metadata)",
        "required": ["http://www.onvif.org/ver20/media/wsdl"],
        "color": "info",
    },
    "G": {
        "name": "Profile G",
        "desc": "Recording, storage, and retrieval",
        "required": [
            "http://www.onvif.org/ver10/recording/wsdl",
            "http://www.onvif.org/ver10/search/wsdl",
            "http://www.onvif.org/ver10/replay/wsdl",
        ],
        "color": "success",
    },
    "C": {
        "name": "Profile C",
        "desc": "Physical access control",
        "required": ["http://www.onvif.org/ver10/accesscontrol/wsdl"],
        "color": "warning",
    },
    "A": {
        "name": "Profile A",
        "desc": "Advanced access control with credentials",
        "required": [
            "http://www.onvif.org/ver10/accesscontrol/wsdl",
            "http://www.onvif.org/ver10/credential/wsdl",
        ],
        "color": "orange",
    },
    "D": {
        "name": "Profile D",
        "desc": "Video display output",
        "required": ["http://www.onvif.org/ver10/display/wsdl"],
        "color": "secondary",
    },
    "M": {
        "name": "Profile M",
        "desc": "Metadata and analytics streaming",
        "required": [
            "http://www.onvif.org/ver20/media/wsdl",
            "http://www.onvif.org/ver20/analytics/wsdl",
        ],
        "color": "danger",
    },
    "Q": {
        "name": "Profile Q",
        "desc": "Quick install and provisioning",
        "required": ["http://www.onvif.org/ver10/provisioning/wsdl"],
        "color": "dark",
    },
}


class ProfileChecker:
    """Detect ONVIF profile support using GetServices (with GetCapabilities fallback)."""

    def check(
        self,
        camera_ip: str,
        camera_port: int,
        username: str,
        password: str,
        use_https: bool = False,
    ) -> dict:
        """Check which ONVIF profiles the device supports.

        Returns:
            {
                "success": True/False,
                "services": [{"namespace": ..., "xaddr": ..., "version": ...}],
                "profiles": {"S": True, "T": False, ...},
                "profile_details": PROFILE_DEFINITIONS,
                "error": None or "message",
            }
        """
        scheme = "https" if use_https else "http"
        xaddr = f"{scheme}://{camera_ip}:{camera_port}/onvif/device_service"

        session = requests.Session()
        if use_https:
            session.verify = False
        transport = Transport(session=session)

        settings = Settings()
        settings.strict = False
        settings.xml_huge_tree = True

        try:
            client = CachingClient(
                wsdl=DEVICE_WSDL,
                wsse=UsernameToken(username, password, use_digest=True),
                settings=settings,
                transport=transport,
            )
            service = client.create_service(DEVICE_BINDING, xaddr)

            services = []
            try:
                response = service.GetServices(IncludeCapability=False)
                for svc in (response or []):
                    ns = getattr(svc, "Namespace", None)
                    xaddr_svc = getattr(svc, "XAddr", None)
                    ver = getattr(svc, "Version", None)
                    ver_str = None
                    if ver:
                        maj = getattr(ver, "Major", "")
                        minor = getattr(ver, "Minor", "")
                        ver_str = f"{maj}.{minor}"
                    if ns:
                        services.append({
                            "namespace": str(ns),
                            "xaddr": str(xaddr_svc) if xaddr_svc else "",
                            "version": ver_str,
                        })
            except Exception:
                # Fallback for older firmware that does not support GetServices
                services = self._check_via_capabilities(service)

            supported_ns = {s["namespace"] for s in services}
            profiles = {
                key: all(ns in supported_ns for ns in defn["required"])
                for key, defn in PROFILE_DEFINITIONS.items()
            }

            return {
                "success": True,
                "services": services,
                "profiles": profiles,
                "profile_details": PROFILE_DEFINITIONS,
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "services": [],
                "profiles": {},
                "profile_details": PROFILE_DEFINITIONS,
                "error": str(e),
            }

    def _check_via_capabilities(self, service) -> list:
        """Map GetCapabilities response to service namespace list (older firmware fallback)."""
        services = []
        try:
            caps = service.GetCapabilities(Category="All")
            cap_map = {
                "Media": "http://www.onvif.org/ver10/media/wsdl",
                "PTZ": "http://www.onvif.org/ver20/ptz/wsdl",
                "Imaging": "http://www.onvif.org/ver20/imaging/wsdl",
                "Events": "http://www.onvif.org/ver10/events/wsdl",
                "Analytics": "http://www.onvif.org/ver20/analytics/wsdl",
            }
            for cap_name, ns in cap_map.items():
                cap_obj = getattr(caps, cap_name, None)
                if cap_obj is not None:
                    xaddr_val = getattr(cap_obj, "XAddr", "")
                    services.append({
                        "namespace": ns,
                        "xaddr": str(xaddr_val) if xaddr_val else "",
                        "version": None,
                    })
            ext = getattr(caps, "Extension", None)
            if ext:
                ext_map = {
                    "Recording": "http://www.onvif.org/ver10/recording/wsdl",
                    "Search": "http://www.onvif.org/ver10/search/wsdl",
                    "Replay": "http://www.onvif.org/ver10/replay/wsdl",
                    "DeviceIO": "http://www.onvif.org/ver10/deviceIO/wsdl",
                }
                for cap_name, ns in ext_map.items():
                    cap_obj = getattr(ext, cap_name, None)
                    if cap_obj is not None:
                        xaddr_val = getattr(cap_obj, "XAddr", "")
                        services.append({
                            "namespace": ns,
                            "xaddr": str(xaddr_val) if xaddr_val else "",
                            "version": None,
                        })
        except Exception:
            pass
        return services
