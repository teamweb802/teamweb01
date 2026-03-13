package com.example.tour.service;

import com.example.tour.domain.Member;
import com.example.tour.domain.Role;
import com.example.tour.dto.MemberJoinRequestDto;
import com.example.tour.dto.MemberListDto;
import com.example.tour.dto.MemberMyPageDto;
import com.example.tour.dto.MemberUpdateDto;
import com.example.tour.repository.MemberRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MemberService {

    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;


    public Member findByLoginId(String loginId) {
        return memberRepository.findByLoginId(loginId)
                .orElseThrow(() -> new IllegalArgumentException("해당 회원이 없습니다."));
    }

    public boolean existsByLoginId(String loginId) {
        return memberRepository.existsByLoginId(loginId);
    }

    public void signup(MemberJoinRequestDto request) {
        if (memberRepository.existsByLoginId(request.getId())) {
            throw new IllegalArgumentException("이미 사용 중인 아이디입니다.");
        }

        if (memberRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("이미 사용 중인 이메일입니다.");
        }

        Member member = Member.builder()
                .loginId(request.getId())
                .passwordHash(passwordEncoder.encode(request.getPw()))
                .email(request.getEmail())
                .phone(request.getTel())
                .role(Role.USER)
                .build();

        memberRepository.save(member);
    }

    public List<MemberListDto> getManageList() {
        return memberRepository.findAllByOrderByIdDesc()
                .stream()
                .map(MemberListDto::new)
                .toList();
    }
    public MemberMyPageDto getMyPage(String loginId) {
        Member member = memberRepository.findByLoginId(loginId)
                .orElseThrow(() -> new IllegalArgumentException("회원이 없습니다."));
        return new MemberMyPageDto(member);
    }

    @Transactional
    public void updateMyPage(String loginId, MemberUpdateDto dto) {
        Member member = memberRepository.findByLoginId(loginId)
                .orElseThrow(() -> new IllegalArgumentException("회원이 없습니다."));

        member.setEmail(dto.getEmail());
        member.setPhone(dto.getPhone());

        if (dto.getPw() != null && !dto.getPw().isBlank()) {
            if (!dto.getPw().equals(dto.getPw2())) {
                throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
            }
            member.setPasswordHash(passwordEncoder.encode(dto.getPw()));
        }
    }

    @Transactional
    public void withdraw(String loginId) {
        Member member = memberRepository.findByLoginId(loginId)
                .orElseThrow(() -> new IllegalArgumentException("회원이 없습니다."));

        if (member.getRole() == Role.ADMIN) {
            throw new IllegalArgumentException("관리자는 회원탈퇴할 수 없습니다.");
        }

        memberRepository.delete(member);
    }
}