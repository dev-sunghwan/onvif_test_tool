# ONVIF Command Tester

A Flask-based web application for testing ONVIF SOAP commands via a browser GUI.

Enter camera IP/credentials, load a WSDL URL, and the available operations are automatically listed. Select an operation to get a dynamically generated parameter form, then execute and view results as JSON and SOAP XML.

> [Korean documentation (README_ko.md)](README_ko.md)

## Quick Start

### Option 1: run.bat (Recommended, Windows)
```
Double-click run.bat
```
Automatically creates a virtual environment, installs dependencies, starts the Flask server, and opens the browser.

### Option 2: Manual Setup
```bash
git clone https://github.com/dev-sunghwan/onvif_test_tool.git
cd onvif_test_tool
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

## Usage

### 1. Camera Connection
| Field | Description | Example |
|-------|-------------|---------|
| IP Address | Camera IP address | `192.168.1.100` |
| Port | ONVIF port (usually 80) | `80` |
| Username | Camera admin account | `admin` |
| Password | Password | `****` |

**Test Connection** button: Calls `GetDeviceInformation` via Device Management to verify connectivity (displays manufacturer, model, firmware version).

### 2. WSDL Service
- **Preset dropdown**: Quick access to 16 ONVIF services grouped by category
- **Custom URL**: Enter any ONVIF WSDL URL directly
- **Load button**: Parses the WSDL and auto-populates binding/operation dropdowns

> The first load may take 5-15 seconds as the WSDL is downloaded remotely. Subsequent loads are cached instantly.

### 3. Operation
- **Binding**: Select the WSDL-defined binding (usually 1 per service)
- **Operation**: Dropdown of available ONVIF operations
- **Parameters**: Auto-generated input form based on the operation's XSD schema
  - Required parameters marked with `*`
  - Complex types: Collapsible fieldsets (click to expand)
  - Enum types: Dropdown selectors
  - Boolean: true/false selector
- **Execute**: Sends the ONVIF command to the camera

### 4. Result Panel
| Tab | Content |
|-----|---------|
| **JSON Result** | Parsed response data (syntax highlighted) |
| **Request XML** | SOAP request XML sent to the camera |
| **Response XML** | SOAP response XML received from the camera |

- Execution time (ms) and success/failure status display
- Copy to clipboard button

## Supported ONVIF Services

| Category | Service | Binding | Key Operations |
|----------|---------|---------|----------------|
| **Core** | Device Management | DeviceBinding | GetDeviceInformation, GetCapabilities, GetServices, SystemReboot... |
| | Media (ver10) | MediaBinding | GetProfiles, GetStreamUri, GetVideoSources... |
| | Media2 (ver20) | Media2Binding | GetProfiles, GetVideoEncoderConfigurations... |
| **Streaming & Control** | PTZ | PTZBinding | ContinuousMove, AbsoluteMove, GetPresets, GotoPreset... |
| | Imaging | ImagingBinding | GetImagingSettings, SetImagingSettings, GetOptions... |
| **Events & Analytics** | Events | EventBinding | Subscribe, PullMessages, GetEventProperties... |
| | Analytics | AnalyticsEngineBinding | GetSupportedRules, GetRules, CreateRules... |
| **Hardware I/O** | Device I/O | DeviceIOBinding | GetDigitalInputs, GetRelayOutputs, SetRelayOutputState... |
| **Recording & Playback** | Recording | RecordingBinding | CreateRecording, GetRecordings, CreateRecordingJob... |
| | Search | SearchBinding | FindRecordings, GetRecordingSearchResults... |
| | Replay | ReplayBinding | GetReplayUri, GetReplayConfiguration... |
| **Specialized** | Provisioning | ProvisioningBinding | PanMove, TiltMove, ZoomMove, FocusMove... |
| | Thermal | ThermalBinding | GetConfiguration, SetConfiguration... |
| **Access Control** | Access Control | PACSBinding | GetAccessPointInfo, EnableAccessPoint... |
| | Door Control | DoorControlBinding | GetDoorInfo, AccessDoor, LockDoor... |
| | Credential | CredentialBinding | GetCredentialInfo, CreateCredential... |

You can also enter any custom WSDL URL for services not listed above.

## Project Structure

```
onvif_test_tool/
├── app.py                      # Flask app entry point + API routes
├── config.py                   # ONVIF preset WSDL URLs, endpoint mapping
├── requirements.txt            # Python dependencies (flask, zeep, lxml, requests)
├── run.bat                     # Windows launch script
├── onvif_client/
│   ├── __init__.py
│   ├── wsdl_loader.py          # WSDL loading, binding/operation discovery
│   ├── type_introspector.py    # Recursive XSD type analysis → parameter schema
│   ├── command_executor.py     # ONVIF command execution + SOAP XML capture
│   └── serializer.py           # zeep object → JSON conversion
├── templates/
│   └── index.html              # Bootstrap 5 SPA main page
└── static/
    ├── css/style.css           # Hanwha Vision branding theme
    └── js/
        ├── app.js              # UI logic, API calls, result display
        └── param-builder.js    # Dynamic parameter form generator
```

## API Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Main page |
| `/api/presets` | GET | ONVIF preset list |
| `/api/load-wsdl` | POST | Load WSDL → return bindings/operations |
| `/api/operation-params` | POST | Return operation parameter schema |
| `/api/execute` | POST | Execute ONVIF command → JSON + XML result |

## Tech Stack

- **Backend**: Python 3, Flask 3.x, zeep 4.x (SOAP client), lxml
- **Frontend**: Bootstrap 5.3, Bootstrap Icons, Vanilla JavaScript
- **Authentication**: WS-Security UsernameToken (Digest)
- **WSDL Cache**: zeep CachingClient (SQLite)

## Roadmap

- GetServices()-based automatic camera service discovery
- Command execution history with save/replay
- Raw SOAP XML direct send mode
