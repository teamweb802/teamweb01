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
