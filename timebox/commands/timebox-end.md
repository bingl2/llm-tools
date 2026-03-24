---
name: timebox-end
description: "타임박스 하루 마감 - Big 3 리뷰 + 에너지 패턴 분석 + 내일 준비"
category: productivity
---

# /timebox-end - 타임박스 하루 마감

오늘의 타임박스를 리뷰하고, 에너지 패턴을 분석하며, 내일을 준비합니다.

> end는 오늘과 내일을 위한 기록입니다. 패턴 분석과 시스템 피드백은 `/timebox-review`의 역할입니다.

## 경로
`$TIMEBOX_HOME` (미설정 시 `~/timebox`). 데이터 조회/생성은 `timebox` CLI를 사용한다.

## 실행 흐름

### 0단계: 체크인 루프 해제

1. CronList로 현재 활성 cron 목록 조회
2. `/timebox-loop` 프롬프트를 가진 recurring job을 찾아 CronDelete로 해제
3. "체크인 루프 해제 완료" 안내

### 1단계: 데이터 수집

1. `timebox stats today` 실행 → JSON으로 Big 3 완료율, 블록 준수율, 에너지, ad-hoc 카운트, 목표 정렬, Estimation Accuracy(예상 대비 실제 블록 배율) 확보
   - **에러(PLAN_NOT_FOUND)면**: "오늘 타임박스 파일이 없습니다." 안내 후 종료
2. 목표 데이터:
   - `timebox goals show --scope weekly` → 주간 목표 JSON (에러면 스킵)
   - `timebox goals show --scope monthly` → 월간 목표 JSON (에러면 스킵)
3. carry-over 판단: `timebox stats carry-over` → 연속 미완료 항목 확인
4. `{base}/_config.md` Read (있으면) — `github_sync` 설정 확인용 (CLI 미지원)

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
- "더 하고 싶은 말이 있으면 자유롭게 남겨주세요"로 길게 쓸 여지를 열어둠

**핵심 질문** (AskUserQuestion, 최대 1개):
- 오늘 데이터에서 가장 눈에 띄는 패턴을 짚어 질문 (예: "오전에 2블록 연속 몰입했는데, 의도적이었나요?")
- 근거 없는 일반론 질문 금지 ("어떤 점이 좋았나요?" 식 X)
- 사용자가 스킵하면 질문 없이 진행

**원문 보존 원칙**:
- `## Reflection`: 사용자가 쓴 리플렉션을 **그대로** 보존한다. 정리, 요약, 교정하지 않는다.
- 한 줄이든 한 페이지든, 날것의 기록이 가장 가치 있다.

**Coach's Notes** (격려가 아닌 팩트 기반):
- 핵심 요약: 원문에서 뽑은 포인트 2-3줄
- 패턴 연결: 이전 기록과의 연결, 반복 패턴 짚기
- When-Then: "다음에 [상황]이 오면, [행동]한다" 형식의 실행 의도 1개 (반드시 포함)
- 질문: 내일 생각해볼 질문 1개 (반드시 포함)
- 성과가 있으면 구체적으로 인정: "API 리팩토링을 2블록 안에 끝낸 건 좋은 집중력이었습니다."
- 문제가 있으면 솔직하게: 데이터가 말하는 것을 전달
- 근거 없는 격려 금지 ("오늘도 수고하셨습니다!" 식의 기계적 칭찬 X)

### 7단계: Review 파일 생성

코칭 대화에서 수집한 리뷰 데이터를 JSON으로 조립하여 CLI로 생성합니다:

```bash
echo '{
  "date": "{YYYY-MM-DD}",
  "weekday": "{요일}",
  "big3_results": [
    {"number": 1, "text": "{항목}", "status": "done", "result": "{결과}", "estimated_blocks": 2, "actual_blocks": 2}
  ],
  "success_rate": "1/3",
  "block_analysis": [
    {"block": "09:00-10:30 Deep", "plan": "{계획}", "actual": "{실제}", "match": true}
  ],
  "block_adherence": 50,
  "energy_pattern": {"peak": "{시간대}", "low": "{시간대}", "recommendation": "{제안}"},
  "goal_alignment": {"direct": 3, "maintenance": 1, "unexpected": 1, "disruptors": "{요인}"},
  "ad_hoc": ["{예상 외 작업}"],
  "carry_forward": {"tomorrow_candidates": ["{항목}"], "open_loops": ["{루프}"], "weekly_progress": ["{진행}"]},
  "carry_over_challenge": "{도전 메시지}",
  "daily_one_liner": "{한줄평}",
  "reflection": "{사용자 원문 그대로}",
  "coach_notes": "{Claude 작성 코치 노트}",
  "when_then": "{다음에 [상황]이 오면, [행동]한다}",
  "coach_question": "{내일 생각해볼 질문}"
}' | timebox review create
```

CLI가 `{base}/reviews/{YYYY-MM-DD}-timebox-review.md` 파일을 자동 생성합니다.

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

CLI로 timebox 데이터 파일을 자동 커밋합니다:

```bash
# _config.md의 github_sync가 on이면 --push 추가
timebox commit [--push]
```

- CLI가 plans/, logs/, reviews/, goals/ 변경 파일을 자동 staging + 커밋
- 변경 없으면 자동 스킵
- push 실패 시 에러 안내만 하고 진행 (블로커 아님)
- "기록 저장 완료 (commit: {hash})" 안내

## 참고

- 오늘 통계: `timebox stats today`
- 목표 조회: `timebox goals show --scope {weekly|monthly}`
- carry-over: `timebox stats carry-over`
- 리뷰 생성: `echo '{json}' | timebox review create`
- Git 커밋: `timebox commit [--push]`
- _config.md는 직접 Read (CLI 미지원)
- Energy Log가 비어있으면 에너지 분석 스킵
