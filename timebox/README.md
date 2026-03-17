# Timebox - Claude Code Plugin

타임박싱 기반 하루 계획 + 목표 정렬 코칭 시스템.

## What is Timebox?

Timebox는 **시간 중심**으로 하루를 설계합니다:
- 목표 계층(연간→월간→주간)을 기반으로 매일의 **Big 3**를 정하고
- 시간 블록으로 배치하여 **"언제 무엇을 하나"**를 명확히 합니다
- 자동 체크인으로 하루를 추적하고, 마감 시 팩트 기반 리뷰를 제공합니다

## Installation

```bash
# 플러그인 설치 (마켓플레이스 등록 후)
claude plugin marketplace add https://github.com/choihyunbin/claude-tools.git
claude plugin install timebox
```

## Setup

```bash
# (선택) 데이터 저장 경로 변경
export TIMEBOX_HOME=~/my-timebox   # 기본값: ~/timebox
```

## Commands

### `/timebox-init` - 목표 설정 (처음 1회 or 시즌 변경)

대화형 인터뷰로 목표 계층을 세웁니다:
- **Foundation**: 방향, 역할, 제약, 유지선, 안 할 것
- **연간 목표**: 3~5개, 성공 기준 포함
- **월간 목표**: 1~3개, 연간 목표와 연결
- **주간 목표**: 3~5개, 월간 목표와 연결

모드:
- `cold-start`: 처음 세팅
- `refresh`: 주간/월간 업데이트 (매주 월요일)
- `realign`: Foundation부터 재검토

### `/timebox` - 매일 아침 플랜 생성

1. 주간/월간 목표 기반으로 Big 3 코칭
2. 도전 질문으로 스코핑 검증
3. 시간 블록 배치
4. 자동 체크인 루프 시작

### `/timebox-check` - 자동 체크인 (loop 연동)

5분마다 현재 블록 상태를 알려줍니다:
- 현재 Focus + 남은 시간
- 블록 전환 알림
- 시간 초과 경고
- 코치 한마디 (명언/동기부여)

### `/timebox-next` - 블록 전환

현재 블록 체크인 + 다음 블록 안내:
- 진행 상태 확인
- 에너지 체크
- 블록 조정 (연장/단축)

### `/timebox-log` - 작업 기록

세션 작업을 로그로 남기고 체크리스트 갱신:
- Big 3 진행률 추적
- 정렬도 분석

### `/timebox-end` - 하루 마감

Big 3 리뷰 + 에너지 패턴 분석 + 내일 준비:
- 냉정한 성과 리뷰
- 블록 준수율 분석
- 주간 목표 진행률 (금요일)
- Tomorrow Candidates 제안

## Data Structure

```
$TIMEBOX_HOME/              # 기본: ~/timebox
├── goals/
│   ├── _foundation.md      # 방향, 역할, 제약, 체크인 주기
│   ├── {YYYY}.md           # 연간 목표
│   ├── {YYYY-MM}.md        # 월간 목표
│   └── {YYYY}-W{WW}.md    # 주간 목표
├── plans/
│   └── {YYYY-MM-DD}.md    # 일간 Big 3 + 블록 스케줄
├── logs/
│   └── {YYYY-MM-DD}/
│       └── {HHmm}-timebox-{블록타입}.md
└── reviews/
    └── {YYYY-MM-DD}-timebox-review.md
```

## Goal Hierarchy

```
Foundation (방향, 제약, 유지선, 안 할 것)
  └→ {YYYY}.md (연간 3~5개, 성공 기준)
       └→ {YYYY-MM}.md (월간 1~3개, Parent: Y1)
            └→ {YYYY}-W{WW}.md (주간 3~5개, Parent: M1)
                 └→ {YYYY-MM-DD}.md (일간 Big 3, Parent: W1)
```

모든 하위 목표는 상위 목표에 `Parent:` 태그로 연결됩니다.

## Daily Flow

```
/timebox-init     (한 번 or 시즌 변경 시)
  └→ /timebox     (매일 아침)
       └→ /timebox-check  (자동, 주기는 init에서 설정)
       └→ /timebox-next   (블록 전환 시)
       └→ /timebox-log    (작업 구간 종료 시)
       └→ /timebox-end    (하루 마감)
```

## Configuration

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `$TIMEBOX_HOME` | `~/timebox` | 데이터 저장 경로 |
| 체크인 주기 | `_foundation.md`에서 설정 (기본 5분) | `/timebox`에서 매일 조정 가능 |
| Deep Work 블록 | 90분 | 사용자 패턴에 따라 조정 |
| Break | 15분 | 종료 의식 포함 |
