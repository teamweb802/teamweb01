CREATE TABLE member (
    id BIGSERIAL PRIMARY KEY,
    login_id VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_member_role CHECK (role IN ('USER', 'ADMIN'))
);

UPDATE member
SET role = 'ADMIN'
WHERE login_id = 'admin';


CREATE TABLE post (
    id BIGSERIAL PRIMARY KEY,
    board_type VARCHAR(30) NOT NULL DEFAULT 'NOTICE',
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    view_count INTEGER NOT NULL DEFAULT 0,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_post_author
        FOREIGN KEY (author_id) REFERENCES member(id)
);


CREATE TABLE post_attachment (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    content_type VARCHAR(100),
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attachment_post
        FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE INDEX ix_post_list_active
    ON post(board_type, created_at DESC)
    WHERE is_deleted = FALSE;

CREATE INDEX ix_post_author_id ON post(author_id);
CREATE INDEX ix_attachment_post_id ON post_attachment(post_id);


select * from member;
select * from post;
select * from post_attachment;
