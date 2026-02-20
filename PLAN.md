# ONVIF Command Tester - Flask Web App 구현 계획

## Context
현재 Jupyter 노트북에서 `zeep` 라이브러리로 ONVIF SOAP 커맨드를 수동 테스트하고 있음. WSDL URL, 바인딩, 오퍼레이션을 코드로 직접 입력해야 하는 불편함을 해소하기 위해, 브라우저 기반 GUI 툴을 만듦.

## 프로젝트 위치
`C:\Users\SungHwan\Desktop\ONVIF_test_tool\`

## 1차 구현 범위
- **Device Management**, **Media (ver10)**, **Media2 (ver20)** 프리셋
- WSDL 자유 입력도 지원

## 프로젝트 구조

```
ONVIF_test_tool/
├── app.py                      # Flask 앱 진입점 + API 라우트
├── config.py                   # ONVIF 프리셋 WSDL URL, 설정값
├── requirements.txt            # flask, zeep, lxml, requests
├── run.bat                     # Windows 실행 스크립트 (venv 자동생성)
├── PLAN.md                     # 이 계획 문서
├── onvif_client/
│   ├── __init__.py
│   ├── wsdl_loader.py          # WSDL 로드, 바인딩/오퍼레이션 탐색
│   ├── type_introspector.py    # XSD 타입 재귀 분석 → 파라미터 스키마 생성
│   ├── command_executor.py     # 인증된 ONVIF 커맨드 실행 + XML 캡처
│   └── serializer.py           # zeep 객체 → JSON 변환
├── templates/
│   └── index.html              # 메인 페이지 (Bootstrap 5 SPA)
└── static/
    ├── css/
    │   └── style.css           # Hanwha 브랜딩 테마
    └── js/
        ├── app.js              # 메인 JS (AJAX, UI 로직)
        └── param-builder.js    # 동적 파라미터 폼 생성기
```

## 핵심 UX 플로우

1. 카메라 접속정보 입력 (IP, Port, Username, Password)
2. WSDL URL 입력 (프리셋 드롭다운 또는 자유입력) → [Load WSDL]
3. 바인딩 선택 → 오퍼레이션 드롭다운 자동 채움
4. 오퍼레이션 선택 → 파라미터 폼 자동 생성
5. 파라미터 입력 → [Execute]
6. 결과 표시: [JSON 탭] [Request XML 탭] [Response XML 탭] + 실행시간

## 1차 프리셋

| 서비스 | WSDL URL | 바인딩 |
|--------|----------|--------|
| Device Management | `https://www.onvif.org/ver10/device/wsdl/devicemgmt.wsdl` | DeviceBinding |
| Media (ver10) | `https://www.onvif.org/ver10/media/wsdl/media.wsdl` | MediaBinding |
| Media2 (ver20) | `https://www.onvif.org/ver20/media/wsdl/media.wsdl` | Media2Binding |

## 구현 순서

1. 프로젝트 셋업: 디렉토리, requirements.txt, config.py, run.bat
2. Flask + 메인 템플릿: app.py, index.html (Bootstrap 레이아웃)
3. WSDL 로드: wsdl_loader.py + /api/load-wsdl + JS 드롭다운
4. 파라미터 분석: type_introspector.py + /api/operation-params + param-builder.js
5. 커맨드 실행: command_executor.py + serializer.py + /api/execute + 결과 UI
6. 마무리: 에러 처리, 로딩 스피너, Test Connection, sessionStorage

## 2차 확장 예정
- PTZ, Imaging, Events, Analytics, Device IO 프리셋 추가
- GetServices() 기반 xaddr 자동 탐색
- 커맨드 히스토리 저장
- Raw XML 직접 전송 모드
