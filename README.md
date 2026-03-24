# llm-tools

Claude Code용 생산성 플러그인 모음.

## [Timebox](./timebox/)

**목표 정렬 + 시간 블록 + 자기 지식의 닫힌 루프.**

"뭘 하지?"가 아니라 "이 시간에 이 결과를 낸다"로 하루를 설계하고, 매일 기록하고, 매주 패턴을 발견하고, 그 패턴이 다음 날의 플랜을 더 정확하게 만들어줍니다.

### 커맨드

| 커맨드 | 역할 |
|--------|------|
| `/timebox-setup` | 시스템 설정 (경로, 블록 길이, 체크인 주기) |
| `/timebox-align` | 목표 정렬 코칭 (Foundation + 연간/월간/주간 목표) |
| `/timebox` | 아침 설계 (Big 3 + 시간 블록 배치) |
| `/timebox-loop` | 자동 블록 알림 (질문 없이 출력만) |
| `/timebox-now` | 지금 뭐하지? (대화형 체크인) |
| `/timebox-log` | 작업 로그 기록 + 체크리스트 갱신 |
| `/timebox-end` | 하루 마감 (Big 3 리뷰 + 내일 준비) |
| `/timebox-review` | 패턴 리뷰 (주간/월간/연간 회고) |

자세한 내용은 [Timebox README](./timebox/README.md)를 참고하세요.

## 설치

### Marketplace (권장)

Claude Code에서 `/plugin` → Marketplace → **Add Market**에 아래 URL을 등록합니다:

```
https://github.com/bingl2/llm-tools.git
```

등록 후 Marketplace에서 `timebox`를 찾아 Install하면 됩니다.

### Git Clone (직접 설치)

```bash
git clone https://github.com/bingl2/llm-tools.git
```

클론 후 Claude Code에서 `/plugin` → **Add local** → 클론한 경로를 입력하면 로컬 플러그인으로 등록됩니다.

## 설정

| 환경변수 | 기본값 | 설명 |
|----------|--------|------|
| `$TIMEBOX_HOME` | `~/timebox` | 타임박스 데이터 저장 경로 |

`/timebox-setup`을 실행하면 경로, 블록 길이, 체크인 주기 등을 설정할 수 있습니다.
