# PIXLLM

PIXLLM은 로컬 코드베이스에 대해 질문하고, 그 답변의 근거가 되는 파일, 심볼, 실행 흐름을 같은 화면에서 바로 확인할 수 있게 만든 데스크톱 워크벤치입니다.

단순히 "대답만 받는" 도구가 아니라, "왜 그런 답이 나왔는지"를 근거와 함께 따라가고 싶은 사용자를 위한 앱입니다.

![PIXLLM 운용 화면](docs/assets/pixllm-desktop-main.png)

_예시 운용 화면: 왼쪽에는 워크스페이스/세션, 가운데에는 대화, 오른쪽에는 근거 파일과 실행 상세 정보가 보입니다._

## 사용자는 이렇게 씁니다

사용 흐름은 단순합니다.

1. 백엔드를 실행합니다.
2. 데스크톱 앱을 엽니다.
3. 확인하고 싶은 워크스페이스를 선택합니다.
4. 자연어로 질문합니다.
5. 답변과 함께 근거 파일, 실행 흐름, 추적 결과를 확인합니다.

정확한 파일명을 몰라도 바로 시작할 수 있습니다. 보통은 팀원에게 묻듯이 질문하면 됩니다.

- `이 오류 메시지가 어디서 나오는지 찾아줘`
- `이 화면이 최종 결과를 만드는 흐름을 설명해줘`
- `이 클래스가 어디서 호출되는지 추적해줘`
- `이 값이 DB에 저장되는 경로를 정리해줘`

## 화면에서 바로 보이는 것

이 앱은 데모용 채팅 화면이 아니라 실제 코드 추적 작업 기준으로 구성되어 있습니다.

- 왼쪽: 워크스페이스, 세션, 실행 맥락
- 가운데: 메인 대화
- 오른쪽: 근거 파일, 실행 상세, 추적 정보

즉, 질문하고 끝나는 구조가 아니라 질문에서 근거 파일 확인까지 바로 이어집니다.

## 이런 사용자에게 맞습니다

다음 상황에서 특히 유용합니다.

- 처음 보는 코드베이스를 빠르게 이해하고 싶을 때
- 기능 흐름을 파일 단위로 따라가야 할 때
- 값, 이벤트, 오류가 어디서 만들어지는지 확인해야 할 때
- 단순 요약이 아니라 근거가 있는 답변이 필요할 때
- 로컬 워크스페이스 검색과 서버형 참조 검색을 함께 쓰고 싶을 때

## 빠른 시작

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

### 2. 데스크톱 앱 실행

```bash
cd desktop
npm install
npm run dev
```

### 3. 포터블 실행 파일 만들기

```bash
cd desktop
npm install
npm run dist:portable
```

빌드가 끝나면 포터블 실행 파일은 아래 경로에 생성됩니다.

- [`desktop/release/PIXLLM Desktop-0.1.0-portable.exe`](./desktop/release/PIXLLM%20Desktop-0.1.0-portable.exe)

## 처음 쓰는 사용자 기준 순서

처음 실행할 때는 아래 순서가 가장 자연스럽습니다.

1. 백엔드 스택을 올립니다.
2. 데스크톱 앱을 실행합니다.
3. 분석할 워크스페이스 루트를 연결합니다.
4. 기능, 오류, 저장 흐름 중 하나를 질문합니다.
5. 답변 오른쪽 패널에서 근거 파일과 실행 정보를 확인합니다.
6. 필요하면 질문을 더 좁혀서 파일 단위로 다시 추적합니다.

## 질문 예시

- `이 화면의 호출 흐름 요약해줘`
- `이 응답 필드가 어디서 매핑되는지 찾아줘`
- `이 팝업을 띄우는 파일이 어디인지 알려줘`
- `submit 버튼 이후 저장 경로를 추적해줘`
- `이 오류 메시지가 어떤 조건에서 발생하는지 찾아줘`

## 저장소 구조

- [`desktop/`](./desktop): Electron 기반 데스크톱 앱
- [`backend/`](./backend): FastAPI 기반 백엔드와 오케스트레이션 API
- [`docs/`](./docs): 설계 문서와 참고 자료

조금 더 구체적으로 보면:

- [`desktop/src/main/`](./desktop/src/main): Electron 메인 프로세스와 로컬 툴 루프
- [`desktop/src/renderer/`](./desktop/src/renderer): 사용자가 직접 보게 되는 UI
- [`backend/app/`](./backend/app): API, 채팅 파이프라인, 검색, 런타임 로직
- [`backend/.profiles/`](./backend/.profiles): 프로파일과 런타임 설정
- [`backend/scripts/`](./backend/scripts): 배포 및 운영 스크립트

## 자주 보는 파일

- [`backend/.profiles/rag_config.yaml`](./backend/.profiles/rag_config.yaml)
- [`backend/.env.example`](./backend/.env.example)
- [`backend/.env.compose.example`](./backend/.env.compose.example)
- [`desktop/package.json`](./desktop/package.json)

## 자주 쓰는 명령어

백엔드 스택:

```bash
bash backend/scripts/deploy_stack.sh --skip-update
```

데스크톱 검증:

```bash
cd desktop
npm run check
npm run build
```

포터블 패키징:

```bash
cd desktop
npm run dist:portable
```

## 참고

- PIXLLM은 범용 챗봇보다는 코드 근거 추적에 더 초점을 둡니다.
- 이 README는 사용자 입장에서 빠르게 시작할 수 있도록 구성했습니다.
- 더 자세한 아키텍처와 구현 메모는 [`docs/`](./docs) 아래에 있습니다.
