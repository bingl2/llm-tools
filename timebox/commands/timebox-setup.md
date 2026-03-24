---
name: timebox-setup
description: "타임박스 시스템 설정 - 경로, 연동, 운영 옵션 구성"
category: productivity
---

# /timebox-setup - 시스템 설정

타임박스 시스템의 환경을 세팅합니다. 최초 1회 실행하고, 이후 설정을 바꿀 때만 다시 실행합니다.

## 실행 흐름

### 0단계: CLI 설치 확인

> 이 단계는 timebox CLI가 설치되어 있는지 확인하고, 없으면 자동 설치합니다.

1. `which timebox` 실행하여 CLI 설치 여부 확인
2. **이미 설치됨** → 바로 1단계로 진행
3. **미설치 시** 순서대로 진행:

**3-1. Python 확인:**
- `python3 --version`으로 Python 3.11+ 확인
- 없거나 3.11 미만이면 안내 후 중단:
  ```
  "Python 3.11 이상이 필요합니다.
   - macOS: brew install python
   - 기타: https://python.org 에서 설치
   설치 후 /timebox-setup을 다시 실행해주세요."
  ```

**3-2. uv 확인 + 설치:**
- `which uv`로 확인
- 없으면 AskUserQuestion: "패키지 관리자 uv를 설치해야 합니다. 설치할까요? (Y/n)"
  - Y → `curl -LsSf https://astral.sh/uv/install.sh | sh` 실행
  - n → "uv 없이는 CLI를 설치할 수 없습니다." 안내 후 중단

**3-3. CLI 설치:**
- **경로 탐색** (우선순위):
  1. 현재 커맨드 파일의 상대 경로 기반: 이 프롬프트(`timebox-setup.md`)가 `{플러그인루트}/commands/` 안에 있으므로, `{플러그인루트}/cli/pyproject.toml` 존재 여부를 확인하여 CLI 경로 확보
  2. Fallback: Glob으로 `**/timebox/cli/pyproject.toml` 검색 (검색 범위: `~/.claude/`, 홈 디렉토리)
- `uv tool install {CLI경로}` 실행
- `timebox --help`로 설치 확인
- 실패 시 수동 설치 안내:
  ```
  "자동 설치에 실패했습니다. 아래 명령어로 직접 설치해주세요:
   cd {플러그인경로}/cli && uv tool install ."
  ```

**3-4. 설치 완료 안내:**
```
"timebox CLI가 설치되었습니다."
```

### 1단계: 기존 상태 확인

1. `echo $TIMEBOX_HOME`으로 환경변수 확인
2. 환경변수가 있으면 해당 경로를 base로 사용
3. `{base}/_config.md` 존재 여부 확인

**상황별 분기:**
- **최초 설치** (환경변수 없음): → 2단계부터 전부 실행
- **설정 변경** (_config.md 있음): → 현재 설정 보여주고 "무엇을 바꾸시겠습니까?" 질문

### 2단계: 초기화 + 경로 설정 (최초 설치 시)

1. AskUserQuestion: "타임박스 데이터를 저장할 경로를 정해주세요. (기본값: ~/timebox)"
2. 사용자가 경로를 지정하면 해당 경로, Enter만 치면 `~/timebox` 사용
3. **CLI로 초기화**: `timebox init --home-override {경로}` 실행
   - 디렉토리 구조(plans, logs, reviews, goals)와 기본 `_config.md`를 자동 생성
4. 쉘 프로필에 환경변수 추가:
   - `$SHELL`에 따라 `~/.zshrc` (zsh) 또는 `~/.bashrc` (bash)에:
     ```
     export TIMEBOX_HOME="{사용자가 지정한 경로}"
     ```
   - 추가 전 이미 TIMEBOX_HOME이 있는지 grep으로 확인. 있으면 스킵.
5. "TIMEBOX_HOME={경로}로 설정했습니다. 새 터미널부터 자동 적용됩니다." 안내
6. 현재 Claude Code 세션에서도 사용하기 위해 `export TIMEBOX_HOME="{경로}"` 실행

### 3단계: 운영 설정 커스텀

**최초 설치 시:**

`timebox init`이 기본 `_config.md`를 생성한 뒤, AskUserQuestion으로 핵심 운영 설정을 확인합니다:

1. "Deep Work 블록 길이를 정해주세요. (기본값: 90분)"
   - 60분, 90분, 120분 등 사용자 선호에 따라 설정
   - 이 값이 "1블록"의 기준이 됩니다 (Estimation Accuracy 등에서 사용)
2. "체크인 루프 주기를 정해주세요. (기본값: 15분)"
   - `/loop {n}m /timebox-loop`으로 자동 알림이 이 주기로 실행됩니다

사용자가 Enter만 치면 기본값(90분, 15분) 유지. 변경이 있으면 `{base}/_config.md`를 Read 후 Edit으로 해당 값만 수정.

**_config.md 구조** (init이 생성하는 기본값):

```markdown
# Timebox Config

## 경로
- home: {사용자가 지정한 경로}

## 연동
- github_sync: off
- notification_channel: claude-code  (claude-code | telegram)
- google_calendar: off

## 운영
- checkin_interval: 15  (분 — 체크인 루프 주기)
- deep_work_block: 90  (분 — 1블록의 기준 시간)
- break_duration: 15  (분)

## 변경 이력
- {오늘 날짜}: 초기 설정 생성
```

### 4단계: 설정 확인

생성된 설정을 보여주고:
```
"설정이 완료되었습니다:
- 데이터 경로: {경로}
- Deep Work 블록: {n}분 (= 1블록)
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
- `{올해}-foundation.md`: 자기 지식 — "나는 어떤 사람인지"
  - 에너지 패턴, 회피 트리거, 검증된 전략, 방향, 역할

## 핵심 규칙

- `_config.md`는 반드시 Read 후 Edit. Write 금지 (초기 생성 제외).
- 설정 변경 시 변경 이력 섹션에 날짜 + 변경 내용 기록.
- 경로 관련 설정은 환경변수(`$TIMEBOX_HOME`)가 우선. _config.md의 home은 참조용.
