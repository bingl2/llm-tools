# Claude Tools

Productivity plugins for Claude Code.

## Available Plugins

### [Timebox](./timebox/)
타임박싱 기반 하루 계획 + 목표 정렬 코칭 시스템.

- 목표 계층 관리 (연간 → 월간 → 주간 → 일간)
- Big 3 중심의 하루 설계
- 자동 체크인 + 에너지 추적
- 팩트 기반 리뷰 코칭

## Installation

```bash
# 마켓플레이스에서 설치
claude plugin marketplace add https://github.com/choihyunbin/claude-tools.git

# 원하는 플러그인 설치
claude plugin install timebox
```

## Configuration

각 플러그인은 환경변수로 데이터 경로를 설정할 수 있습니다:

```bash
# Timebox 데이터 경로 (기본: ~/timebox)
export TIMEBOX_HOME=~/my-timebox
```
