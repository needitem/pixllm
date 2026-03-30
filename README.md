# PIXLLM

로컬 코드베이스를 대상으로 질문하고, 근거가 되는 파일과 코드 흐름을 함께 확인할 수 있는 데스크톱 + 백엔드 조합입니다.

이 저장소는 두 부분으로 구성됩니다.

- [`desktop/`](./desktop): Electron 기반 데스크톱 앱
- [`backend/`](./backend): FastAPI 기반 API 서버와 검색/추론 런타임

## 이 프로젝트로 할 수 있는 것

- 로컬 워크스페이스를 열고 코드에 대해 질문하기
- 질문에 맞는 파일, 심볼, 호출 흐름을 추적해서 설명 받기
- 채팅, 프롬프트, 대화 이력, 실행 run, import 작업을 백엔드에서 관리하기
- Docker Compose로 백엔드 스택을 올리고 데스크톱 앱과 연결하기

## 이런 사용자에게 맞습니다

- 코드베이스를 빠르게 이해하고 싶은 개발자
- 특정 기능의 호출 흐름이나 저장 흐름을 추적하고 싶은 사용자
- 로컬 코드와 서버형 검색을 섞어서 grounded 답변을 받고 싶은 팀

## 가장 빠른 시작 방법

### 1. 백엔드 실행

```bash
cd backend
cp .env.compose.example .env
docker compose up -d --build
```

헬스 체크:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

### 2. 데스크톱 실행

```bash
cd desktop
npm install
npm run dev
```

개발용이 아니라 배포용 실행 파일이 필요하면:

```bash
cd desktop
npm install
npm run dist:portable
```

## 처음 쓰는 순서

1. 백엔드를 띄웁니다.
2. 데스크톱 앱을 실행합니다.
3. 워크스페이스 루트를 연결합니다.
4. 파일을 선택하거나 코드 범위를 읽은 뒤 질문합니다.
5. 답변에 나온 근거 파일과 흐름을 같이 확인합니다.

## 질문 예시

- `이 함수가 DB에 저장하는 흐름 정리해줘`
- `이 클래스가 어디서 호출되는지 추적해줘`
- `이 화면에서 정합 결과가 만들어지는 흐름 설명해줘`
- `이 오류 메시지가 어떤 조건에서 나오는지 찾아줘`

## 저장소 구조

- [`backend/app/`](./backend/app): API, 채팅 파이프라인, 검색/도구 런타임
- [`backend/.profiles/`](./backend/.profiles): 런타임 규칙과 설정
- [`backend/scripts/`](./backend/scripts): 배포/운영 스크립트
- [`desktop/src/main/`](./desktop/src/main): Electron 메인 프로세스와 로컬 툴 루프
- [`desktop/src/renderer/`](./desktop/src/renderer): 앱 UI
- [`docs/`](./docs): 설계 문서와 참고 자료

## 자주 보는 설정 파일

- [`backend/.profiles/rag_config.yaml`](./backend/.profiles/rag_config.yaml)
- [`backend/.env.example`](./backend/.env.example)
- [`backend/.env.compose.example`](./backend/.env.compose.example)
- [`desktop/package.json`](./desktop/package.json)

## 개발 명령어

백엔드 스택 배포:

```bash
bash backend/scripts/deploy_stack.sh --skip-update
```

데스크톱 빌드:

```bash
cd desktop
npm run build
```

포터블 exe 생성:

```bash
cd desktop
npm run dist:portable
```

## 참고

- 이 프로젝트는 일반적인 범용 챗봇보다 코드 근거 추적에 더 초점을 둡니다.
- 상위 `README`는 빠른 시작용이고, 세부 설계는 [`docs/`](./docs) 아래에 있습니다.
