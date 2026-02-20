# ONVIF Command Tester - Development Changelog

## v1.0.0 - Initial Release (2026-02-20)

### Phase 1: Project Setup
- 프로젝트 디렉토리 구조 생성 (`ONVIF_test_tool/`)
- `requirements.txt` 작성: flask, zeep, lxml, requests
- `config.py` 작성: ONVIF 프리셋 3종 (Device Management, Media ver10, Media2 ver20) 및 엔드포인트 맵핑
- `run.bat` 작성: venv 자동 생성/활성화 + 의존성 설치 + Flask 서버 시작 + 브라우저 자동 오픈
- Python 가상환경(`.venv`) 생성 및 의존성 설치 완료

### Phase 2: Backend - ONVIF Client Module (`onvif_client/`)

**`wsdl_loader.py`**
- `WSDLLoader` 클래스 구현
- zeep `CachingClient`를 사용한 WSDL 파싱 및 캐싱
- WSDL 내 바인딩/오퍼레이션 목록 자동 탐색

**`type_introspector.py`**
- `introspect_operation()` 함수 구현
- XSD 타입을 재귀적으로 분석하여 파라미터 스키마 생성 (depth 5 제한)
- ComplexType → 중첩 children, SimpleType → 타입명 매핑
- Enumeration 타입 감지 (`accepted_values`) 지원

**`command_executor.py`**
- `CommandExecutor` 클래스 구현
- WS-Security `UsernameToken` (Digest 인증) 적용
- zeep `HistoryPlugin`으로 Request/Response SOAP XML 캡처
- 바인딩 이름 → 카메라 엔드포인트 경로 자동 매핑 (`_resolve_xaddr`)

**`serializer.py`**
- `ONVIFSerializer` 클래스 구현
- `zeep.helpers.serialize_object` 래핑
- datetime, timedelta, Decimal, bytes 등 비-JSON 타입 처리

### Phase 3: Backend - Flask App (`app.py`)
- 4개 API 라우트 구현:
  - `GET /` - 메인 페이지 렌더링
  - `POST /api/load-wsdl` - WSDL 로드 → 바인딩/오퍼레이션 반환
  - `POST /api/operation-params` - 오퍼레이션 파라미터 스키마 반환
  - `POST /api/execute` - ONVIF 커맨드 실행 → JSON + XML 결과 반환
  - `GET /api/presets` - 프리셋 목록 반환

### Phase 4: Frontend

**`templates/index.html`**
- Bootstrap 5.3 + Bootstrap Icons CDN 기반 SPA
- 2컬럼 레이아웃: 좌측(입력 패널) + 우측(결과 패널)
- Camera Connection 카드: IP, Port, Username, Password 입력 + 비밀번호 토글
- WSDL Service 카드: 프리셋 드롭다운 + 자유 URL 입력 + Load 버튼
- Operation 카드: Binding/Operation 드롭다운 + 동적 파라미터 폼 영역 + Execute 버튼
- Result 패널: JSON / Request XML / Response XML 탭 + 상태 바 + Copy 버튼
- 로딩 오버레이 + Toast 알림 시스템

**`static/css/style.css`**
- Hanwha Vision 브랜딩 테마 (`#FF6600` 오렌지)
- 다크 배경 네비게이션 바 + 오렌지 액센트 바
- VS Code 스타일 결과 표시 영역 (다크 배경, Consolas 폰트)
- JSON/XML 구문 강조 색상 정의
- 반응형 디자인 (991px 이하 세로 스택)

**`static/js/param-builder.js`**
- `ParamBuilder` 객체 구현
- 파라미터 스키마 → HTML 폼 동적 생성
  - string → text input
  - integer → number input (step=1)
  - float → number input (step=any)
  - boolean → select (true/false)
  - enum → select (값 목록)
  - ComplexType → 접이식 fieldset (기본 접힌 상태)
- `collectParams()`: dot-notation 폼 입력값 → 중첩 dict 변환
- `_castValue()`: 타입별 값 캐스팅 (string→string, integer→int, boolean→bool)

**`static/js/app.js`**
- WSDL 로드 → 바인딩/오퍼레이션 드롭다운 자동 채움
- 바인딩 변경 → 오퍼레이션 목록 갱신
- 오퍼레이션 변경 → 파라미터 폼 자동 생성
- Execute → 카메라 커맨드 실행 → 결과 표시
- Test Connection → DeviceBinding.GetDeviceInformation 호출
- JSON/XML 구문 강조 (`highlightJson`, `highlightXml`)
- sessionStorage 기반 접속정보 유지
- Toast 알림 (성공/에러)
- Copy to Clipboard 기능

---

## Bugfix #1 - WSDL 바인딩 탐색 실패 (2026-02-20)

### 증상
WSDL URL을 Load한 후 바인딩/오퍼레이션 드롭다운이 빈 상태로 표시됨.
API 응답: `{ "bindings": {}, "success": true }`

### 원인
ONVIF WSDL 파일은 `<wsdl:service>` 요소를 정의하지 않음.
zeep에서 `client.wsdl.services`가 빈 딕셔너리를 반환하여 바인딩 순회 루프가 실행되지 않음.

```python
# 기존 코드 (동작하지 않음)
for service in client.wsdl.services.values():      # services = {} → 루프 미실행
    for port in service.ports.values():
        binding = port.binding
```

### 수정

**`onvif_client/wsdl_loader.py`** - `load_wsdl()` 메서드
```python
# 수정 후: client.wsdl.bindings 직접 순회
for binding_qname, binding in client.wsdl.bindings.items():
    qname = str(binding_qname)
    local_name = qname.split("}")[-1] if "}" in qname else qname
    ops = sorted(binding._operations.values(), key=operator.attrgetter("name"))
    ...
```

**`onvif_client/type_introspector.py`** - `introspect_operation()` 함수
```python
# 수정 후: client.wsdl.bindings에서 직접 조회
binding = client.wsdl.bindings.get(binding_name)
if binding:
    operation = binding._operations.get(operation_name)
    ...
```

### 검증
- `curl -X POST /api/load-wsdl` → Device WSDL: 1 binding, 103 operations 정상 반환
- `curl -X POST /api/load-wsdl` → Media WSDL: MediaBinding 정상 반환
- `curl -X POST /api/operation-params` → GetProfile 파라미터 `ProfileToken (string, required)` 정상 반환

### 학습 포인트
zeep에서 WSDL 구조를 탐색할 때, `client.wsdl.services`는 WSDL에 `<service>` 요소가 명시적으로 정의되어 있어야 데이터가 존재함. ONVIF처럼 추상 WSDL(바인딩만 정의)을 사용하는 경우 `client.wsdl.bindings`를 직접 사용해야 함.

---

## Bugfix #2 - JSON 직렬화 실패로 HTML 에러 페이지 반환 (2026-02-20)

### 증상
Media Binding에서 `CreateProfile`로 토큰을 받은 후, `GetCompatibleVideoSourceConfigurations`를 호출하면:
```
Error: Unexpected token '<', "<!doctype "... is not valid JSON
```

### 원인
zeep이 반환하는 ONVIF 응답 객체에 `timedelta`, `Decimal`, `bytes`, `set` 등 Python 표준 JSON 인코더가 처리할 수 없는 타입이 포함됨. Flask의 `jsonify()`가 이를 직렬화하지 못하고 500 에러를 발생시키면서, Flask 기본 HTML 에러 페이지를 반환. 프론트엔드 JS의 `response.json()`이 HTML을 파싱하려다 실패.

**재현 경로:**
1. `executor.execute()` → zeep 호출 → 응답에 `timedelta` 포함
2. `ONVIFSerializer.serialize()` → `_make_json_safe()` → 일부 타입 누락
3. `jsonify(result)` → `json.dumps()` 내부에서 `TypeError: Object of type timedelta is not JSON serializable`
4. Flask → 500 HTML 에러 페이지 반환
5. JS `response.json()` → `"<!doctype"` 파싱 실패

### 수정

**`app.py`** - 커스텀 JSON Provider 추가
```python
class ONVIFJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles zeep-specific types."""
    @staticmethod
    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, timedelta):
            total = int(o.total_seconds())
            h, rem = divmod(total, 3600)
            m, s = divmod(rem, 60)
            return f"PT{h}H{m}M{s}S" if h else f"PT{m}M{s}S" if m else f"PT{s}S"
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, bytes):
            return o.decode("utf-8", errors="replace")
        if isinstance(o, set):
            return list(o)
        return str(o)  # 최후의 fallback

app.json_provider_class = ONVIFJSONProvider
app.json = ONVIFJSONProvider(app)
```

**`app.py`** - `/api/execute` 라우트에 try/except 추가
```python
try:
    result = executor.execute(...)
    return jsonify(result)
except Exception as e:
    return jsonify({
        "success": False, "error": f"Server error: {type(e).__name__}: {e}", ...
    }), 500
```

**`static/js/app.js`** - 응답 Content-Type 검증 추가
```javascript
async function apiCall(url, data) {
    const resp = await fetch(url, { ... });
    const contentType = resp.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
        throw new Error(`Server returned non-JSON response (HTTP ${resp.status}).`);
    }
    return resp.json();
}
```

### 검증
- `timedelta(seconds=30)` → `"PT30S"` 정상 변환
- `Decimal('3.14')` → `3.14` 정상 변환
- `bytes(b'hello')` → `"hello"` 정상 변환
- `set({1, 2, 3})` → `[1, 2, 3]` 정상 변환
- 네트워크 에러 시에도 HTML 대신 JSON 에러 응답 반환 확인

### 학습 포인트
Flask의 `jsonify()`는 내부적으로 `json.dumps()`를 사용하며, Python 기본 JSON 인코더는 `dict`, `list`, `str`, `int`, `float`, `bool`, `None`만 지원. zeep 응답에는 `timedelta`, `Decimal`, `OrderedDict` 등이 포함될 수 있으므로, SOAP 클라이언트를 Flask와 함께 사용할 때는 반드시 커스텀 JSON Provider를 등록해야 함. 또한 `jsonify()` 실패 시 HTML을 반환하는 것을 방지하기 위해 모든 API 라우트에 try/except + JSON 에러 응답 패턴을 적용해야 함.

---

## Bugfix #3 - lxml Element 객체가 문자열로 표시되는 문제 (2026-02-20)

### 증상
`GetCompatibleVideoSourceConfigurations` 등의 응답에서 `_value_1` 필드가 lxml 객체의 메모리 주소로 표시됨:
```json
"_value_1": [
  "<Element {http://www.onvif.org/ver10/schema}Extension at 0x1f37a872f40>"
]
```

### 원인
`zeep.helpers.serialize_object()`가 ONVIF Extension 등 일부 XSD `any` 타입 요소를 lxml `_Element` 객체 그대로 반환함. `ONVIFSerializer._make_json_safe()`에 lxml Element 처리 로직이 없어 Python의 기본 `str()` 변환이 적용됨.

### 수정

**`onvif_client/serializer.py`** - lxml Element → dict 변환 메서드 추가
```python
from lxml import etree

# _make_json_safe()에 lxml 체크 추가
elif isinstance(obj, etree._Element):
    return ONVIFSerializer._element_to_dict(obj)

# 새 메서드: Element를 재귀적으로 dict로 변환
@staticmethod
def _element_to_dict(element):
    tag = etree.QName(element.tag).localname  # namespace 제거
    children = list(element)
    if not children and element.text:
        return {tag: element.text.strip()}
    # ... children 재귀 처리
```

**`app.py`** - `ONVIFJSONProvider.default()`에도 lxml fallback 추가
```python
if isinstance(o, etree._Element):
    return ONVIFSerializer._element_to_dict(o)
```

### 검증
수정 전:
```json
"_value_1": ["<Element {http://...}Extension at 0x1f37a872f40>"]
```

수정 후:
```json
"_value_1": [
  {
    "Extension": {
      "Rotate": {
        "Mode": "OFF",
        "Degree": "0"
      }
    }
  }
]
```

### 학습 포인트
zeep의 `serialize_object()`는 XSD `any` 타입이나 Extension 요소를 lxml Element 그대로 남긴다. ONVIF 응답에는 이런 Extension이 빈번하므로, serializer에서 `etree._Element` 타입을 반드시 처리해야 한다.

---

## Enhancement #1 - 전체 ONVIF 서비스 바인딩 프리셋 추가 (2026-02-20)

### 변경 내용
기존 3개 프리셋(Device Management, Media ver10, Media2 ver20)에서 **16개 프리셋**으로 확장.

### 추가된 서비스

| 카테고리 | 서비스 | 바인딩 | 주요 용도 |
|----------|--------|--------|-----------|
| **Core** | Device Management | DeviceBinding | 장치 정보, 설정, 네트워크 |
| | Media (ver10) | MediaBinding | 프로필, 스트림 URI |
| | Media2 (ver20) | Media2Binding | 향상된 미디어 관리 |
| **Streaming & Control** | PTZ | PTZBinding | Pan/Tilt/Zoom 제어, 프리셋 |
| | Imaging | ImagingBinding | 밝기, 대비, WB 등 이미지 설정 |
| **Events & Analytics** | Events | EventBinding | 이벤트 구독, 알림 |
| | Analytics | AnalyticsEngineBinding | 비디오 분석, 모션 감지 규칙 |
| **Hardware I/O** | Device I/O | DeviceIOBinding | 디지털 입출력, 릴레이 |
| **Recording & Playback** | Recording | RecordingBinding | 녹화 제어, 트랙 관리 |
| | Search | SearchBinding | 녹화 영상/메타데이터 검색 |
| | Replay | ReplayBinding | 녹화 영상 재생, ReplayUri |
| **Specialized** | Provisioning | ProvisioningBinding | 장치 프로비저닝 |
| | Thermal | ThermalBinding | 열화상 카메라 설정 |
| **Access Control** | Access Control | PACSBinding | 출입 통제 |
| | Door Control | DoorControlBinding | 도어 상태/제어 |
| | Credential | CredentialBinding | 출입 자격 증명 관리 |

### 수정 파일

**`config.py`**
- `ONVIF_PRESETS`: 3개 → 16개 서비스 확장, 각 프리셋에 `category` 필드 추가
- `ENDPOINT_MAP`: 8개 → 25개 바인딩-엔드포인트 매핑 추가 (Events WSDL의 7개 바인딩, Analytics의 RuleEngineBinding 포함)

**`templates/index.html`**
- 프리셋 드롭다운에 `<optgroup>` 적용: 카테고리별 그룹핑 (Core, Streaming & Control, Events & Analytics, Hardware I/O, Recording & Playback, Specialized, Access Control)

### 수정하지 않은 파일
- `app.py`, `command_executor.py`, `serializer.py`, `wsdl_loader.py`, `type_introspector.py`, `app.js`, `param-builder.js` — 기존 아키텍처가 동적으로 동작하므로 변경 불필요
