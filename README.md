# Business Network Graph Agent

AI 기반 비즈니스 네트워크 관리 시스템입니다. 명함과 메모를 자동으로 분석하여 지식 그래프로 구조화하고, 자연어로 검색할 수 있습니다.

![main.png](https://cdn.discordapp.com/attachments/1466261696338460947/1467402452394442926/bde84e4697869926.png?ex=69804087&is=697eef07&hm=06d00ae87ebf989db238f51fc2d863baad0f3de7665ba9c0dd4b6360909ea2e6&)

![Image](https://github.com/user-attachments/assets/1520e6a2-71d3-4312-80f5-f9b336a9e468)

---

## 목차

1. [목적 및 개요](#목적-및-개요)
2. [주요 기능](#주요-기능)
3. [빠른 시작](#빠른-시작)
4. [사용 방법](#사용-방법)
5. [아키텍처](#아키텍처)
6. [확장 로드맵](#확장-로드맵)

---

## 목적 및 개요

### 문제 정의

비즈니스 환경(거래처/네트워크 기반 업무)에서는 다음 문제가 반복적으로 발생합니다:

- **정보의 파편화**: 명함(지갑), 회의 메모(노트/메모앱), 연락처(메신저), 거래 내역(이메일) 등으로 분산
- **맥락의 손실**: "이 사람 누구였지?", "어떤 프로젝트?", "마지막 컨택 언제?"를 확인하려면 여러 앱을 탐색해야 함
- **관계의 불투명**: "A회사와 B회사를 연결해줄 사람?", "이 거래처 라인업?" 같은 네트워크 질문에 답하기 어려움
- **검색의 비효율**: 오래된 명함/메모/거래처 히스토리 검색이 사실상 불가능에 가까움

### 페인 포인트

#### 1) 파편화된 정보 저장

- 명함 앱, 메모 앱, CRM, 이메일, 메신저 등 각 플랫폼에 정보가 분산
- 정보 간 연결고리가 없어 통합 인사이트 도출이 어려움
- "김 과장"만으로는 회사/프로젝트/만난 시점 등 맥락 파악 불가

#### 2) 수동 정리의 한계

- 명함 받을 때마다 CRM 입력 → 입력 부담으로 지속 불가
- 노트 기반 수동 링크(예: Obsidian `[[링크]]`) → 초기에만 하다가 중단
- 결과: 데이터는 쌓이지만 활용은 안 됨

#### 3) 검색의 어려움

- "작년 전시회에서 만난 삼성 사람" 같은 **복합 조건** 검색 불가
- 단순 키워드 검색만으로는 맥락(언제/어디서/누구 통해)을 회수하기 어려움
- 관계 기반 탐색("이 사람 통해 누구 소개 가능?") 불가

### 타겟 유저

**Primary**

- B2B 영업/마케팅
- 프리랜서(다수 클라이언트 관리)
- 스타트업 창업자(네트워킹 중심)
- 컨설턴트/에이전시(거래처 다수)

**Secondary**

- 투자자/VC(포트폴리오 네트워크)
- HR(후보자 네트워크)
- 이벤트 기획자(참가자/파트너)

**공통 특징**

- 월 10명+ 신규 미팅
- 명함/연락처 100개+
- 관계 기반 비즈니스 수행
- 기존 CRM은 복잡/고가로 인해 도입 장벽이 큼

### 솔루션

**핵심 컨셉**: "메모만 하면 AI가 알아서 정리해주는 지식 그래프"

**How it works**

1. **간편 입력**: 명함 사진 업로드 또는 자연어 메모
2. **자동 구조화**: 인물/회사/이벤트/관계 추출 및 그래프 형태로 저장
3. **지능형 검색**: 자연어 질문 → 즉시 답변(+근거 출처)
4. **관계 탐색(향후)**: 그래프 기반 소개 경로/연결고리 발견

**차별점**

- vs 명함 앱: 연락처 저장이 아니라 관계망/맥락까지 관리
- vs Notion/Obsidian: 수동 링크가 아니라 자동 추출/연결
- vs CRM: 필드 입력/설정 없이 자연어 기반으로 동작

### 기대효과

**비즈니스 임팩트**

- 거래처 정보 검색 시간 단축 (예: 10분 → 2분)
- 놓친 기회 감소 (예: "3개월 미컨택" 자동 리마인드 가능)
- 네트워크 활용도 증가 (연결고리/소개경로 가시화)

**사용자 경험**

- 입력 부담 감소 (CRM 양식 입력 대비)
- 한 곳에서 정보 조회 (명함/메모/관계/히스토리)
- 맥락 있는 검색 (언제/어디서/누구/무슨 건)

**장기적 가치**

- 개인 네트워크 "세컨드 브레인"
- 축적 데이터 기반 관계 인사이트 제공
- 팀 협업 도구로 확장 가능

---

## 주요 기능

### 명함 자동 인식

![htil](https://cdn.discordapp.com/attachments/1466261696338460947/1467402453799538761/hitl.png?ex=69804088&is=697eef08&hm=c7ded1eb95f6ddbfad50bf7a5093902b11d5ddb623866aee4d661a51c90c7780&)

![res](https://cdn.discordapp.com/attachments/1466261696338460947/1467402454659371049/save.png?ex=69804088&is=697eef08&hm=117a87b00f7f2d45073e5fa85a5cabf8be23f9ccb178a8765902796655c5008d&)

- 명함 사진 업로드 시 upstage_document parse로 정보 자동 추출
- 이름, 직책, 회사, 전화번호, 이메일 구조화
- **HITL**: 추출 결과 확인 후 수정 가능

### 메모 자동 분석

![memo](https://cdn.discordapp.com/attachments/1466261696338460947/1467402454277554288/inputmemo.png?ex=69804088&is=697eef08&hm=a56774f51d9469a079031b0b0d2e678cb63124bacf82493a9fc41187bbf68c4f&)

- 자연어 메모 입력 시 인물/회사/일정 자동 추출
- 시간 인식: "내일 14시" → "2026-02-02T14:00:00"
- 이름 정규화: "길동님" → "홍길동" (중복 방지)

### 자연어 검색

![search](https://cdn.discordapp.com/attachments/1466261696338460947/1467402454982197376/search_nl.png?ex=69804088&is=697eef08&hm=f8b513807fbe06dcaad5b6a24e1276f021d3208a00b554be60e9dd63ff4d538d&)

- "홍길동님과 무슨 일정이 있지?" → 관련 일정 조회
- 부분 이름 매칭: "길동" 검색 시 "홍길동" 결과 포함
- 그래프 관계 탐색: 인물-회사-프로젝트 연결

### 지식 그래프

![graph](https://cdn.discordapp.com/attachments/1466261696338460947/1467402453417984051/graph_res.png?ex=69804087&is=697eef07&hm=1115cd36c30e8aaaeeb159509fe3d30b47d7f812c72a67ff7c8244c298a985ad&)

- Neo4j 기반 그래프 데이터베이스
- 노드: Person, Company, Event, Project, Memo
- 관계: WORKS_AT, ATTENDED, DISCUSSED, MENTIONED_IN

---

## 빠른 시작

### 1. 환경 변수 설정

`.env` 파일을 생성하고 API 키를 입력하세요:

```bash
# Upstage API (필수)
UPSTAGE_API_KEY=your_api_key_here

# Neo4j (기본값 사용 가능)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LangSmith (선택사항 - 디버깅용)
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_langsmith_project_name
LANGCHAIN_TRACING_V2=true
```

### 2. Docker Compose로 실행

```bash
# 전체 서비스 시작 (Neo4j + Backend + Frontend)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 3. 접속

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Neo4j 브라우저**: http://localhost:7474

---

## 사용 방법

### 명함 등록

1. 채팅 화면에서 📷 버튼 클릭
2. 명함 사진 선택
3. 추출된 정보 확인
4. **✅ 확인** 또는 **✏️ 수정** 선택

### 메모 작성

채팅 입력창에 자연어로 입력:

```
내일 길동님과 14시 프로젝트 미팅
```

→ 자동으로 Person(홍길동), Event(프로젝트 미팅, 2026-02-02T14:00:00) 생성

### 정보 검색

채팅 입력창에 질문 입력:

```
홍길동님 전화번호?
홍길동님과 무슨 일정이 있지?
ABC상사에 누가 있지?
```

→ Neo4j 그래프 검색 후 자연어 응답 반환

---

## 아키텍처

### 기술 스택

| 레이어            | 기술                  | 용도         |
| ----------------- | --------------------- | ------------ |
| **Frontend**      | React 18 + TypeScript | SPA UI       |
| **Backend**       | FastAPI + Python 3.12 | REST API     |
| **AI/ML**         | Upstage Solar Pro 3   | 한국어 LLM   |
|                   | Document Parse API    | 명함 OCR     |
| **Database**      | Neo4j 5.15            | 그래프 DB    |
| **Observability** | LangSmith             | LLM 트레이싱 |
| **Infra**         | Docker Compose        | 컨테이너     |

### 디렉토리 구조

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 엔트리포인트
│   │   ├── api/
│   │   │   └── routes.py        # API 엔드포인트
│   │   ├── services/
│   │   │   ├── neo4j_service.py # Neo4j 연동
│   │   │   └── upstage.py       # Upstage API 연동
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic 스키마
│   │   └── core/
│   │       ├── config.py
│   │       └── logger.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # 메인 컴포넌트
│   │   └── App.css              # 스타일
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env                         # 환경 변수 (생성 필요)
└── README.md
```

### 데이터 플로우

#### 명함 처리

```
명함 업로드 → Document Parse (OCR) → Solar Pro (구조화)
→ 사용자 확인 (HITL) → Neo4j 저장
```

#### 메모 처리

```
자연어 입력 → Solar Pro (엔티티 추출) → 이름 정규화
→ Neo4j 저장 (노드 + 관계)
```

#### 검색 처리

```
자연어 질문 → Solar Pro (Cypher 생성) → Neo4j 실행
→ Solar Pro (자연어 응답) → 사용자
```

---

## API 엔드포인트

### 명함 관련

```http
POST /api/extract-business-card
Content-Type: multipart/form-data

파일: 명함 이미지 (JPG, PNG)
응답: { person_data, company_data }
```

```http
POST /api/save-contact
Content-Type: application/json

{ "person_data": {...}, "company_data": {...} }
응답: { "status": "Contact successfully saved" }
```

### 메모 관련

```http
POST /api/memo
Content-Type: application/json

{ "text": "내일 홍길동님과 14시 미팅" }
응답: { "status": "Memo processed", "extracted_data": {...} }
```

### 검색

```http
POST /api/query
Content-Type: application/json

{ "question": "홍길동님 전화번호?" }
응답: { "answer": "...", "query_results": [...], "cypher_query": "..." }
```

### 기타

```http
GET /api/memos
응답: { "success": true, "data": [...] }

GET /health
응답: { "status": "ok" }
```

---

## 🗄️ Neo4j 스키마

### 노드

```cypher
(:Person {name, title, phone, email})
(:Company {name})
(:Event {name, date})
(:Project {name})
(:Memo {id, text, timestamp, business_related})
```

### 관계

```cypher
(Person)-[:WORKS_AT]->(Company)
(Person)-[:ATTENDED]->(Event)
(Person)-[:MENTIONED_IN]->(Memo)
(Company)-[:MENTIONED_IN]->(Memo)
(Event)-[:DISCUSSED]->(Project)
(Person)-[:INTRODUCED_BY]->(Person)
```

### 쿼리 예시

```cypher
-- 특정 인물 검색
MATCH (p:Person) WHERE p.name CONTAINS "홍길동" RETURN p;

-- 인물의 일정 조회
MATCH (p:Person)-[:ATTENDED]->(e:Event)
WHERE p.name CONTAINS "홍길동"
RETURN e.name, e.date ORDER BY e.date;

-- 회사 소속 인원 조회
MATCH (p:Person)-[:WORKS_AT]->(c:Company {name:"ABC상사"})
RETURN p.name, p.title;
```

---

## 개발 가이드

### 로컬 개발 환경

```bash
# Backend 개발
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend 개발
cd frontend
npm install
npm run dev

# Neo4j (Docker)
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.15
```

### 테스트

```bash
# API 테스트
curl -X POST http://localhost:8000/api/memo \
  -H "Content-Type: application/json" \
  -d '{"text": "내일 홍길동님과 15시 회의"}'

# 검색 테스트
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "홍길동님 전화번호?"}'
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f neo4j
```

---

## 트러블슈팅

### Neo4j 연결 실패

```bash
# Neo4j 상태 확인
docker-compose ps neo4j

# 재시작
docker-compose restart neo4j

# 로그 확인
docker-compose logs neo4j
```

### Upstage API 오류

```bash
# .env 파일 확인
cat .env | grep UPSTAGE_API_KEY

# API 키 유효성 확인
curl -H "Authorization: Bearer $UPSTAGE_API_KEY" \
  https://api.upstage.ai/v1/solar/chat/completions
```

### Frontend 빌드 오류

```bash
# 캐시 삭제 후 재빌드
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

---

## 주요 기능 상세

### 1. 이름 정규화

중복 노드 방지를 위해 부분 이름을 자동으로 매칭:

- "길동님" → "홍길동"
- "성재" → "안성재"

**동작 원리**:

1. 메모에서 "길동님" 추출
2. Neo4j에서 유사한 이름 검색
3. "홍길동" (연락처 있음) 발견
4. "홍길동"으로 노드/관계 생성

### 2. 시간 인식

한국어 상대 시간을 절대 시간으로 변환:

| 입력            | 변환 결과             |
| --------------- | --------------------- |
| "내일 14시"     | "2026-02-02T14:00:00" |
| "오늘 오후 3시" | "2026-02-01T15:00:00" |
| "다음주 월요일" | (계산된 날짜)         |

### 3. 부분 매칭 검색

Cypher의 `CONTAINS` 연산자로 유연한 검색:

```cypher
-- "길동" 검색 시 "홍길동", "김길동" 모두 매칭
MATCH (p:Person) WHERE p.name CONTAINS "길동" RETURN p;
```

---

## 미구현 리스트

1. **그래프 시각화**: MVP에는 미포함 (v0.2 예정)
2. **인증/권한**: 단일 사용자 환경 (멀티테넌시 미지원)
3. **성능**: LLM API 레이턴시로 인해 응답 3-7초 소요
4. **명함 이미지**: 원본 이미지 저장 미구현

---

## 확장 로드맵

### v0.2 - 회의록 통합

**목표**: 음성 회의록 자동 처리 및 그래프 연결

- [ ] Whisper API를 통한 음성 → 텍스트 변환
- [ ] Speaker diarization (화자 분리)
- [ ] 회의 참석자 자동 인식 및 그래프 연결
- [ ] 회의록에서 핵심 논의사항/액션아이템 추출
- [ ] 회의록 Memo 노드로 저장

**예상 효과**: 1시간 회의 → 5분 내 요약 + 그래프 자동 업데이트

---

### v0.3 - 인맥 관리 (소셜 네트워크)

**목표**: 외부 플랫폼 연동으로 네트워크 정보 풍부화

- [ ] LinkedIn 연동
  - 프로필 정보 자동 동기화
  - 공동 연결고리(mutual connections) 발견
  - 경력 이력 자동 업데이트
- [ ] 인맥 관계 강도 계산 (마지막 컨택 일자, 상호작용 빈도)
- [ ] 소개 경로 탐색 (A → B → C 최단 경로)

**예상 효과**: "김 과장 통해 삼성 담당자 소개 가능" 자동 발견

---

### v0.4 - 사내 문서 통합

**목표**: 이메일/문서에서 자동으로 비즈니스 관계 추출

- [ ] 이메일 자동 처리 (Gmail/Outlook API)
  - 발신자/수신자 자동 등록
  - 이메일 스레드 → 프로젝트 연결
  - 중요 이메일 자동 분류 (계약/견적/문의)
- [ ] 문서 파싱 (PDF, PPTX, DOCX)
  - 계약서에서 거래처/날짜/금액 추출
  - 제안서에서 프로젝트 정보 추출
- [ ] 첨부파일 연결 (문서 → 인물/회사/프로젝트)

**예상 효과**: 이메일함 자동 분석 → 1000+ 거래처 관계 자동 구축

---

### v0.5 - 태스크 & 투두 관리

**목표**: 비즈니스 관계와 연결된 액션 아이템 관리

- [ ] 메모에서 TODO 자동 추출
  - "김 과장에게 견적서 보내기" → TODO 노드 생성
  - 담당자/마감일 자동 인식
- [ ] 리마인더 기능
  - "3개월 미컨택 인물" 알림
  - "마감일 임박 태스크" 알림
- [ ] 그래프 기반 태스크 우선순위
  - 중요 거래처 관련 태스크 우선 표시

**예상 효과**: "잊고 있던 중요한 팔로업" 자동 리마인드

---

### v0.6 - 멀티 채널 지원

**목표**: 다양한 입력 채널에서 정보 수집

- [ ] Slack 봇
  - 채널/DM에서 자동 메모 수집
  - 멘션된 인물/회사 자동 추출
- [ ] KakaoTalk 연동
  - 대화 내용 자동 메모화
  - 비즈니스 관련 대화만 필터링
- [ ] 브라우저 확장 프로그램
  - LinkedIn 프로필 → 원클릭 저장
  - 웹사이트에서 회사 정보 추출

**예상 효과**: "메모 잊어버림" 방지 - 어디서든 자동 수집

---

### 크리티컬 확장 (장기)

#### 1. 관계 강도 시각화

- 그래프 노드 크기/색상으로 중요도 표시
- "최근 3개월 미컨택" 노드 하이라이트
- 관계 유형별 필터링 (거래처/파트너/지인)

#### 2. 인트로 경로 자동 추천

- "A회사 담당자 만나고 싶음" → "B님 통해 소개 가능" 자동 제안
- 최단 경로 + 관계 강도 기반 최적 경로

#### 3. CRM 동기화

- Salesforce, HubSpot 양방향 동기화
- 기존 CRM 데이터 → 그래프 자동 임포트
- 그래프 업데이트 → CRM 자동 반영

#### 4. 팀 협업 모드

- 멀티 테넌시 (회사/팀 단위)
- 인물 정보 공유 (중복 제거)
- 권한 관리 (개인 메모 vs 팀 공유)

#### 5. 지능형 인사이트

- "이번 달 주요 거래처 TOP 5" 자동 리포트
- "네트워크 확장 추천" (같은 회사 다른 부서)
- "관계망 공백 지역" 발견 (예: 제조업 네트워크 부족)

---

### 참고: MVP (v0.1) 완료 항목

현재 구현 완료된 기능:

- ✅ 명함 OCR (Document Parse API)
- ✅ 메모 자동 분석 (엔티티 추출, 시간 인식)
- ✅ 자연어 검색 (Cypher 생성)
- ✅ 이름 정규화 (중복 방지)
- ✅ Neo4j 그래프 데이터베이스
- ✅ HITL (명함 확인/수정)
- ✅ LangSmith 트레이싱

---

## 라이선스

MIT License

---

## 문의

이슈가 있으시면 GitHub Issues에 등록해주세요.

---

**Built with ❤️ using Upstage Solar Pro**
