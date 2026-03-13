package com.example.tour.service;

import com.example.tour.domain.Member;
import com.example.tour.domain.Post;
import com.example.tour.domain.PostAttachment;
import com.example.tour.dto.NoticeDetailDto;
import com.example.tour.dto.NoticeFormDto;
import com.example.tour.dto.NoticeListDto;
import com.example.tour.repository.MemberRepository;
import com.example.tour.repository.PostRepository;
import com.example.tour.util.FileUploadUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Paths;
import java.util.List;

@Service
@RequiredArgsConstructor
public class NoticeService {

    private final PostRepository postRepository;
    private final MemberRepository memberRepository;

    @Value("${file.upload-dir}")
    private String uploadDir;

    private static final String UPLOAD_URL = "/uploads/";

    private String getUploadPath() {
        return Paths.get(System.getProperty("user.dir"), uploadDir).toString();
    }

    @Transactional(readOnly = true)
    public List<NoticeListDto> getList() {
        List<Post> posts = postRepository.findByBoardTypeAndDeletedFalseOrderByCreatedAtDesc("NOTICE");

        return posts.stream()
                .map(post -> new NoticeListDto(post, getAuthorLoginId(post.getAuthorId())))
                .toList();
    }

    @Transactional(readOnly = true)
    public List<NoticeListDto> search(String type, String keyword) {
        List<Post> posts;

        if ("title".equals(type)) {
            posts = postRepository.findByBoardTypeAndDeletedFalseAndTitleContainingOrderByCreatedAtDesc("NOTICE", keyword);
        } else if ("content".equals(type)) {
            posts = postRepository.findByBoardTypeAndDeletedFalseAndContentContainingOrderByCreatedAtDesc("NOTICE", keyword);
        } else {
            posts = postRepository
                    .findByBoardTypeAndDeletedFalseAndTitleContainingOrBoardTypeAndDeletedFalseAndContentContainingOrderByCreatedAtDesc(
                            "NOTICE", keyword,
                            "NOTICE", keyword
                    );
        }

        return posts.stream()
                .map(post -> new NoticeListDto(post, getAuthorLoginId(post.getAuthorId())))
                .toList();
    }

    @Transactional
    public NoticeDetailDto getDetail(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다."));

        if (post.isDeleted()) {
            throw new IllegalArgumentException("삭제된 게시글입니다.");
        }

        post.increaseViewCount();

        return new NoticeDetailDto(post, getAuthorLoginId(post.getAuthorId()));
    }

    @Transactional
    public Long create(NoticeFormDto dto, Long authorId, MultipartFile[] files) throws Exception {
        Post post = Post.builder()
                .boardType("NOTICE")
                .title(dto.getTitle())
                .content(dto.getContent())
                .authorId(authorId)
                .build();

        if (files != null) {
            String uploadPath = getUploadPath();

            for (MultipartFile file : files) {
                if (file == null || file.isEmpty()) continue;

                String storedFileName = FileUploadUtil.saveFile(file, uploadPath);

                PostAttachment attachment = PostAttachment.builder()
                        .post(post)
                        .fileName(file.getOriginalFilename())
                        .filePath(UPLOAD_URL + storedFileName)
                        .contentType(file.getContentType())
                        .fileSize(file.getSize())
                        .build();

                post.addAttachment(attachment);
            }
        }

        return postRepository.save(post).getId();
    }

    @Transactional
    public void update(Long id, NoticeFormDto dto, MultipartFile[] files) throws Exception {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다."));

        if (post.isDeleted()) {
            throw new IllegalArgumentException("삭제된 게시글입니다.");
        }

        post.update(dto.getTitle(), dto.getContent());

        boolean hasNewFiles = false;
        if (files != null) {
            for (MultipartFile file : files) {
                if (file != null && !file.isEmpty()) {
                    hasNewFiles = true;
                    break;
                }
            }
        }

        if (hasNewFiles) {
            String uploadPath = getUploadPath();

            for (PostAttachment oldFile : post.getAttachments()) {
                String oldStoredName = oldFile.getFilePath().replace("/uploads/", "");
                FileUploadUtil.deleteFile(oldStoredName, uploadPath);
            }

            post.getAttachments().clear();

            for (MultipartFile file : files) {
                if (file == null || file.isEmpty()) continue;

                String storedFileName = FileUploadUtil.saveFile(file, uploadPath);

                PostAttachment newAttachment = PostAttachment.builder()
                        .post(post)
                        .fileName(file.getOriginalFilename())
                        .filePath(UPLOAD_URL + storedFileName)
                        .contentType(file.getContentType())
                        .fileSize(file.getSize())
                        .build();

                post.addAttachment(newAttachment);
            }
        }
    }

    @Transactional
    public void delete(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("게시글을 찾을 수 없습니다."));

        String uploadPath = getUploadPath();

        for (PostAttachment file : post.getAttachments()) {
            String storedName = file.getFilePath().replace("/uploads/", "");
            FileUploadUtil.deleteFile(storedName, uploadPath);
        }

        post.softDelete();
    }

    private String getAuthorLoginId(Long authorId) {
        return memberRepository.findById(authorId)
                .map(Member::getLoginId)
                .orElse("알 수 없음");
    }

    @Transactional(readOnly = true)
    public List<NoticeListDto> getTop4List() {
        List<Post> posts = postRepository.findTop4ByBoardTypeAndDeletedFalseOrderByCreatedAtDesc("NOTICE");

        return posts.stream()
                .map(post -> new NoticeListDto(post, getAuthorLoginId(post.getAuthorId())))
                .toList();
    }
}