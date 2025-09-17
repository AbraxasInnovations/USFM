-- Add fields for scraped and rewritten content
ALTER TABLE posts ADD COLUMN scraped_content text;
ALTER TABLE posts ADD COLUMN article_slug text;

-- Add index for article slug lookups
CREATE INDEX idx_posts_article_slug ON posts (article_slug) WHERE article_slug IS NOT NULL;

-- Add index for scraped content
CREATE INDEX idx_posts_scraped_content ON posts (scraped_content) WHERE scraped_content IS NOT NULL;
