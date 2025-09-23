-- Add company_name field to posts table for SEC filings
ALTER TABLE posts ADD COLUMN company_name TEXT;

-- Create index for company_name for better query performance
CREATE INDEX idx_posts_company_name ON posts (company_name) WHERE company_name IS NOT NULL;

-- Add comment to document the field
COMMENT ON COLUMN posts.company_name IS 'Company name for SEC filings and other corporate documents';
