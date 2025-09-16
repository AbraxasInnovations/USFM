-- Add image_url field to posts table
ALTER TABLE posts ADD COLUMN image_url text;

-- Add index for image_url queries
CREATE INDEX idx_posts_image_url ON posts (image_url) WHERE image_url IS NOT NULL;

-- Update existing posts with placeholder images (optional)
-- UPDATE posts SET image_url = 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600&fit=crop&crop=center' WHERE image_url IS NULL;
