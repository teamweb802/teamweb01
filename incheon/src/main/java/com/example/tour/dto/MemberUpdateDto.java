package com.example.tour.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MemberUpdateDto {
    private String email;
    private String phone;
    private String pw;
    private String pw2;
}