package com.example.tour.controller;

import com.example.tour.dto.NoticeListDto;
import com.example.tour.service.NoticeService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
@RequiredArgsConstructor
public class HomeController {

    private final NoticeService noticeService;

    @GetMapping("/")
    public String home(Model model) {
        List<NoticeListDto> topNotices = noticeService.getTop4List();
        model.addAttribute("topNotices", topNotices);
        return "index";
    }
}