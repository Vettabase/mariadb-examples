CREATE SCHEMA lkv;
USE lkv;

CREATE TABLE ping (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    url VARCHAR(50) NOT NULL,
    duration DOUBLE NOT NULL,
    PRIMARY KEY (id),
    UNIQUE unq_url (url),
    CHECK (url LIKE '_%._%')
)
    ENGINE TIDESDB
;

