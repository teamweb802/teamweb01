package com.example.tour.dto;


import com.example.tour.domain.Post;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
public class NoticeDetailDto {

    private Long id;
    private String title;
    private String content;
    private String displayContent;
    private String author;
    private int viewCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<AttachmentDto> attachments;

    public NoticeDetailDto(Post post, String author) {
        this.id = post.getId();
        this.title = post.getTitle();
        this.content = post.getContent();
        this.displayContent = convertContent(post.getContent());
        this.author = author;
        this.viewCount = post.getViewCount();
        this.createdAt = post.getCreatedAt();
        this.updatedAt = post.getUpdatedAt();
        this.attachments = post.getAttachments().stream()
                .map(AttachmentDto::new)
                .toList();
    }

    private String convertContent(String content) {
        if (content == null) {
            return "";
        }
        return content.replace("\r\n", "<br>")
                .replace("\n", "<br>");
    }
}