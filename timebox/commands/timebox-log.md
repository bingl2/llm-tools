---
name: timebox-log
description: "현재 블록의 작업 로그 기록 + 체크리스트 갱신"
category: productivity
---

# /timebox-log - 블록 작업 로그 + 체크리스트 갱신

현재 세션에서 수행한 작업을 타임박스 로그로 남기고, 마스터 파일의 체크리스트도 함께 갱신합니다.

## 경로 설정

```
Base Path: $TIMEBOX_HOME (환경변수 미설정 시 ~/timebox)
Plans: {base}/plans/
Logs: {base}/logs/
```

- 시작 시 `echo $TIMEBOX_HOME`으로 확인. 없으면 `~/timebox` 사용.
- `{base}/logs/{오늘날짜}/` 디렉토리가 없으면 mkdir로 자동 생성.

## 실행 흐름

### 1단계: 현재 상태 확인

1. `date +%H:%M`으로 현재 시간 확인
2. 오늘 타임박스 파일 Read
   - 경로: `{base}/plans/{오늘날짜}.md`
   - **파일 없으면**: "`/timebox`로 먼저 플랜을 생성해주세요." 안내 후 종료
3. 현재 시각이 어느 블록에 해당하는지 파악

### 2단계: 작업 내용 정리

현재 세션의 대화 내용을 기반으로:
1. 어떤 작업을 했는지 요약
2. Big 3 중 어떤 항목과 관련되는지 매칭
3. 완료된 작업과 진행 중인 작업 분류
4. **이벤트 분류**: 이 블록의 흐름 유형 판단
   - `deep-work`: 계획대로 Deep Work 진행
   - `interrupt`: 외부 인터럽트로 계획 변경 (누구에게서, 무엇 때문에)
   - `switch`: 자발적 작업 전환 (왜 전환했는지)
   - `ad-hoc`: 예상 외 작업 발생
   - `break`: 휴식/이동
   - `shallow`: Shallow Work (이메일, 리뷰, 미팅 등)
5. **목표 연결** (`related_to`): 이 작업이 어떤 목표에 기여하는지
   - Big 3 항목 번호 (예: "Big 1-A")
   - 주간/월간 목표 (예: "W1: TNA-5967 완료")
   - 없으면: "ad-hoc" 또는 "유지/운영"

### 3단계: 로그 파일 생성/업데이트

**경로**: `{base}/logs/{YYYY-MM-DD}/{HHmm}-timebox-{블록타입}.md`

```markdown
# {HH:MM} Timebox Log - {블록타입}

## Block
{HH:MM}-{HH:MM} | {블록타입}
Focus: {Big 3 항목}

## Event
- type: {deep-work | interrupt | switch | ad-hoc | break | shallow}
- related_to: {Big 3 항목 번호 또는 목표, 없으면 "ad-hoc"}
- energy: {1-5, 체감 에너지 수준}
- trigger: {interrupt/switch일 경우 원인. 없으면 생략}

## Work Done
- {작업 내용 1}
- {작업 내용 2}

## Status
- Big 3 #1: {진행률 또는 완료}
- Big 3 #2: {진행률}

## Decisions
- {주요 결정사항}

## Notes
- {메모}
```

### 4단계: 마스터 파일 갱신

1. 마스터 파일을 Read하여 최신 내용 확인
2. 완료된 작업: `- [ ]` → `- [x]` 변환 (Edit)
3. Big 3 완료 시: `1. [ ]` → `1. [x]` 변환 (Edit)
4. 새로운 서브태스크 추가 (필요시 Edit)
5. **반드시 Read 후 Edit 사용. Write 금지.**

### 5단계: 진행률 안내

```
## 타임박스 진행률

Big 3: 1/3 완료
- [x] API 리팩토링
- [ ] 프론트엔드 수정 (60% 진행)
- [ ] 테스트 작성

현재 블록: Deep Work (14:00-15:30) - 남은 시간 45분
다음 블록: Break (15:30-15:45)
```

**Big 3 정렬도:**
- 이 세션 작업이 Big 3 중 어디에 기여했는지 명시
- 기여도 없으면 솔직하게: "이번 작업은 Big 3와 직접 관련이 없습니다."
- 하루 전체 시간 중 Big 3에 투자한 비율 계산:
  `"오늘 Deep Work {n}시간 중 Big 3에 실제 투자: {n}시간 ({n}%)"`

## 참고

- 마스터 파일: `{base}/plans/{YYYY-MM-DD}.md`
- 로그 경로: `{base}/logs/{YYYY-MM-DD}/`
- 날짜별 로그 폴더가 없으면 자동 생성
- 프로젝트명 축약: mrt-experiences → mrt-exp 등
- **마스터 파일은 절대 Write 금지. 반드시 Read 후 Edit만 사용.**
