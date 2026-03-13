package com.example.tour.dto;

import com.example.tour.domain.PostAttachment;
import lombok.Getter;

@Getter
public class AttachmentDto {

    private Long id;
    private String fileName;
    private String filePath;
    private Long fileSize;

    public AttachmentDto(PostAttachment attachment) {
        this.id = attachment.getId();
        this.fileName = attachment.getFileName();
        this.filePath = attachment.getFilePath();
        this.fileSize = attachment.getFileSize();
    }
}