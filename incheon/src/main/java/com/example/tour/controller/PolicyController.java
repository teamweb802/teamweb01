package com.example.tour.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/policy")
public class PolicyController {

    @GetMapping("/privacy")
    public String privacy() {
        return "policy/privacy";
    }

    @GetMapping("/copyright")
    public String copyright() {
        return "policy/copyright";
    }
}
