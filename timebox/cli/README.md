# timebox CLI

타임박싱 기반 시간 관리 CLI — LLM 코칭 시스템의 데이터 엔진.

프롬프트(`/timebox`, `/timebox-end` 등)가 코칭 대화를 담당하고, 이 CLI가 마크다운 파일의 **읽기/쓰기/계산**을 담당합니다. 모든 출력은 JSON이며, 프롬프트가 파싱하기 쉽도록 설계되었습니다.

## 설치

```bash
cd timebox/cli
uv pip install -e ".[dev]"
```

설치 후 `timebox` 명령어가 사용 가능합니다.

## 커맨드

### `timebox init`

디렉토리 구조(`plans/`, `logs/`, `reviews/`, `goals/`)와 `_config.md`를 생성합니다.

### `timebox plan`

| 서브커맨드 | 설명 |
|-----------|------|
| `plan show [--date YYYY-MM-DD]` | 플랜 조회. 파일 없으면 빈 데이터 반환 (exit 0) |
| `plan create [--date]` | stdin JSON으로 플랜 마크다운 생성 |
| `plan check [--date] --item TEXT` | 체크리스트 항목 토글 `[ ]` ↔ `[x]` |
| `plan energy [--date] --time HH:MM --level N` | Energy Log 테이블에 행 추가 |

### `timebox now`

```bash
timebox now [--date YYYY-MM-DD] [--time HH:MM]
```

현재 블록, 남은 시간, 다음 블록, Big 3 진행 상황을 반환합니다. 플랜이 없으면 빈 상태를 반환합니다.

### `timebox log`

| 서브커맨드 | 설명 |
|-----------|------|
| `log create [--date] --time HH:MM [--type TYPE] [--related TEXT] [--summary TEXT]` | 작업 로그 파일 생성 |

`--type`: `deep-work` (기본), `shallow`, `ad-hoc`, `interrupt`

### `timebox goals`

| 서브커맨드 | 설명 |
|-----------|------|
| `goals show --scope yearly\|monthly\|weekly` | 목표 조회. 파일 없으면 빈 배열 반환 (exit 0) |
| `goals progress [--year N] [--week N]` | 주간 목표 진행 현황 (Big 3 참조 집계) |

### `timebox stats`

| 서브커맨드 | 설명 |
|-----------|------|
| `stats today [--date]` | 일간 통계. 플랜 없으면 빈 데이터 반환 (exit 0) |
| `stats week [--year N] [--week N]` | 주간 통계 |
| `stats month [--year N] [--month N]` | 월간 통계 |
| `stats carry-over [--count N]` | carry-over 항목 연속 일수 통계 |

### `timebox review`

| 서브커맨드 | 설명 |
|-----------|------|
| `review show [--date]` | 리뷰 조회. 파일 없으면 빈 데이터 반환 (exit 0) |
| `review create [--date]` | stdin JSON으로 리뷰 마크다운 생성 |

### `timebox commit`

```bash
timebox commit [--push]
```

`plans/`, `logs/`, `reviews/`, `goals/`, `_config.md`를 자동 커밋합니다.

## 에러 처리 규칙

- **조회(show/read-only)** 커맨드: 데이터 없으면 **exit 0 + 빈 JSON** 반환
- **쓰기/수정** 커맨드: 필수 파일 없으면 **exit 1 + `{"error": "...", "code": "..."}`** 반환
- 설정 파일(`_config.md`) 없으면 항상 **exit 1**

## 데이터 구조

```
$TIMEBOX_HOME/          # 기본: ~/timebox
├── _config.md          # 설정 (블록 길이, 체크인 주기 등)
├── plans/              # 일간 플랜 (YYYY-MM-DD.md)
├── logs/               # 작업 로그 (YYYY-MM-DD/HHMM-type.md)
├── reviews/            # 리뷰 (YYYY-MM-DD-timebox-review.md)
└── goals/              # 목표 (YYYY.md, YYYY-MM.md, YYYY-WNN.md)
```

## 설정

| 환경변수 | 기본값 | 설명 |
|----------|--------|------|
| `TIMEBOX_HOME` | `~/timebox` | 데이터 저장 경로 |

또는 `--home` 옵션으로 오버라이드 가능합니다.

## 개발

```bash
uv pip install -e ".[dev]"
uv run pytest              # 테스트
uv run ruff check src/     # 린트
```
