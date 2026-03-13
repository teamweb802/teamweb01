from pathlib import Path
import re

ROOT = Path('.')


def write(rel_path: str, content: str):
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


SECURITY_CONFIG = '''
package com.example.tour.config;

import com.example.tour.service.MemberService;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

    private final MemberService memberService;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(
                                "/", "/error",
                                "/member/login", "/member/terms", "/member/join", "/member/check-id",
                                "/policy/**", "/spot/**",
                                "/notice/list", "/notice/detail/**",
                                "/css/**", "/js/**", "/images/**", "/fonts/**"
                        ).permitAll()
                        .requestMatchers(
                                "/notice/write", "/notice/edit/**", "/notice/delete/**"
                        ).hasRole("ADMIN")
                        .requestMatchers(
                                "/review/list", "/review/detail/**",
                                "/review/write", "/review/edit/**", "/review/delete/**",
                                "/member/mypage", "/uploads/**"
                        ).authenticated()
                        .requestMatchers("/member/manage").hasRole("ADMIN")
                        .anyRequest().authenticated()
                )
                .formLogin(form -> form
                        .loginPage("/member/login")
                        .loginProcessingUrl("/login")
                        .usernameParameter("id")
                        .passwordParameter("pw")
                        .defaultSuccessUrl("/", true)
                        .permitAll()
                )
                .logout(logout -> logout
                        .logoutUrl("/logout")
                        .logoutSuccessUrl("/member/login")
                );

        return http.build();
    }

    @Bean
    public UserDetailsService userDetailsService() {
        return loginId -> {
            var member = memberService.findByLoginId(loginId);
            return User.builder()
                    .username(member.getLoginId())
                    .password(member.getPasswordHash())
                    .roles(member.getRole().name())
                    .build();
        };
    }
}
'''

NOTICE_API_CONTROLLER = '''
package com.example.tour.controller;

import com.example.tour.domain.Member;
import com.example.tour.dto.NoticeDetailDto;
import com.example.tour.dto.NoticeFormDto;
import com.example.tour.dto.NoticeListDto;
import com.example.tour.service.MemberService;
import com.example.tour.service.NoticeService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Collections;
import java.util.List;

@Controller
@RequiredArgsConstructor
@RequestMapping("/notice")
public class NoticeApiController {

    private static final int PAGE_SIZE = 8;

    private final NoticeService noticeService;
    private final MemberService memberService;

    private void addAuthInfo(Model model, Authentication authentication) {
        boolean isLogin = authentication != null
                && authentication.isAuthenticated()
                && !(authentication instanceof AnonymousAuthenticationToken);

        boolean isAdmin = isLogin && authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        model.addAttribute("isLogin", isLogin);
        model.addAttribute("isAdmin", isAdmin);
        model.addAttribute("loginId", isLogin ? authentication.getName() : null);
    }

    @GetMapping("/list")
    public String list(Model model,
                       @RequestParam(required = false) String type,
                       @RequestParam(required = false) String keyword,
                       @RequestParam(defaultValue = "0") int page,
                       Authentication authentication) {

        List<NoticeListDto> allBoards = (keyword != null && !keyword.isBlank())
                ? noticeService.search(type, keyword)
                : noticeService.getList();

        int totalCount = allBoards.size();
        int totalPages = totalCount == 0 ? 1 : (int) Math.ceil((double) totalCount / PAGE_SIZE);
        int currentPage = Math.max(0, Math.min(page, totalPages - 1));
        int start = currentPage * PAGE_SIZE;
        int end = Math.min(start + PAGE_SIZE, totalCount);
        List<NoticeListDto> boards = totalCount == 0 ? Collections.emptyList() : allBoards.subList(start, end);

        model.addAttribute("boards", boards);
        model.addAttribute("currentPage", currentPage);
        model.addAttribute("totalPages", totalPages);
        model.addAttribute("type", type);
        model.addAttribute("keyword", keyword);
        addAuthInfo(model, authentication);
        return "notice/list";
    }

    @GetMapping("/detail/{id}")
    public String detail(@PathVariable Long id, Model model, Authentication authentication) {
        model.addAttribute("board", noticeService.getDetail(id));
        addAuthInfo(model, authentication);
        return "notice/detail";
    }

    @GetMapping("/write")
    public String writeForm(Model model, Authentication authentication) {
        model.addAttribute("boardForm", new NoticeFormDto());
        model.addAttribute("authorName", authentication.getName());
        addAuthInfo(model, authentication);
        return "notice/form";
    }

    @PostMapping("/write")
    public String write(@ModelAttribute NoticeFormDto dto,
                        @RequestParam(value = "newsfile", required = false) MultipartFile[] files,
                        Authentication authentication) throws Exception {
        Member member = memberService.findByLoginId(authentication.getName());
        Long id = noticeService.create(dto, member.getId(), files);
        return "redirect:/notice/detail/" + id;
    }

    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model, Authentication authentication) {
        NoticeDetailDto board = noticeService.getDetail(id);
        NoticeFormDto boardForm = new NoticeFormDto();
        boardForm.setId(board.getId());
        boardForm.setTitle(board.getTitle());
        boardForm.setContent(board.getContent());

        model.addAttribute("boardForm", boardForm);
        model.addAttribute("authorName", board.getAuthor());
        addAuthInfo(model, authentication);
        return "notice/form";
    }

    @PostMapping("/edit/{id}")
    public String edit(@PathVariable Long id,
                       @ModelAttribute NoticeFormDto dto,
                       @RequestParam(value = "newsfile", required = false) MultipartFile[] files) throws Exception {
        noticeService.update(id, dto, files);
        return "redirect:/notice/detail/" + id;
    }

    @PostMapping("/delete/{id}")
    public String delete(@PathVariable Long id) {
        noticeService.delete(id);
        return "redirect:/notice/list";
    }
}
'''

REVIEW_CONTROLLER = '''
package com.example.tour.controller;

import com.example.tour.domain.Member;
import com.example.tour.dto.NoticeDetailDto;
import com.example.tour.dto.NoticeFormDto;
import com.example.tour.dto.NoticeListDto;
import com.example.tour.service.MemberService;
import com.example.tour.service.ReviewService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Collections;
import java.util.List;

@Controller
@RequiredArgsConstructor
@RequestMapping("/review")
public class ReviewController {

    private static final int PAGE_SIZE = 8;

    private final ReviewService reviewService;
    private final MemberService memberService;

    @GetMapping("/list")
    public String list(Model model,
                       @RequestParam(required = false) String type,
                       @RequestParam(required = false) String keyword,
                       @RequestParam(defaultValue = "0") int page) {

        List<NoticeListDto> allBoards = (keyword != null && !keyword.isBlank())
                ? reviewService.search(type, keyword)
                : reviewService.getList();

        int totalCount = allBoards.size();
        int totalPages = totalCount == 0 ? 1 : (int) Math.ceil((double) totalCount / PAGE_SIZE);
        int currentPage = Math.max(0, Math.min(page, totalPages - 1));
        int start = currentPage * PAGE_SIZE;
        int end = Math.min(start + PAGE_SIZE, totalCount);
        List<NoticeListDto> boards = totalCount == 0 ? Collections.emptyList() : allBoards.subList(start, end);

        model.addAttribute("boards", boards);
        model.addAttribute("currentPage", currentPage);
        model.addAttribute("totalPages", totalPages);
        model.addAttribute("type", type);
        model.addAttribute("keyword", keyword);
        return "review/list";
    }

    @GetMapping("/detail/{id}")
    public String detail(@PathVariable Long id, Model model, Authentication authentication) {
        model.addAttribute("board", reviewService.getDetail(id));
        model.addAttribute("isOwner", authentication != null && reviewService.isOwner(id, authentication.getName()));
        return "review/detail";
    }

    @GetMapping("/write")
    public String writeForm(Model model, Authentication authentication) {
        model.addAttribute("boardForm", new NoticeFormDto());
        model.addAttribute("authorName", authentication.getName());
        return "review/form";
    }

    @PostMapping("/write")
    public String write(@ModelAttribute NoticeFormDto dto,
                        @RequestParam(value = "newsfile", required = false) MultipartFile[] files,
                        Authentication authentication) throws Exception {
        Member member = memberService.findByLoginId(authentication.getName());
        Long id = reviewService.create(dto, member.getId(), files);
        return "redirect:/review/detail/" + id;
    }

    @GetMapping("/edit/{id}")
    public String editForm(@PathVariable Long id, Model model, Authentication authentication) {
        NoticeDetailDto board = reviewService.getDetail(id);
        NoticeFormDto boardForm = new NoticeFormDto();
        boardForm.setId(board.getId());
        boardForm.setTitle(board.getTitle());
        boardForm.setContent(board.getContent());

        model.addAttribute("boardForm", boardForm);
        model.addAttribute("authorName", board.getAuthor());
        model.addAttribute("isOwner", reviewService.isOwner(id, authentication.getName()));
        return "review/form";
    }

    @PostMapping("/edit/{id}")
    public String edit(@PathVariable Long id,
                       @ModelAttribute NoticeFormDto dto,
                       @RequestParam(value = "newsfile", required = false) MultipartFile[] files,
                       Authentication authentication) throws Exception {
        reviewService.update(id, dto, files, authentication.getName(), authentication);
        return "redirect:/review/detail/" + id;
    }

    @PostMapping("/delete/{id}")
    public String delete(@PathVariable Long id, Authentication authentication) {
        reviewService.delete(id, authentication.getName(), authentication);
        return "redirect:/review/list";
    }
}
'''

COMMON_HEADER = '''
<header id="hd">
    <div class="container">
        <h1 class="logo">
            <a th:href="@{/}">
                <img th:src="@{/images/logo.png}" src="/images/logo.png" alt="LOGO">
            </a>
        </h1>
        <nav class="gnb">
            <ul class="menu">
                <li>
                    <a th:href="@{/spot/sub11}" href="/spot/sub11" class="dp1">인천 안내</a>
                    <ul class="sub">
                        <li><a th:href="@{/spot/sub11}" href="/spot/sub11">소개</a></li>
                        <li><a th:href="@{/spot/sub12}" href="/spot/sub12">캐릭터</a></li>
                        <li><a th:href="@{/spot/sub13}" href="/spot/sub13">시목/시화/시조</a></li>
                    </ul>
                </li>
                <li>
                    <a th:href="@{/spot/sub21}" href="/spot/sub21" class="dp1">테마여행</a>
                    <ul class="sub">
                        <li><a th:href="@{/spot/sub21}" href="/spot/sub21">역사문화</a></li>
                        <li><a th:href="@{/spot/sub22}" href="/spot/sub22">휴양관광</a></li>
                        <li><a th:href="@{/spot/sub23}" href="/spot/sub23">박물관/기념관</a></li>
                    </ul>
                </li>
                <li>
                    <a th:href="@{/spot/sub31}" href="/spot/sub31" class="dp1">문화관광</a>
                    <ul class="sub">
                        <li><a th:href="@{/spot/sub31}" href="/spot/sub31">문화행사</a></li>
                        <li><a th:href="@{/spot/sub32}" href="/spot/sub32">문화공간</a></li>
                        <li><a th:href="@{/spot/sub33}" href="/spot/sub33">문화체험</a></li>
                    </ul>
                </li>
                <li>
                    <a th:href="@{/spot/sub41}" href="/spot/sub41" class="dp1">길라잡이</a>
                    <ul class="sub">
                        <li><a th:href="@{/spot/sub41}" href="/spot/sub41">도시철도</a></li>
                        <li><a th:href="@{/spot/sub42}" href="/spot/sub42">인천공항</a></li>
                        <li><a th:href="@{/spot/sub43}" href="/spot/sub43">시외버스</a></li>
                    </ul>
                </li>
                <li>
                    <a th:href="@{/spot/sub51}" href="/spot/sub51" class="dp1">맛집 숙박 쇼핑</a>
                    <ul class="sub">
                        <li><a th:href="@{/spot/sub51}" href="/spot/sub51">인천의 맛</a></li>
                        <li><a th:href="@{/spot/sub52}" href="/spot/sub52">숙박시설</a></li>
                        <li><a th:href="@{/spot/sub53}" href="/spot/sub53">시장/쇼핑</a></li>
                    </ul>
                </li>
            </ul>
        </nav>
        <div class="tnb">
            <th:block th:if="${!isLogin}">
                <a th:href="@{/member/login}" href="/member/login">로그인</a>
                <a th:href="@{/member/terms}" href="/member/terms">회원가입</a>
                <a th:href="@{/notice/list}" href="/notice/list">게시판</a>
            </th:block>
            <th:block th:if="${isLogin and !isAdmin}">
                <a th:href="@{/logout}" href="/logout">로그아웃</a>
                <a th:href="@{/member/mypage}" href="/member/mypage">마이페이지</a>
                <a th:href="@{/notice/list}" href="/notice/list">게시판</a>
            </th:block>
            <th:block th:if="${isAdmin}">
                <a th:href="@{/logout}" href="/logout">로그아웃</a>
                <a th:href="@{/member/mypage}" href="/member/mypage">마이페이지</a>
                <a th:href="@{/notice/list}" href="/notice/list">게시판</a>
                <a th:href="@{/member/manage}" href="/member/manage">회원관리</a>
            </th:block>
        </div>
    </div>
</header>
'''

COMMON_FOOTER = '''
<footer id="ft">
    <div class="ft_topbar">
        <div class="container ft_topbar_inner">
            <div class="ft_tel">
                <em class="bar">|</em><a href="https://www.youtube.com/@icncityhall" target="_blank"><img th:src="@{/images/icon/snsIcon1.png}" src="/images/icon/snsIcon1.png" alt="유튜브"></a>
                <em class="bar">|</em><a href="https://www.instagram.com/incheon_gov" target="_blank"><img th:src="@{/images/icon/snsIcon2.png}" src="/images/icon/snsIcon2.png" alt="인스타그램"></a>
                <em class="bar">|</em><a href="https://www.facebook.com/incheon.gov" target="_blank"><img th:src="@{/images/icon/snsIcon3.png}" src="/images/icon/snsIcon3.png" alt="페이스북"></a>
                <em class="bar">|</em><a href="https://blog.naver.com/incheontogi" target="_blank"><img th:src="@{/images/icon/snsIcon4.png}" src="/images/icon/snsIcon4.png" alt="블로그"></a>
                <em class="bar">|</em>
            </div>
            <nav class="ft_policy">
                <a th:href="@{/policy/privacy}" href="/policy/privacy">개인정보처리방침</a>
                <a th:href="@{/policy/copyright}" href="/policy/copyright">저작권보호정책</a>
                <a href="#" download>뷰어 다운로드</a>
            </nav>
        </div>
    </div>
    <div class="ft_body">
        <div class="container ft_body_inner">
            <div class="ft_info">
                <div class="ft_logos">
                    <a href="https://www.incheon.go.kr/index"><img th:src="@{/images/footer_logo01.svg}" src="/images/footer_logo01.svg" alt="인천광역시"></a>
                    <a href="https://www.ito.or.kr/main/"><img th:src="@{/images/footer_logo02.svg}" src="/images/footer_logo02.svg" alt="인천관광공사"></a>
                    <a href="https://www.iisland.or.kr/"><img th:src="@{/images/footer_logo03.png}" src="/images/footer_logo03.png" id="logo_sum" alt="인천섬발전지원센터"></a>
                    <a href="https://ifac.or.kr/index.do"><img th:src="@{/images/footer_logo04.svg}" src="/images/footer_logo04.svg" alt="인천문화재단"></a>
                </div>
                <p class="ft_addr">[21404] 인천 부평구 광장로 16 6층 &nbsp; TEL : 0507-1424-2448 &nbsp; FAX : 032-721-6224</p>
                <p class="ft_notice">본 홈페이지에 게시되는 이메일주소 자동수집을 거부하며 이를 위반 시 정보통신망법에 의해 처벌됨을 유념하시기 바랍니다.</p>
                <p class="ft_copy">COPYRIGHT(c) 2026 MBC Academy. ALL RIGHTS RESERVED.</p>
            </div>
            <div class="ft_badge">
                <a href="https://www.wa.or.kr/board/list.asp?search=total&SearchString=%C0%CE%C3%B5%C5%F5%BE%EE&BoardID=0006">
                    <img th:src="@{/images/footer_webmark_2025.png}" src="/images/footer_webmark_2025.png" alt="WA 웹접근성" class="wa_img">
                </a>
            </div>
        </div>
    </div>
</footer>
<a href="#" class="btn-top">TOP</a>
'''


def snb(selected: str) -> str:
    return f'''
            <div id="snb" class="snb">
                <div class="snb_wrap">
                    <div class="snb_title_wrap"><h2 class="snb_title">게시판</h2></div>
                    <div class="snb_nav_wrap">
                        <nav class="snb_nav">
                            <ul class="depth2">
                                <li class="fst_child"><a th:href="@{{/notice/list}}" href="/notice/list" target="_self"{' title="선택됨"' if selected == 'notice' else ''}><span>공지사항</span></a></li>
                                <li class="sec_child"><a th:href="@{{/review/list}}" href="/review/list" target="_self"{' title="선택됨"' if selected == 'review' else ''}><span>여행후기</span></a></li>
                                <li class="thr_child"><a th:href="@{{/policy/privacy}}" href="/policy/privacy" target="_self"{' title="선택됨"' if selected == 'privacy' else ''}><span>개인정보처리방침</span></a></li>
                                <li class="four_child"><a th:href="@{{/policy/copyright}}" href="/policy/copyright" target="_self"{' title="선택됨"' if selected == 'copyright' else ''}><span>저작권보호정책</span></a></li>
                            </ul>
                        </nav>
                    </div>
                </div>
            </div>
'''


def page_template(title: str, css: str, current_path_label: str, selected: str, body: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="ko" xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" th:href="@{{/css/common.css}}" href="/css/common.css">
    <link rel="stylesheet" th:href="@{{/css/reset.css}}" href="/css/reset.css">
    <link rel="stylesheet" th:href="@{{/css/fonts.css}}" href="/css/fonts.css">
    <link rel="stylesheet" th:href="@{{/css/{css}}}" href="/css/{css}">
</head>
<body>
<div class="wrap">
{COMMON_HEADER}
<div class="contanier">
    <div class="content_location" id="content_location">
        <div class="content_location_inner">
            <ul>
                <li class="home"><p><a th:href="@{{/}}" href="/">Home</a> <span>&gt;</span></p></li>
                <li><p><a th:href="@{{/notice/list}}" href="/notice/list">게시판</a> <span>&gt;</span></p></li>
                <li><p>{current_path_label}</p></li>
            </ul>
        </div>
    </div>
    <div class="content_wrap">
{snb(selected)}
        <main class="content">
            <div class="content_head"><div class="content_title_wrap"><h3 class="content_title">{title}</h3></div></div>
{body}
        </main>
    </div>
</div>
{COMMON_FOOTER}
</div>
</body>
</html>
'''


NOTICE_LIST_BODY = '''
            <section class="con">
                <div class="form_wrap board_wrap">
                    <article class="form_con board_card">
                        <h4 class="item_tit">&nbsp목록&nbsp</h4>
                        <table class="table">
                            <thead>
                            <tr><th>번호</th><th>제목</th><th>작성자</th><th>조회수</th></tr>
                            </thead>
                            <tbody>
                            <tr th:if="${#lists.isEmpty(boards)}"><td colspan="4">등록된 공지사항이 없습니다.</td></tr>
                            <tr th:each="board : ${boards}">
                                <td class="no" th:text="${board.id}">1</td>
                                <td class="n_tit"><a th:href="@{/notice/detail/{id}(id=${board.id})}" href="/notice/detail/1" th:text="${board.title}">제목</a></td>
                                <td class="atho" th:text="${board.author}">관리자</td>
                                <td class="hits" th:text="${board.viewCount}">0</td>
                            </tr>
                            </tbody>
                        </table>
                        <div class="btn_con write_wrap" th:if="${isAdmin}">
                            <a th:href="@{/notice/write}" href="/notice/write" class="btn_ctrl write">글쓰기</a>
                        </div>
                        <div class="pagenav" th:if="${totalPages > 1}">
                            <a th:if="${currentPage > 0}" th:href="@{/notice/list(page=${currentPage - 1}, type=${type}, keyword=${keyword})}">&lt;</a>
                            <th:block th:each="pageNum : ${#numbers.sequence(0, totalPages - 1)}">
                                <a th:href="@{/notice/list(page=${pageNum}, type=${type}, keyword=${keyword})}"
                                   th:text="${pageNum + 1}"
                                   th:classappend="${pageNum == currentPage} ? 'active' : ''">1</a>
                            </th:block>
                            <a th:if="${currentPage < totalPages - 1}" th:href="@{/notice/list(page=${currentPage + 1}, type=${type}, keyword=${keyword})}">&gt;</a>
                        </div>
                    </article>
                </div>
            </section>
'''

NOTICE_DETAIL_BODY = '''
            <section class="con">
                <div class="form_wrap board_wrap">
                    <article class="form_con board_card">
                        <h4 class="item_tit">&nbsp글 상세보기&nbsp</h4>
                        <table class="table detail_table">
                            <tbody>
                            <tr><th>번호</th><td th:text="${board.id}">1</td></tr>
                            <tr><th>제목</th><td th:text="${board.title}">제목</td></tr>
                            <tr><th>작성자</th><td th:text="${board.author}">관리자</td></tr>
                            <tr><th>작성일</th><td th:text="${#temporals.format(board.createdAt, 'yyyy-MM-dd HH:mm')}">2026-03-12 10:00</td></tr>
                            <tr><th>조회수</th><td th:text="${board.viewCount}">0</td></tr>
                            <tr>
                                <th>첨부파일</th>
                                <td>
                                    <div th:if="${#lists.isEmpty(board.attachments)}">첨부파일 없음</div>
                                    <div th:each="file : ${board.attachments}">
                                        <a th:href="${file.filePath}" th:text="${file.fileName}" href="#">파일명</a>
                                    </div>
                                </td>
                            </tr>
                            <tr><th>내용</th><td><div class="detail_body" th:utext="${board.displayContent}">내용</div></td></tr>
                            </tbody>
                        </table>
                        <div class="btn_con detail_btn_con">
                            <div class="btn_con detail_btn_wrap">
                                <a th:href="@{/notice/list}" href="/notice/list" class="btn_ctrl list">글 목록</a>
                                <div class="detail_btn_right" th:if="${isAdmin}">
                                    <a th:href="@{/notice/edit/{id}(id=${board.id})}" href="/notice/edit/1" class="btn_ctrl edit">수정</a>
                                    <form th:action="@{/notice/delete/{id}(id=${board.id})}" method="post" style="display:inline;">
                                        <button type="submit" class="btn_ctrl del" onclick="return confirm('삭제하시겠습니까?');">삭제</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </article>
                </div>
            </section>
'''

NOTICE_FORM_BODY = '''
            <section class="con">
                <div class="form_wrap board_wrap">
                    <article class="form_con board_card">
                        <h3 class="item_tit" th:text="${boardForm.id == null ? ' 글 쓰기' : ' 글 수정'}">&nbsp글 쓰기</h3>
                        <form th:action="${boardForm.id == null} ? @{/notice/write} : @{/notice/edit/{id}(id=${boardForm.id})}" method="post" enctype="multipart/form-data" class="form2">
                            <table class="table write_table">
                                <tbody>
                                <tr><th><label for="title">글 제목</label></th><td><input type="text" name="title" id="title" class="txt_ctrl" placeholder="제목을 입력하세요" th:value="${boardForm.title}"></td></tr>
                                <tr><th><label for="content">글 내용</label></th><td><textarea name="content" id="content" class="txt_ctrl memo_ctrl" placeholder="내용을 입력하세요" th:text="${boardForm.content}"></textarea></td></tr>
                                <tr><th><label for="author">작성자</label></th><td><input type="text" name="author" id="author" class="txt_ctrl" th:value="${authorName}" readonly></td></tr>
                                <tr><th><label for="newsfile">첨부 파일</label></th><td><input type="file" name="newsfile" id="newsfile" class="txt_ctrl file_ctrl" multiple></td></tr>
                                </tbody>
                            </table>
                            <div class="btn_con write_btn_wrap">
                                <a th:href="@{/notice/list}" href="/notice/list" class="btn_ctrl list">게시판</a>
                                <button type="submit" class="btn_ctrl write" th:text="${boardForm.id == null ? '등록' : '수정'}">등록</button>
                            </div>
                        </form>
                    </article>
                </div>
            </section>
'''

REVIEW_LIST_BODY = NOTICE_LIST_BODY.replace('/notice/', '/review/').replace('공지사항', '여행후기').replace('isAdmin', 'isLogin')
REVIEW_DETAIL_BODY = NOTICE_DETAIL_BODY.replace('/notice/', '/review/').replace('공지사항', '여행후기').replace('th:if="${isAdmin}"', 'th:if="${isOwner or isAdmin}"')
REVIEW_FORM_BODY = NOTICE_FORM_BODY.replace('/notice/', '/review/').replace('공지사항', '여행후기').replace('게시판', '글 목록')

PRIVACY_BODY = '''
            <section class="privacy_body">
                <article class="privacy_item">
                    <p class="privacy_text">인천투어는 「개인정보 보호법」에 따라 그 목적에 필요한 범위에서 최소한의 개인정보만을 적법하고 정당하게 수집·이용하고, 정보주체의 개인정보 및 권익을 보호하기 위해 개인정보처리방침을 공개합니다.</p>
                </article>
                <article class="privacy_item">
                    <h3 class="privacy_strong">제1조 (개인정보의 처리 목적)</h3>
                    <p class="privacy_text">회원가입, 게시판 운영, 문의 응대, 서비스 개선을 위한 최소한의 개인정보를 처리합니다.</p>
                </article>
                <article class="privacy_item">
                    <h3 class="privacy_strong">제2조 (개인정보의 보유 및 파기)</h3>
                    <p class="privacy_text">처리 목적이 달성되면 관련 법령이 정한 경우를 제외하고 지체 없이 파기합니다.</p>
                </article>
                <article class="privacy_item">
                    <h3 class="privacy_strong">제3조 (정보주체의 권리)</h3>
                    <p class="privacy_text">정보주체는 자신의 개인정보에 대해 열람, 정정, 삭제, 처리정지를 요구할 수 있습니다.</p>
                </article>
            </section>
'''

COPYRIGHT_BODY = '''
            <section class="copyright_body">
                <article class="copyright_item">
                    <p class="copyright_text">인천투어에 게시된 저작물은 「저작권법」 및 공공누리 이용조건에 따라 보호됩니다.</p>
                </article>
                <article class="copyright_item">
                    <p class="copyright_text">출처 표시가 있는 공공저작물은 해당 이용조건 범위에서만 사용해 주세요.</p>
                </article>
                <article class="copyright_item">
                    <p class="copyright_text">별도 이용허락이 없는 자료의 무단 복제, 배포, 전송은 제한될 수 있습니다.</p>
                </article>
                <div class="cc_img_box">
                    <img th:src="@{/images/copyright/copyright05.jpg}" src="/images/copyright/copyright05.jpg" alt="자유이용">
                </div>
            </section>
'''

# Java files
write('src/main/java/com/example/tour/config/SecurityConfig.java', SECURITY_CONFIG)
write('src/main/java/com/example/tour/controller/NoticeApiController.java', NOTICE_API_CONTROLLER)
write('src/main/java/com/example/tour/controller/ReviewController.java', REVIEW_CONTROLLER)

# Notice / Review / Policy templates
write('src/main/resources/templates/notice/list.html', page_template('공지사항', 'boardcommon.css', '<a th:href="@{/notice/list}" href="/notice/list">공지사항</a>', 'notice', NOTICE_LIST_BODY))
write('src/main/resources/templates/notice/detail.html', page_template('공지사항', 'board_detailcommon.css', '<a th:href="@{/notice/list}" href="/notice/list">공지사항</a>', 'notice', NOTICE_DETAIL_BODY))
write('src/main/resources/templates/notice/form.html', page_template('공지사항', 'board_formcommon.css', '<a th:href="@{/notice/list}" href="/notice/list">공지사항</a>', 'notice', NOTICE_FORM_BODY))
write('src/main/resources/templates/review/list.html', page_template('여행후기', 'boardcommon.css', '<a th:href="@{/review/list}" href="/review/list">여행후기</a>', 'review', REVIEW_LIST_BODY))
write('src/main/resources/templates/review/detail.html', page_template('여행후기', 'board_detailcommon.css', '<a th:href="@{/review/list}" href="/review/list">여행후기</a>', 'review', REVIEW_DETAIL_BODY))
write('src/main/resources/templates/review/form.html', page_template('여행후기', 'board_formcommon.css', '<a th:href="@{/review/list}" href="/review/list">여행후기</a>', 'review', REVIEW_FORM_BODY))
write('src/main/resources/templates/policy/privacy.html', page_template('개인정보처리방침', 'privacycommon.css', '<a th:href="@{/policy/privacy}" href="/policy/privacy">개인정보처리방침</a>', 'privacy', PRIVACY_BODY))
write('src/main/resources/templates/policy/copyright.html', page_template('저작권보호정책', 'copyrightcommon.css', '<a th:href="@{/policy/copyright}" href="/policy/copyright">저작권보호정책</a>', 'copyright', COPYRIGHT_BODY))

# member templates: 회원가입 링크는 /member/terms 로 보이게 수정
member_replacements = {
    'src/main/resources/templates/member/login.html': [
        ('<a th:href="@{/member/join}" href="/member/join" target="_self">', '<a th:href="@{/member/terms}" href="/member/terms" target="_self">')
    ],
    'src/main/resources/templates/member/join.html': [
        ('<p><a th:href="@{/member/join}" href="/member/join">회원가입</a></p>', '<p><a th:href="@{/member/terms}" href="/member/terms">회원가입</a></p>'),
        ('<a th:href="@{/member/join}" href="/member/join" target="_self" title="선택됨">', '<a th:href="@{/member/terms}" href="/member/terms" target="_self" title="선택됨">')
    ],
    'src/main/resources/templates/member/terms.html': [
        ('<a th:href="@{/member/join}" href="/member/join" target="_self">', '<a th:href="@{/member/terms}" href="/member/terms" target="_self">')
    ]
}

for rel, replacements in member_replacements.items():
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

# spot sub pages: 로그인 버튼 영역 통일 + sub11 파싱 오류 제거
spot_tnb = '''<div class="tnb">
      <th:block th:if="${!isLogin}">
        <a th:href="@{/member/login}" href="/member/login">로그인</a>
        <a th:href="@{/member/terms}" href="/member/terms">회원가입</a>
        <a th:href="@{/notice/list}" href="/notice/list">게시판</a>
      </th:block>
      <th:block th:if="${isLogin and !isAdmin}">
        <a th:href="@{/logout}" href="/logout">로그아웃</a>
        <a th:href="@{/member/mypage}" href="/member/mypage">마이페이지</a>
        <a th:href="@{/notice/list}" href="/notice/list">게시판</a>
      </th:block>
      <th:block th:if="${isAdmin}">
        <a th:href="@{/logout}" href="/logout">로그아웃</a>
        <a th:href="@{/member/mypage}" href="/member/mypage">마이페이지</a>
        <a th:href="@{/notice/list}" href="/notice/list">게시판</a>
        <a th:href="@{/member/manage}" href="/member/manage">회원관리</a>
      </th:block>
    </div>
  </div>
</header>'''

for path in sorted((ROOT / 'src/main/resources/templates/spot').glob('sub*.html')):
    text = path.read_text(encoding='utf-8')
    text = text.replace('@{/member/join}', '@{/member/terms}')
    text = text.replace('th:href="#"', 'href="#"')
    text = re.sub(r'<div class="tnb">.*?</div>\s*</div>\s*</header>', spot_tnb, text, flags=re.S)
    path.write_text(text, encoding='utf-8')

print('PATCH DONE')