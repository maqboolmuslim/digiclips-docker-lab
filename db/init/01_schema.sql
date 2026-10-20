-- Small version of the DigiClips schema (outlet hierarchy + chunks + typed text tracks)
CREATE TABLE market (
  market_id   INT AUTO_INCREMENT PRIMARY KEY,
  country     VARCHAR(60)  NOT NULL,
  state       VARCHAR(60),
  name        VARCHAR(100) NOT NULL,
  UNIQUE KEY uq_market (country, state, name)
);

CREATE TABLE outlet (
  outlet_id   INT AUTO_INCREMENT PRIMARY KEY,
  market_id   INT NOT NULL,
  media_class ENUM('tv','radio','web','print','podcast') NOT NULL,
  call_sign   VARCHAR(20)  NOT NULL,
  network     VARCHAR(40),
  UNIQUE KEY uq_outlet (market_id, call_sign),
  FOREIGN KEY (market_id) REFERENCES market(market_id)
);

-- 10 minute capture chunk (with 2 min lead and 2 min tail that overlap the next chunk)
CREATE TABLE media_chunk (
  chunk_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  outlet_id   INT NOT NULL,
  start_time  DATETIME NOT NULL,
  end_time    DATETIME NOT NULL,
  lead_sec    SMALLINT NOT NULL DEFAULT 120,
  tail_sec    SMALLINT NOT NULL DEFAULT 120,
  UNIQUE KEY uq_chunk (outlet_id, start_time),
  FOREIGN KEY (outlet_id) REFERENCES outlet(outlet_id)
);

-- one table for all six track types instead of six tables
CREATE TABLE text_line (
  line_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
  chunk_id    BIGINT NOT NULL,
  track_type  ENUM('closed_caption','stt_left','stt_right','video_text','image_rec','lip_read') NOT NULL,
  frame_no    INT NOT NULL,
  spoken_at   DATETIME NOT NULL,
  content     TEXT NOT NULL,
  in_overlap  BOOLEAN NOT NULL DEFAULT FALSE,   -- TRUE = an earlier chunk already has this moment, skip it to avoid duplicate words
  FOREIGN KEY (chunk_id) REFERENCES media_chunk(chunk_id),
  FULLTEXT KEY ft_content (content)
);
