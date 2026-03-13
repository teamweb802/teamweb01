package com.example.tour.repository;

import java.util.List;
import java.util.Optional;

import com.example.tour.domain.Member;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MemberRepository extends JpaRepository<Member, Long> {
    Optional<Member> findByLoginId(String loginId);
    Optional<Member> findByEmail(String email);

    boolean existsByLoginId(String loginId);
    boolean existsByEmail(String email);

    List<Member> findAllByOrderByIdDesc();
}