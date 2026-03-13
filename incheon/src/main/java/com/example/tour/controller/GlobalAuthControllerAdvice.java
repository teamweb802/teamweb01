package com.example.tour.controller;

import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.ui.Model;

@ControllerAdvice
public class GlobalAuthControllerAdvice {

    @ModelAttribute
    public void addAuthInfo(Model model, Authentication authentication) {
        boolean isLogin = authentication != null
                && authentication.isAuthenticated()
                && !(authentication instanceof AnonymousAuthenticationToken);

        boolean isAdmin = isLogin && authentication.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));

        model.addAttribute("isLogin", isLogin);
        model.addAttribute("isAdmin", isAdmin);
        model.addAttribute("loginId", isLogin ? authentication.getName() : null);
    }
}