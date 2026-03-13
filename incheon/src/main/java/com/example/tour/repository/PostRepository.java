package com.example.tour.repository;

import com.example.tour.domain.Post;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PostRepository extends JpaRepository<Post, Long> {

    List<Post> findByBoardTypeAndDeletedFalseOrderByCreatedAtDesc(String boardType);

    List<Post> findByBoardTypeAndDeletedFalseAndTitleContainingOrderByCreatedAtDesc(String boardType, String keyword);

    List<Post> findByBoardTypeAndDeletedFalseAndContentContainingOrderByCreatedAtDesc(String boardType, String keyword);

    List<Post> findByBoardTypeAndDeletedFalseAndTitleContainingOrBoardTypeAndDeletedFalseAndContentContainingOrderByCreatedAtDesc(
            String boardType1, String titleKeyword,
            String boardType2, String contentKeyword
    );
    List<Post> findTop4ByBoardTypeAndDeletedFalseOrderByCreatedAtDesc(String boardType);
}