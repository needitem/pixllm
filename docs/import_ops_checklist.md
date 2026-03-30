# Import/Index 운영 체크리스트

운영 중 발생하는 업로드·인덱싱 문제의 재시도·취소·정리 절차를 기술합니다.

---

## 1. 에러 유형별 초기 대응

| 에러 코드 | 현상 | 즉시 조치 |
|-----------|------|-----------|
| `PAYLOAD_TOO_LARGE` (413) | 대용량 파일 업로드 실패 | 파일 분할 후 재업로드. Nginx `client_max_body_size` 확인 |
| `CONNECTION_ABORTED` | 업로드 중 연결 끊김 | 네트워크 안정화 후 재시도. 업로드 세션 만료(6h) 고려 |
| `PERMISSION_DENIED` | MarginIO AccessDenied / PermissionError | MinIO 버킷 정책·IAM 설정 확인. 파일시스템 권한 점검 |
| `SERVER_ERROR` (5xx) | 서버 내부 오류 | FastAPI / MinIO / Qdrant 컨테이너 로그 확인 |
| `UPLOAD_TIMEOUT` | 인덱싱 하트비트 만료 | `FILE_INDEXING_STALE_SECONDS` 설정 확인 후 재업로드 |

---

## 2. Import 잡 재시도 절차

### 2-1. 상태 확인
```bash
# 잡 목록 조회
curl http://localhost:8000/v1/imports

# 특정 잡 상태 확인
curl http://localhost:8000/v1/imports/<job_id>
```

### 2-2. 재시도 (실패 잡 재실행)
> 현재 직접 재시도 API는 없습니다. 아래 순서로 새 잡을 생성합니다.
1. `DELETE /v1/imports/<failed_job_id>` — 실패 잡 및 불완전 벡터 정리
2. 동일 경로·프로젝트로 `POST /v1/imports` 혹은 `POST /v1/imports/repo` 재호출
3. 신규 `job_id`로 진행 상황 폴링

---

## 3. Import 잡 취소 절차

1. **취소 요청 전송**
   ```bash
   curl -X POST http://localhost:8000/v1/imports/<job_id>/cancel
   ```
2. 백그라운드 태스크는 파일 단위 루프 내에서 취소 플래그를 감지하고 조기 종료합니다.
3. 상태가 `cancelled`로 전환되면 해당 잡의 데이터를 정리합니다 (아래 참조).

---

## 4. 불완전 데이터 정리 절차

```bash
# 잡 전체 삭제 (Qdrant 벡터 + MinIO 객체 + Redis 레코드)
curl -X DELETE http://localhost:8000/v1/imports/<job_id>
```

벡터는 `job_id` 페이로드 필드 기준으로 필터 삭제되므로, 다른 잡의 데이터에 영향을 주지 않습니다.

### 고립 벡터 수동 정리 (비상시)
```python
# Qdrant Python 클라이언트
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = QdrantClient("localhost", port=6333)
client.delete(
    collection_name="documents",
    points_selector=Filter(
        must=[FieldCondition(key="job_id", match=MatchValue(value="<job_id>"))]
    )
)
```

---

## 5. 코드 모드 메타 검증

코드 모드 잡은 벡터 임베딩 없이 메타데이터만 등록합니다.
`embedded_chunks=0, total_chunks=0` 규칙이 깨진 경우 아래 스크립트로 확인합니다.

```bash
cd backend
python scripts/validate_code_mode_meta.py --redis-url redis://localhost:6379

# Redis 없이 dry-run 테스트
python scripts/validate_code_mode_meta.py --dry-run
```

위반 발견 시 해당 잡을 삭제 후 재인덱스합니다.

---

## 6. 로컬 폴더 업로드 세션 만료

업로드 세션은 Redis에 **6시간** TTL로 저장됩니다.
세션 만료 후 `finalize` 호출 시 `NOT_FOUND` 에러가 반환됩니다.

→ 세션 만료 시 `session_id` 없이 `stage` → `finalize`를 처음부터 다시 시작합니다.

---

## 7. 배치 실패 대응 (SVN/TFS 동기화)

| 실패 원인 | 오류 패턴 | 조치 |
|-----------|-----------|------|
| SVN 인증 실패 | `authentication error from server` | `svn_username`, `svn_password` 재확인 |
| SVN 연결 실패 | `E170013: Unable to connect` | URL·네트워크 경로·SVN 데몬 상태 확인 |
| TFS 명령 없음 | `command not found` | `TFS_DOCS_SYNC_COMMAND` 환경 변수 설정 확인 |
| 경로 권한 | `permission denied` | `IMPORT_DOCS_ROOT` / `IMPORT_CODE_ROOT` 디렉터리 권한 확인 |

---

## 8. 모니터링 포인트

- **Redis**: `import_job:index` 세트 크기, 각 잡 상태 추적
- **MinIO**: `imports/` 프리픽스 오브젝트 수, 스토리지 사용량
- **Qdrant**: 컬렉션 포인트 수 (`documents`, `code_snippets`)
- **FastAPI**: `/v1/health` 엔드포인트 정기 폴링

```bash
# 시스템 헬스 확인
curl http://localhost:8000/v1/health
```
