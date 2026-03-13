package com.example.tour.controller;
import com.example.tour.dto.MemberJoinRequestDto;
import com.example.tour.dto.MemberUpdateDto;
import com.example.tour.service.MemberService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.logout.SecurityContextLogoutHandler;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequiredArgsConstructor
@RequestMapping("/member")
public class MemberController {

    private final MemberService memberService;

    @GetMapping("/login")
    public String loginForm() {
        return "member/login";
    }

    @GetMapping("/terms")
    public String termsForm() {
        return "member/terms";
    }

    @GetMapping("/join")
    public String joinForm() {
        return "member/join";
    }

    @ResponseBody
    @GetMapping("/check-id")
    public String checkId(@RequestParam("id") String loginId) {
        return memberService.existsByLoginId(loginId) ? "DUPLICATE" : "OK";
    }

    @ResponseBody
    @PostMapping("/join")
    public String join(@ModelAttribute MemberJoinRequestDto request) {
        if (!request.getPw().equals(request.getPw2())) {
            return "비밀번호가 일치하지 않습니다.";
        }

        memberService.signup(request);
        return "SUCCESS";
    }

    @GetMapping("/manage")
    public String manage(Model model) {
        model.addAttribute("members", memberService.getManageList());
        return "member/manage";
    }

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

    @GetMapping("/mypage")
    public String myPage(Model model, Authentication authentication) {
        String loginId = authentication.getName();
        model.addAttribute("member", memberService.getMyPage(loginId));
        model.addAttribute("updateForm", new MemberUpdateDto());
        return "member/mypage";
    }

    @PostMapping("/mypage")
    public String updateMyPage(@ModelAttribute MemberUpdateDto updateForm,
                               Authentication authentication) {
        String loginId = authentication.getName();
        memberService.updateMyPage(loginId, updateForm);
        return "redirect:/member/mypage";
    }

    @PostMapping("/withdraw")
    public String withdraw(Authentication authentication,
                           HttpServletRequest request,
                           HttpServletResponse response) {
        String loginId = authentication.getName();

        memberService.withdraw(loginId);
        new SecurityContextLogoutHandler().logout(request, response, authentication);

        return "redirect:/member/login?withdraw=success";
    }
}