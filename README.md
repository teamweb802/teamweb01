# 인천 문화·관광 웹사이트 (teamweb01)

인천의 문화/관광 정보를 소개하는 팀 프로젝트입니다.  
현재는 **프론트엔드(정적 페이지) 중심으로 구현**되어 있으며, 추후 **백엔드 연동을 포함한 풀스택 프로젝트**로 확장할 예정입니다.

- Repository: `teamweb802/teamweb01`
- 배포 주소: `https://teamweb802.github.io/teamweb01/`
- Project Type: Team Project (Web Publishing → Fullstack 확장 예정)
- Current Status: ✅ Frontend MVP 완료 / 🔄 Backend 기획·연동 예정

---

## 프로젝트 개요

본 프로젝트는 인천시 관련 정보를 주제별로 탐색할 수 있도록 구성한 웹사이트입니다.

- 메인 랜딩 페이지
- 5개 대분류 × 각 3개 서브페이지
- 공지사항(목록/상세/등록 UI)
- 회원 안내(로그인/약관/회원가입)
- 정책 페이지(개인정보처리방침/저작권보호정책)

---

## 주요 기능 (Frontend)

- 공통 헤더/푸터 및 드롭다운 GNB 메뉴
- 메인 비주얼 섹션(라디오 버튼 기반 슬라이드 UI)
- 카테고리별 정보 페이지 구성
- 공지사항 UI
  - 목록(`board.html`)
  - 상세(`board_detail.html`)
  - 등록 폼(`board_form.html`)
- 회원 플로우 UI
  - 로그인(`login.html`)
  - 이용약관(`terms.html`)
  - 회원가입(`join.html`)
- 정책 페이지
  - 개인정보처리방침(`privacy.html`)
  - 저작권보호정책(`copyright.html`)

---

## 페이지 구성

### 1) 메인
- `index.html` : 메인 화면

### 2) 인천 안내
- `sub11.html` : 소개
- `sub12.html` : 캐릭터
- `sub13.html` : 시목/시화/시조

### 3) 테마여행
- `sub21.html` : 역사문화
- `sub22.html` : 휴양관광
- `sub23.html` : 박물관/기념관

### 4) 문화관광
- `sub31.html` : 문화행사
- `sub32.html` : 문화공간
- `sub33.html` : 문화체험

### 5) 길라잡이(교통)
- `sub41.html` : 도시철도
- `sub42.html` : 인천공항
- `sub43.html` : 시외버스

### 6) 맛집·숙박·쇼핑
- `sub51.html` : 인천의 맛
- `sub52.html` : 숙박시설
- `sub53.html` : 시장/쇼핑

### 7) 회원/게시판/정책
- `login.html` : 로그인
- `terms.html` : 이용약관 동의
- `join.html` : 회원가입
- `board.html` : 공지사항 목록
- `board_detail.html` : 공지사항 상세
- `board_form.html` : 공지사항 등록 폼
- `privacy.html` : 개인정보처리방침
- `copyright.html` : 저작권보호정책

---

## 기술 스택

- **HTML5**
- **CSS**
- **JavaScript** (약관 동의 체크 등 최소 스크립트)
- **Git / GitHub Pages**

> 현재는 빌드 툴 없이 동작하는 정적 웹 구조입니다.

---

## 디렉터리 구조

```text
teamweb01/
├─ index.html
├─ sub11.html ~ sub53.html
├─ board.html
├─ board_detail.html
├─ board_form.html
├─ login.html
├─ terms.html
├─ join.html
├─ privacy.html
├─ copyright.html
│
├─ common.css
├─ reset.css
├─ fonts.css
├─ main.css
├─ main2.css
├─ vs.css
├─ *common.css (페이지별 스타일)
│
└─ image/
   ├─ index/
   ├─ sub11/ ~ sub53/
   ├─ icon/
   ├─ copyright/
   └─ ...
```

---

## 현재 상태 및 범위

현재 구현은 퍼블리싱 중심의 정적 구조이며, 핵심 화면 및 UI 동작을 중심으로 구성되어 있습니다.

---

## 백엔드 확장 계획 (Fullstack Roadmap)

### 1) 인증/회원
- 회원가입, 로그인, 로그아웃
- 비밀번호 암호화
- 세션 또는 JWT 기반 인증

### 2) 게시판
- 공지사항 CRUD
- 조회수 증가 로직
- 파일 첨부(선택)

### 3) 콘텐츠 관리
- 카테고리별 데이터 API화
- 관리자 페이지(게시글/콘텐츠 관리)

### 4) 데이터베이스
- **PostgreSQL** 사용 예정

