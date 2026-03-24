---
name: timebox-setup
description: "타임박스 시스템 설정 - 경로, 연동, 운영 옵션 구성"
category: productivity
---

# /timebox-setup - 시스템 설정

타임박스 시스템의 환경을 세팅합니다. 최초 1회 실행하고, 이후 설정을 바꿀 때만 다시 실행합니다.

## 실행 흐름

### 1단계: 기존 상태 확인

1. `echo $TIMEBOX_HOME`으로 환경변수 확인
2. 환경변수가 있으면 해당 경로를 base로 사용
3. `{base}/_config.md` 존재 여부 확인

**상황별 분기:**
- **최초 설치** (환경변수 없음): → 2단계부터 전부 실행
- **설정 변경** (_config.md 있음): → 현재 설정 보여주고 "무엇을 바꾸시겠습니까?" 질문
- **마이그레이션** (_foundation.md 있음 + _config.md 없음): → 3단계에서 기존 값 이관

### 2단계: 경로 설정 (최초 설치 시)

1. AskUserQuestion: "타임박스 데이터를 저장할 경로를 정해주세요. (기본값: ~/timebox)"
2. 사용자가 경로를 지정하면 해당 경로, Enter만 치면 `~/timebox` 사용
3. 디렉토리 구조 생성: `mkdir -p {base}/{plans,logs,reviews,goals}`
4. 쉘 프로필에 환경변수 추가:
   - `~/.zshrc` (macOS/zsh) 또는 `~/.bashrc` (Linux/bash)에:
     ```
     export TIMEBOX_HOME="{사용자가 지정한 경로}"
     ```
   - 추가 전 이미 TIMEBOX_HOME이 있는지 grep으로 확인. 있으면 스킵.
5. "TIMEBOX_HOME={경로}로 설정했습니다. 새 터미널부터 자동 적용됩니다." 안내
6. 현재 세션에서도 사용하기 위해 `export TIMEBOX_HOME="{경로}"` 실행

### 3단계: 설정 파일 생성

**최초 설치 시:**
기본값으로 `{base}/_config.md` 생성:

```markdown
# Timebox Config

## 경로
- home: {사용자가 지정한 경로}

## 연동
- github_sync: off
- notification_channel: claude-code  <!-- claude-code | telegram -->
- google_calendar: off

## 운영
- checkin_interval: 5  <!-- 분 -->
- deep_work_block: 90  <!-- 분 -->
- break_duration: 15  <!-- 분 -->

## 변경 이력
- {오늘 날짜}: 초기 설정 생성
```

**마이그레이션 시** (_foundation.md 있음 + _config.md 없음):
1. `{base}/goals/_foundation.md` Read
2. "운영" 섹션에서 설정값 추출 (체크인 주기, 리뷰 주기 등)
3. 추출한 값으로 `_config.md` 생성
4. `_foundation.md`에서 "운영" 섹션 제거 (Edit)
5. "기존 _foundation.md의 운영 설정을 _config.md로 이관했습니다." 안내

### 4단계: 설정 확인

생성된 설정을 보여주고:
```
"설정이 완료되었습니다:
- 데이터 경로: {경로}
- 체크인 주기: {n}분
- 연동: GitHub(off), Telegram(off), Google Calendar(off)

설정을 변경하려면 언제든 /timebox-setup을 다시 실행하세요.
다음 단계: /timebox-align으로 목표를 설정하세요."
```

## 설정 변경 모드

_config.md가 이미 있을 때 `/timebox-setup` 실행 시:

1. 현재 설정 전체를 보여줌
2. AskUserQuestion: "어떤 설정을 변경하시겠습니까?"
3. 사용자가 지정한 항목만 Edit으로 변경
4. 변경 이력에 기록 추가

## 설정 파일 위치

```
{base}/_config.md    # 시스템 설정 (이 커맨드가 관리)
{base}/goals/        # 목표 파일들 (/timebox-align이 관리)
```

## config vs foundation 분리 기준

- `_config.md`: 시스템 동작 설정 — "도구가 어떻게 동작할지"
  - 체크인 주기, 블록 길이, 연동 on/off
- `_foundation.md`: 자기 지식 — "나는 어떤 사람인지"
  - 에너지 패턴, 회피 트리거, 검증된 전략, 방향, 역할

## 미래 TODO

> 아래 기능들은 방향성만 기록. 구현 시 이 파일의 3단계에 설정 항목 추가.

- [ ] **GitHub 연동**: 로그/리뷰 자동 commit + push (on/off, remote URL, push 주기 — `/timebox-end` 시 자동 실행)
- [ ] **알림 채널**: Telegram 봇 연동 (`/timebox-loop` 출력을 Telegram으로 전송)
- [ ] **Google Calendar 연동**: `/timebox` 생성 일정을 Google Calendar 이벤트로 생성

## 핵심 규칙

- `_config.md`는 반드시 Read 후 Edit. Write 금지 (마이그레이션 초기 생성 제외).
- 설정 변경 시 변경 이력 섹션에 날짜 + 변경 내용 기록.
- 경로 관련 설정은 환경변수(`$TIMEBOX_HOME`)가 우선. _config.md의 home은 참조용.
