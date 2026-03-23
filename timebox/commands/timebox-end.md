---
name: timebox-end
description: "타임박스 하루 마감 - Big 3 리뷰 + 에너지 패턴 분석 + 내일 준비"
category: productivity
---

# /timebox-end - 타임박스 하루 마감

오늘의 타임박스를 리뷰하고, 에너지 패턴을 분석하며, 내일을 준비합니다.

## 경로 설정

```
Base Path: $TIMEBOX_HOME (환경변수 미설정 시 ~/timebox)
Plans: {base}/plans/
Logs: {base}/logs/
Reviews: {base}/reviews/
Goals: {base}/goals/
```

- 시작 시 `echo $TIMEBOX_HOME`으로 확인. 없으면 `~/timebox` 사용.
- `{base}/reviews/` 디렉토리가 없으면 mkdir로 자동 생성.

## 실행 흐름

### 0단계: 체크인 루프 해제

1. CronList로 현재 활성 cron 목록 조회
2. `/timebox-check` 프롬프트를 가진 recurring job을 찾아 CronDelete로 해제
3. "체크인 루프 해제 완료" 안내

### 1단계: 데이터 수집

1. 오늘 타임박스 파일 Read
   - 경로: `{base}/plans/{오늘날짜}.md`
   - **파일 없으면**: "오늘 타임박스 파일이 없습니다." 안내 후 종료
2. 오늘 로그 파일 전부 Read
   - Glob 패턴: `{base}/logs/{오늘날짜}/*.md`
3. 목표 파일 확인:
   - `{base}/goals/{올해}-W{이번주}.md` (주간 목표) Read (있으면)
   - `{base}/goals/{올해-이번달}.md` (월간 목표) Read (있으면)

### 2단계: Big 3 냉정한 리뷰

```
## Big 3 결과

1. [x] API 리팩토링 → 완료! (2블록 사용, 예상 2블록)
2. [~] 프론트엔드 수정 → 70% 진행 (1블록 사용, 예상 1.5블록)
3. [ ] 테스트 작성 → 미착수

성공률: 1/3 완료, 1/3 진행중
```

**완료된 Big 3**: 구체적으로 뭐가 달성됐는지, 이게 진짜 의미있는 진전인지 평가.

**미완료 Big 3**: "왜 못 했는가?"를 파고듦:
- **시간 부족?** → "애초에 스코핑이 잘못됨. 내일은 더 작게."
- **ad-hoc 때문?** → "방어를 못 함. 내일은 오전 {n}블록을 반드시 사수하세요."
- **의지 문제?** → "어려운 작업을 미루지 않았나요? 내일은 가장 어려운 걸 첫 블록에."

미완료 Big 3에 대해 AskUserQuestion:
- **내일 Big 3에 포함**: 자동 carry-over
- **더 작게 분해**: 서브태스크로 쪼개서 내일 배치
- **드롭**: 더 이상 불필요

### 3단계: 블록 실행 분석

각 블록의 계획 vs 실제를 비교:

```
## 블록 분석

| Block | Plan | Actual | Match |
|-------|------|--------|-------|
| 09:00-10:30 Deep | API 리팩토링 | API 리팩토링 | O |
| 10:45-12:00 Deep | 프론트엔드 | 긴급 버그 수정 | X (ad-hoc) |
| 13:00-14:00 Shallow | 이메일/리뷰 | 이메일/리뷰 | O |
| 14:00-15:30 Deep | 테스트 작성 | 프론트엔드 이어서 | △ |
| 15:45-17:00 Flex | - | 테스트 일부 | - |

블록 준수율: 2/4 (50%)
```

**블록 준수율 해석:**
- 60% 이상: 현실적 배치
- 40% 미만: "계획이 현실과 너무 동떨어져 있습니다. 내일은 블록을 더 유연하게."

### 4단계: 에너지 패턴 분석

Energy Log 테이블이 있으면 분석:

```
## 에너지 패턴

오전 에너지: 높음 (4-5/5)
오후 에너지: 보통 (3/5)
최적 Deep Work 시간대: 09:00-12:00

💡 내일 제안: 가장 어려운 작업을 오전에 배치하세요.
```

### 5단계: 목표 정렬 분석

오늘 한 작업들을 목표 기준으로 분류:

```
## Goal Alignment

### 목표 직접 기여
- {Big 3 항목} → {주간/월간 목표와의 연결}

### 유지/운영
- {Shallow Work, 이메일, 리뷰 등}

### 예상 밖
- {ad-hoc 작업들}
```

**비율 계산**: "오늘 Deep Work {n}블록 중 목표 직접 기여: {n}블록 ({n}%)"

### 6단계: 리플렉션 + 하루 감상

**하루 감상 질문** (반드시 물어볼 것):
- "오늘 하루를 한 줄로 표현하면?" 또는 "오늘 하루 어땠어요?"
- 사용자가 `/timebox-end` 호출 시 이미 감상을 함께 남겼으면 그대로 사용
- 말하지 않았으면 AskUserQuestion으로 질문: "하루 한줄평을 남겨주세요. 기분, 느낌, 깨달은 것 뭐든."
- 응답은 Review 파일의 `## Daily One-liner` 섹션에 기록

**핵심 질문** (AskUserQuestion, 최대 2개):
1. "오늘 계획을 가장 크게 흔든 요인은?" (ad-hoc, 스코핑 문제, 에너지 저하 등)
2. "내일 반드시 이어가야 할 작업은?" (carry-forward 확인)

사용자가 스킵하면 질문 없이 진행.

**원문 보존 + 요약 원칙**:
- `## Reflection (원문)`: 사용자가 쓴 리플렉션을 **그대로** 보존한다. 정리, 요약, 교정하지 않는다.
- `## Reflection (요약)`: Claude가 원문을 읽고 핵심 포인트를 3-5줄로 정리한다. 나중에 빠르게 훑어볼 때 유용.
- `## Growth Notes`: Claude의 분석/인사이트를 별도 작성한다.
- 날것의 기록과 정리된 요약이 함께 있어야 과거를 돌아볼 때 온전하다.

**코치 피드백** (격려가 아닌 팩트 기반, Growth Notes에 작성):
- 성과가 있으면 구체적으로 인정: "API 리팩토링을 2블록 안에 끝낸 건 좋은 집중력이었습니다."
- 문제가 있으면 솔직하게: 데이터가 말하는 것을 전달
- 근거 없는 격려 금지 ("오늘도 수고하셨습니다!" 식의 기계적 칭찬 X)

### 7단계: Review 파일 생성

**경로**: `{base}/reviews/{YYYY-MM-DD}-timebox-review.md`

```markdown
# {YYYY-MM-DD} ({요일}) Timebox Review

## Big 3 Results
1. {상태} {항목} → {결과}
2. {상태} {항목} → {결과}
3. {상태} {항목} → {결과}

Success Rate: {n}/3

## Block Analysis
| Block | Plan | Actual | Match |
|-------|------|--------|-------|
| ... | ... | ... | ... |

Block Adherence: {n}%

## Energy Pattern
- Peak: {시간대}
- Low: {시간대}
- Recommendation: {내일 제안}

## Goal Alignment
- 목표 직접 기여: {n}블록 ({n}%)
- 유지/운영: {n}블록
- 예상 밖: {n}블록
- 계획을 흔든 요인: {사용자 응답 또는 데이터 기반 분석}

## Ad-hoc Interruptions
- {예상 외 작업들}

## Carry Forward
### 내일 Big 3 후보
1. {carry-over 또는 새 항목}
2. {후보}
3. {후보}

### 오픈 루프
- {완료되지 않은 진행중 작업, 대기 중인 리뷰, 블로커 등}

### Weekly Goal Progress
- W1: {목표} → {이번 주 진행률}
- W2: {목표} → {이번 주 진행률}

### Coaching Notes
- {carry-over 항목에 대한 도전: "이걸 3일째 미루고 있습니다. 정말 해야 하는 건가요, 드롭할 건가요?"}
- {패턴 기반 제안}

### Notes
{내일 참고할 메모}

## Daily One-liner
> {하루 한줄평 — 기분, 느낌, 깨달은 것}

## Reflection (원문)
{사용자가 쓴 리플렉션 원문 그대로 보존. 정리하거나 요약하지 않는다.}

## Reflection (요약)
{Claude가 원문을 읽고 핵심 포인트를 3-5줄로 정리. 나중에 빠르게 훑어볼 때 유용.}

## Growth Notes
{Claude 분석 및 인사이트 — 사용자 원문과 분리하여 별도로 작성}
```

### 8단계: 주간 리뷰 안내 (금요일/주말)

금요일 또는 주말에 실행 시:
- "`/timebox-review weekly`로 이번 주 패턴 리뷰를 해보시겠습니까?" 안내
- 주간 목표 대비 간략 진행률만 표시 (상세 분석은 `/timebox-review`에서)

### 9단계: 마무리

- Review 파일 경로 안내
- 내일 Big 3 후보 요약 (Carry Forward에서)
- 오픈 루프 리마인드
- 월간/주간 목표 대비 간략 진행상황 (있으면)

### 10단계: Git 자동 커밋 + Push

timebox base path가 git repo이면, 변경된 기록을 자동으로 커밋하고 push합니다.

1. `git -C {base} status --porcelain`으로 변경 파일 확인
2. 변경 없으면 스킵
3. 변경 있으면:
   - `git -C {base} add plans/ logs/ reviews/ goals/`
   - 커밋 메시지: `{YYYY-MM-DD} timebox — Big 3: {완료}/{전체}, {한줄 요약}`
   - `git -C {base} push`
4. remote 설정 확인: `git -C {base} remote -v`
   - SSH config에 별도 Host가 설정된 경우 (예: `personal`) 해당 Host를 사용
5. push 실패 시 에러 안내만 하고 진행 (블로커 아님)
6. "기록 저장 완료 (commit: {hash})" 안내

## 참고

- 마스터 파일: `{base}/plans/{YYYY-MM-DD}.md`
- Review 파일: `{base}/reviews/{YYYY-MM-DD}-timebox-review.md`
- 로그 경로: `{base}/logs/{YYYY-MM-DD}/`
- Energy Log가 비어있으면 에너지 분석 스킵
- **마스터 파일은 Read 후 Edit만 사용. Write 금지.**
