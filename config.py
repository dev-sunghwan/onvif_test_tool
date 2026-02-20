"""ONVIF Command Tester configuration."""

# Preset WSDL URLs for ONVIF services (with category for UI grouping)
ONVIF_PRESETS = {
    # ── Core ──────────────────────────────────────────────
    "Device Management": {
        "wsdl": "https://www.onvif.org/ver10/device/wsdl/devicemgmt.wsdl",
        "namespace": "http://www.onvif.org/ver10/device/wsdl",
        "binding": "DeviceBinding",
        "endpoint_path": "/onvif/device_service",
        "category": "Core",
    },
    "Media (ver10)": {
        "wsdl": "https://www.onvif.org/ver10/media/wsdl/media.wsdl",
        "namespace": "http://www.onvif.org/ver10/media/wsdl",
        "binding": "MediaBinding",
        "endpoint_path": "/onvif/media_service",
        "category": "Core",
    },
    "Media2 (ver20)": {
        "wsdl": "https://www.onvif.org/ver20/media/wsdl/media.wsdl",
        "namespace": "http://www.onvif.org/ver20/media/wsdl",
        "binding": "Media2Binding",
        "endpoint_path": "/onvif/media_service",
        "category": "Core",
    },
    # ── Streaming & Control ───────────────────────────────
    "PTZ": {
        "wsdl": "https://www.onvif.org/ver20/ptz/wsdl/ptz.wsdl",
        "namespace": "http://www.onvif.org/ver20/ptz/wsdl",
        "binding": "PTZBinding",
        "endpoint_path": "/onvif/ptz_service",
        "category": "Streaming & Control",
    },
    "Imaging": {
        "wsdl": "https://www.onvif.org/ver20/imaging/wsdl/imaging.wsdl",
        "namespace": "http://www.onvif.org/ver20/imaging/wsdl",
        "binding": "ImagingBinding",
        "endpoint_path": "/onvif/imaging_service",
        "category": "Streaming & Control",
    },
    # ── Events & Analytics ────────────────────────────────
    "Events": {
        "wsdl": "https://www.onvif.org/ver10/events/wsdl/event.wsdl",
        "namespace": "http://www.onvif.org/ver10/events/wsdl",
        "binding": "EventBinding",
        "endpoint_path": "/onvif/event_service",
        "category": "Events & Analytics",
    },
    "Analytics": {
        "wsdl": "https://www.onvif.org/ver20/analytics/wsdl/analytics.wsdl",
        "namespace": "http://www.onvif.org/ver20/analytics/wsdl",
        "binding": "AnalyticsEngineBinding",
        "endpoint_path": "/onvif/analytics_service",
        "category": "Events & Analytics",
    },
    # ── Hardware I/O ──────────────────────────────────────
    "Device I/O": {
        "wsdl": "https://www.onvif.org/ver10/deviceio.wsdl",
        "namespace": "http://www.onvif.org/ver10/deviceIO/wsdl",
        "binding": "DeviceIOBinding",
        "endpoint_path": "/onvif/deviceio_service",
        "category": "Hardware I/O",
    },
    # ── Recording & Playback ──────────────────────────────
    "Recording": {
        "wsdl": "https://www.onvif.org/ver10/recording.wsdl",
        "namespace": "http://www.onvif.org/ver10/recording/wsdl",
        "binding": "RecordingBinding",
        "endpoint_path": "/onvif/recording_service",
        "category": "Recording & Playback",
    },
    "Search": {
        "wsdl": "https://www.onvif.org/ver10/search.wsdl",
        "namespace": "http://www.onvif.org/ver10/search/wsdl",
        "binding": "SearchBinding",
        "endpoint_path": "/onvif/search_service",
        "category": "Recording & Playback",
    },
    "Replay": {
        "wsdl": "https://www.onvif.org/ver10/replay.wsdl",
        "namespace": "http://www.onvif.org/ver10/replay/wsdl",
        "binding": "ReplayBinding",
        "endpoint_path": "/onvif/replay_service",
        "category": "Recording & Playback",
    },
    # ── Specialized ───────────────────────────────────────
    "Provisioning": {
        "wsdl": "https://www.onvif.org/ver10/provisioning/wsdl/provisioning.wsdl",
        "namespace": "http://www.onvif.org/ver10/provisioning/wsdl",
        "binding": "ProvisioningBinding",
        "endpoint_path": "/onvif/provisioning_service",
        "category": "Specialized",
    },
    "Thermal": {
        "wsdl": "https://www.onvif.org/ver10/thermal/wsdl/thermal.wsdl",
        "namespace": "http://www.onvif.org/ver10/thermal/wsdl",
        "binding": "ThermalBinding",
        "endpoint_path": "/onvif/thermal_service",
        "category": "Specialized",
    },
    # ── Access Control (PACS) ─────────────────────────────
    "Access Control": {
        "wsdl": "https://www.onvif.org/ver10/pacs/accesscontrol.wsdl",
        "namespace": "http://www.onvif.org/ver10/accesscontrol/wsdl",
        "binding": "PACSBinding",
        "endpoint_path": "/onvif/accesscontrol_service",
        "category": "Access Control",
    },
    "Door Control": {
        "wsdl": "https://www.onvif.org/ver10/pacs/doorcontrol.wsdl",
        "namespace": "http://www.onvif.org/ver10/doorcontrol/wsdl",
        "binding": "DoorControlBinding",
        "endpoint_path": "/onvif/doorcontrol_service",
        "category": "Access Control",
    },
    "Credential": {
        "wsdl": "https://www.onvif.org/ver10/credential/wsdl/credential.wsdl",
        "namespace": "http://www.onvif.org/ver10/credential/wsdl",
        "binding": "CredentialBinding",
        "endpoint_path": "/onvif/credential_service",
        "category": "Access Control",
    },
}

# Mapping from binding local name to camera endpoint path
ENDPOINT_MAP = {
    # Core
    "DeviceBinding": "/onvif/device_service",
    "MediaBinding": "/onvif/media_service",
    "Media2Binding": "/onvif/media_service",
    # Streaming & Control
    "PTZBinding": "/onvif/ptz_service",
    "ImagingBinding": "/onvif/imaging_service",
    # Events (multiple bindings in one WSDL)
    "EventBinding": "/onvif/event_service",
    "NotificationProducerBinding": "/onvif/event_service",
    "PullPointSubscriptionBinding": "/onvif/event_service",
    "SubscriptionManagerBinding": "/onvif/event_service",
    "NotificationConsumerBinding": "/onvif/event_service",
    "PullPointBinding": "/onvif/event_service",
    "CreatePullPointBinding": "/onvif/event_service",
    "PausableSubscriptionManagerBinding": "/onvif/event_service",
    # Analytics (multiple bindings in one WSDL)
    "AnalyticsEngineBinding": "/onvif/analytics_service",
    "RuleEngineBinding": "/onvif/analytics_service",
    # Hardware I/O
    "DeviceIOBinding": "/onvif/deviceio_service",
    # Recording & Playback
    "RecordingBinding": "/onvif/recording_service",
    "SearchBinding": "/onvif/search_service",
    "ReplayBinding": "/onvif/replay_service",
    # Specialized
    "ProvisioningBinding": "/onvif/provisioning_service",
    "ThermalBinding": "/onvif/thermal_service",
    # Access Control (PACS)
    "PACSBinding": "/onvif/accesscontrol_service",
    "DoorControlBinding": "/onvif/doorcontrol_service",
    "CredentialBinding": "/onvif/credential_service",
}

# Flask settings
DEFAULT_PORT = 5000
ZEEP_TIMEOUT = 15
ZEEP_OPERATION_TIMEOUT = 30
