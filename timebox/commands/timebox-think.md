---
name: timebox-think
description: "생각 캡처 — 날것의 브레인덤프를 Foundation 기반으로 정제하고 옵시디언에 저장"
category: productivity
---

# /timebox-think - 생각 캡처

순간적으로 떠오르는 생각, 감정, 영감, 관찰을 즉시 캡처합니다. 원문을 보존하고, Foundation을 거울삼아 코칭 피드백을 생성하여 옵시디언 노트로 저장합니다.

## 경로
`$TIMEBOX_HOME` (미설정 시 `~/timebox`). 데이터 조회/생성은 `timebox` CLI를 사용한다.

## 시간대 (Timezone)
- `_config.md`의 `timezone` 값 기준으로 날짜/시각을 판단한다 (기본값: `Asia/Seoul`).

## 핵심 철학

- **즉시성**: 생각은 휘발된다. 입력 받으면 곧바로 처리한다. 긴 질문 없이 빠르게.
- **원문 보존**: 사용자의 Raw Dump는 한 글자도 수정/교정/요약하지 않는다. 날것이 가장 가치 있다.
- **거울 효과**: 뻔한 위로나 일반론을 금지한다. Foundation에 명시된 사용자의 현재 가치관과 목표를 기반으로 객관적 피드백을 제공한다.
- **주제 범용성**: 업무, 미디어 감상, 철학적 고민, 일상 관찰 — 어떤 주제든 결에 맞춰 자연스럽게 응답한다.

## 실행 흐름

### 1단계: 컨텍스트 로드

1. `{base}/goals/{올해}-foundation.md` Read (있으면) — 방향, 가치관, 자기 지식 로드
2. `{base}/_config.md` Read (있으면) — `obsidian_vault` 설정 확인
3. (Optional) 최근 로그 확인: `timebox think list --date {오늘}` 실행 → 오늘 이미 남긴 think가 있으면 맥락 참고
4. (Optional) 현재 블록 확인: `timebox now` 실행 → 에러가 아니면 현재 시간 블록 맥락을 참고 (에러면 무시, timebox plan 없이도 동작)

**Foundation이 없는 경우:**
- Foundation 없이도 동작한다. 코칭 피드백에서 Foundation 기반 교차 분석을 스킵하고, 사용자의 생각 자체에 집중한 피드백을 제공한다.
- "Foundation을 설정하면 더 깊은 코칭이 가능합니다. `/timebox-align`으로 설정하시겠습니까?" 한 줄 안내.

### 2단계: 브레인덤프 수용

**사용자가 이미 텍스트를 함께 입력한 경우** (예: `/timebox-think "오늘 코드 리뷰에서..."`) → 3단계로 바로 진행.

**텍스트 없이 호출한 경우:**
- "무슨 생각이 드셨나요? 자유롭게 쏟아내주세요."
- AskUserQuestion 1번만. 추가 질문하지 않는다. 받은 그대로 처리한다.

### 3단계: 분석 + 노트 생성

Claude가 사용자의 Raw Dump를 분석하여 마크다운 노트를 생성한다.

**분석 과정 (내부, 사용자에게 노출하지 않음):**
1. 상황/계기 파악: 무엇이 이 생각을 촉발했는가?
2. 핵심 인지 추출: 감정인가, 관찰인가, 깨달음인가, 고민인가?
3. 키워드 2-3개 추출: 나중에 검색/필터에 사용할 태그
4. 감정 톤 판별: mood 이모지 + 영문 단어 1개
5. short_name 생성: 핵심을 담은 영문 kebab-case 3-5단어 (예: `code-review-frustration`, `leadership-debt-insight`)

**Foundation 교차 분석 (Foundation이 있을 때만):**
- 사용자의 현재 방향/목표와 이 생각이 어떻게 연결되는지
- 자기 지식(에너지 패턴, 회피 트리거 등)에 비추어 볼 때 이 생각의 의미
- Foundation의 톤과 결에 맞춘 코칭 (Foundation이 성장 지향이면 성장 관점, 안정 지향이면 안정 관점)

**코칭 톤 원칙:**
- 무조건적 위로 금지. "힘드셨겠네요"로 끝내지 않는다.
- 무조건적 비판 금지. 감정을 부정하지 않는다.
- Foundation에 적힌 사용자의 현재 다짐과 목표를 **거울처럼** 비춘다.
- "당신이 세운 원칙에 비추어 보면..." / "이 상황에서 당신의 [Foundation 항목]은..." 식으로 연결한다.
- Foundation이 없으면 사용자의 생각 자체의 논리와 감정을 정제하여 되비춘다.

### 4단계: 파일 저장

생성된 마크다운을 CLI로 저장한다.

**저장 방법:**

```bash
cat <<'THINK_EOF' | timebox think create --time {HH:MM} --name {short_name}
{생성된 마크다운 전체}
THINK_EOF
```

**마크다운 출력 포맷 (정확히 이 템플릿을 따른다):**

```markdown
---
date: {YYYY-MM-DD HH:mm}
tags: [think-log, {키워드1}, {키워드2}]
mood: {이모지}{영문단어} (예: 🤔reflective, 😤frustrated, 💡inspired, 😊grateful, 🔥motivated)
---

## 🧠 정제된 생각 (Refined Summary)
* (상황/계기): {Raw Dump에서 파악한 객관적 상황 1줄}
* (핵심 인지): {감정이나 생각의 본질 1줄}

---

## 🗣️ 생생한 기록 (Raw Dump)
{사용자가 입력한 내용 원문 그대로. 한 글자도 수정하지 않는다.}

---

## 💡 멘토의 코칭 & 피드백
**[코칭 피드백]**
{Foundation 맥락과 Raw Dump를 교차 분석한 통찰 피드백. 3문장 이내.}

**[생각의 확장]**
{인지의 틀을 깨거나 다음 단계로 넘어가게 하는 건설적인 질문 1개}

**[다음 액션 아이템]**
* [ ] {오늘 당장 적용할 수 있는 작고 구체적인 실천 행동 1개}
```

### 5단계: 완료 안내

1. 저장된 파일 경로를 안내한다
2. 정제된 생각 요약 (Refined Summary)을 보여준다
3. **옵시디언 연동** (`_config.md`의 `obsidian_vault: on`일 때):
   - **데일리 노트에 백링크 추가**: `obsidian daily:append content="- [[{YYYYMMDD}-{HHMM}-{short_name}]]"` 실행
     - Obsidian CLI가 없으면(에러 시) 스킵하고 안내: "Obsidian CLI를 설치하면 데일리 노트에 자동 링크됩니다."
   - **노트 열기**: `open "obsidian://open?vault={vault_name}&file=thinks/{YYYY-MM-DD}/{filename_without_ext}"` 실행
     - vault 이름은 `$TIMEBOX_HOME` 폴더명에서 추출 (예: `~/timebox` → `timebox`)
   - "옵시디언에서 노트를 열었습니다." 안내
4. 끝. 추가 질문하지 않는다.

## 참고사항

- think 생성: `cat <<'EOF' | timebox think create --time HH:MM --name short-name`에 stdin으로 마크다운 전달
- think 조회: `timebox think show [--date YYYY-MM-DD] [--name short-name]`
- think 목록: `timebox think list [--date YYYY-MM-DD] [--from YYYY-MM-DD --to YYYY-MM-DD]`
- foundation.md, _config.md는 직접 Read (CLI 미지원)
- **timebox plan 없이도 동작한다.** think는 독립적이다.
- **Raw Dump 원문은 절대 수정하지 않는다.** 오탈자, 비문, 구어체 전부 그대로 보존.
- short_name은 영문 kebab-case, 3-5단어, ASCII만 사용 (예: `morning-energy-reflection`)
- tags의 첫 번째 항목은 항상 `think-log` (고정). 나머지 2-3개는 AI가 추출한 키워드.
- 코칭 피드백에서 일반론("열심히 하세요", "괜찮아요")은 금지. Foundation 또는 사용자 원문에 근거한 피드백만.
- 이 스킬은 **기록에 집중**한다. 길게 대화하지 않는다. 받고 → 정제하고 → 저장하고 → 끝.
- **Obsidian CLI** (`obsidian` 명령): 데일리 노트 백링크 추가, 검색 등에 사용. 없어도 동작하며, 있으면 더 풍부한 연동 제공.
  - 데일리 노트 링크: `obsidian daily:append content="- [[filename]]"`
  - 검색: `obsidian search query="tag:#think-log"`
  - 설치: Obsidian 앱 → Settings → General → Command line interface 활성화
