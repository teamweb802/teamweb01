package com.example.tour.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MemberLoginRequestDto {
    private String id;
    private String pw;
}