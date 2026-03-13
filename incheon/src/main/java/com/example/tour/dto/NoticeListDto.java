package com.example.tour.dto;

import com.example.tour.domain.Post;
import lombok.Getter;

import java.time.LocalDateTime;


@Getter
public class NoticeListDto {
    private Long id;
    private String title;
    private String author;
    private int viewCount;
    private LocalDateTime createdAt;

    public NoticeListDto(Post post, String author) {
        this.id = post.getId();
        this.title = post.getTitle();
        this.author = author;
        this.viewCount = post.getViewCount();
        this.createdAt = post.getCreatedAt();
    }
}