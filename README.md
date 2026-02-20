# ONVIF Command Tester

ONVIF SOAP 커맨드를 GUI로 테스트할 수 있는 Flask 기반 웹 애플리케이션.

카메라 IP/Credential을 입력하고, WSDL URL을 로드하면 사용 가능한 오퍼레이션 목록이 자동으로 표시됩니다.
오퍼레이션을 선택하면 파라미터 입력 폼이 동적으로 생성되고, 실행 결과를 JSON 및 SOAP XML로 확인할 수 있습니다.

## Quick Start

### 방법 1: run.bat (권장)
```
run.bat 더블클릭
```
가상환경 생성, 의존성 설치, 서버 시작, 브라우저 오픈이 자동으로 실행됩니다.

### 방법 2: 수동 실행
```bash
cd C:\Users\SungHwan\Desktop\ONVIF_test_tool
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
브라우저에서 `http://127.0.0.1:5000` 접속

## 사용법

### 1. Camera Connection
| 필드 | 설명 | 예시 |
|------|------|------|
| IP Address | 카메라 IP | `192.168.1.100` |
| Port | ONVIF 포트 (보통 80) | `80` |
| Username | 카메라 관리자 계정 | `admin` |
| Password | 비밀번호 | `****` |

**Test Connection** 버튼: Device Management의 `GetDeviceInformation`을 호출하여 연결 확인 (제조사, 모델, 펌웨어 버전 표시)

### 2. WSDL Service
- **프리셋 드롭다운**: Device Management / Media (ver10) / Media2 (ver20) 선택
- **자유 입력**: 임의의 ONVIF WSDL URL 직접 입력 가능
- **Load 버튼**: WSDL을 파싱하여 바인딩/오퍼레이션 목록 자동 로드

> 첫 로드 시 WSDL을 원격에서 다운로드하므로 5~15초 소요될 수 있습니다. 이후 캐시되어 즉시 로드됩니다.

### 3. Operation
- **Binding**: WSDL에 정의된 바인딩 선택 (보통 1개)
- **Operation**: 사용 가능한 ONVIF 오퍼레이션 드롭다운
- **Parameters**: 선택한 오퍼레이션의 파라미터가 자동으로 폼 생성
  - 필수 파라미터: `*` 표시
  - Complex Type: 접이식 fieldset (클릭하여 확장)
  - Enum Type: 드롭다운 선택
  - Boolean: true/false 선택
- **Execute**: 카메라에 ONVIF 커맨드 전송

### 4. Result Panel
| 탭 | 내용 |
|----|------|
| **JSON Result** | 파싱된 응답 데이터 (syntax highlighted) |
| **Request XML** | 카메라에 전송된 SOAP 요청 XML |
| **Response XML** | 카메라에서 수신된 SOAP 응답 XML |

- 실행 시간(ms) 및 성공/실패 상태 표시
- Copy 버튼으로 클립보드 복사

## 지원 ONVIF 서비스 (1차)

| 서비스 | WSDL URL | 주요 오퍼레이션 |
|--------|----------|----------------|
| **Device Management** | `ver10/device/wsdl/devicemgmt.wsdl` | GetDeviceInformation, GetCapabilities, GetServices, GetNetworkInterfaces, GetUsers, SystemReboot... (103개) |
| **Media (ver10)** | `ver10/media/wsdl/media.wsdl` | GetProfiles, GetProfile, GetStreamUri, GetVideoSources, GetVideoEncoderConfigurations... |
| **Media2 (ver20)** | `ver20/media/wsdl/media.wsdl` | GetProfiles, GetVideoEncoderConfigurations, GetStreamUri... |

자유 입력 모드로 PTZ, Imaging, Events 등 모든 ONVIF WSDL URL을 직접 입력하여 사용할 수도 있습니다.

## 프로젝트 구조

```
ONVIF_test_tool/
├── app.py                      # Flask 앱 진입점 + API 라우트
├── config.py                   # ONVIF 프리셋 WSDL URL, 엔드포인트 맵핑
├── requirements.txt            # Python 의존성 (flask, zeep, lxml, requests)
├── run.bat                     # Windows 실행 스크립트
├── onvif_client/
│   ├── __init__.py
│   ├── wsdl_loader.py          # WSDL 로드, 바인딩/오퍼레이션 탐색
│   ├── type_introspector.py    # XSD 타입 재귀 분석 → 파라미터 스키마
│   ├── command_executor.py     # ONVIF 커맨드 실행 + SOAP XML 캡처
│   └── serializer.py           # zeep 객체 → JSON 변환
├── templates/
│   └── index.html              # Bootstrap 5 SPA 메인 페이지
└── static/
    ├── css/style.css           # Hanwha Vision 브랜딩 테마
    └── js/
        ├── app.js              # UI 로직, API 호출, 결과 표시
        └── param-builder.js    # 동적 파라미터 폼 생성기
```

## API 엔드포인트

| Route | Method | 설명 |
|-------|--------|------|
| `/` | GET | 메인 페이지 |
| `/api/presets` | GET | ONVIF 프리셋 목록 |
| `/api/load-wsdl` | POST | WSDL 로드 → 바인딩/오퍼레이션 반환 |
| `/api/operation-params` | POST | 오퍼레이션 파라미터 스키마 반환 |
| `/api/execute` | POST | ONVIF 커맨드 실행 → JSON + XML 결과 |

## 기술 스택

- **Backend**: Python 3, Flask 3.x, zeep 4.x (SOAP client), lxml
- **Frontend**: Bootstrap 5.3, Bootstrap Icons, Vanilla JavaScript
- **인증**: WS-Security UsernameToken (Digest)
- **WSDL 캐시**: zeep CachingClient (SQLite)

## 향후 확장 예정

- PTZ, Imaging, Events, Analytics, Device IO 프리셋 추가
- GetServices() 기반 카메라 서비스 자동 탐색
- 커맨드 실행 히스토리 저장/재실행
- Raw SOAP XML 직접 전송 모드
