-- Seed data for posts only (sections already exist)
-- Run this in your Supabase SQL Editor

-- Insert sample posts
insert into posts (
  title,
  summary,
  excerpt,
  source_name,
  source_url,
  section_slug,
  tags,
  content_hash,
  status,
  origin_type
) values
(
  'Microsoft Acquires AI Startup for $2.3B',
  'Major tech acquisition signals continued AI investment boom',
  'Microsoft Corporation announced today that it has entered into a definitive agreement to acquire Advanced AI Solutions, a leading artificial intelligence startup, for approximately $2.3 billion in cash. The acquisition is expected to close in the second quarter of 2024, subject to regulatory approvals.',
  'Microsoft News',
  'https://news.microsoft.com/ai-acquisition',
  'ma',
  ARRAY['ai', 'acquisition', 'microsoft', 'tech'],
  'hash1',
  'published',
  'PRESS'
),
(
  'Fed Signals Rate Stability Through Q2',
  'Federal Reserve maintains dovish stance amid economic uncertainty',
  'The Federal Reserve indicated today that interest rates will likely remain stable through the second quarter, citing ongoing economic headwinds and inflation concerns. Chair Powell emphasized the need for continued monitoring of economic indicators.',
  'Federal Reserve',
  'https://federalreserve.gov/news/pressreleases',
  'reg',
  ARRAY['fed', 'rates', 'monetary-policy', 'inflation'],
  'hash2',
  'published',
  'USGOV'
),
(
  'Blackstone Raises $15B for New Private Equity Fund',
  'Largest PE fundraise of 2024 demonstrates continued investor appetite',
  'Blackstone Inc. announced the successful closing of its latest private equity fund, raising $15 billion from institutional investors. The fund will focus on technology and healthcare investments across North America.',
  'Blackstone',
  'https://blackstone.com/news/fund-close',
  'lbo',
  ARRAY['private-equity', 'blackstone', 'fundraising', 'pe'],
  'hash3',
  'published',
  'PRESS'
),
(
  'Tesla Stock Surges 8% on Q4 Earnings Beat',
  'Strong delivery numbers and margin improvement drive investor optimism',
  'Tesla Inc. reported fourth-quarter earnings that exceeded analyst expectations, with vehicle deliveries reaching a record high. The company also announced plans to accelerate production of its Cybertruck model.',
  'Tesla Investor Relations',
  'https://tesla.com/ir/earnings',
  'cap',
  ARRAY['tesla', 'earnings', 'automotive', 'ev'],
  'hash4',
  'published',
  'PRESS'
),
(
  'DOJ Investigates Potential Antitrust Violations in Tech Sector',
  'Regulatory scrutiny intensifies for major technology companies',
  'The Department of Justice has launched a preliminary investigation into potential antitrust violations by several major technology companies. The probe focuses on market concentration and competitive practices in the digital advertising space.',
  'Department of Justice',
  'https://justice.gov/news/antitrust-investigation',
  'reg',
  ARRAY['antitrust', 'doj', 'tech', 'regulation'],
  'hash5',
  'published',
  'USGOV'
),
(
  'Rumor: Apple Considering Major Acquisition',
  'Sources suggest Apple may be evaluating strategic acquisition targets',
  'Industry sources indicate that Apple Inc. is actively evaluating potential acquisition targets in the artificial intelligence and augmented reality sectors. While no specific targets have been confirmed, the company is reportedly seeking to strengthen its position in emerging technologies.',
  'Tech Industry Sources',
  'https://example.com/rumor',
  'rumor',
  ARRAY['apple', 'acquisition', 'ai', 'rumor'],
  'hash6',
  'published',
  'RUMOR'
),
(
  'Goldman Sachs Reports Strong Q4 Trading Revenue',
  'Investment banking division shows resilience amid market volatility',
  'Goldman Sachs Group Inc. reported fourth-quarter results that beat expectations, driven by strong performance in its trading and investment banking divisions. The bank also announced a $2 billion share repurchase program.',
  'Goldman Sachs',
  'https://goldmansachs.com/ir/earnings',
  'cap',
  ARRAY['goldman-sachs', 'earnings', 'investment-banking', 'trading'],
  'hash7',
  'published',
  'PRESS'
),
(
  'KKR Completes $8B Take-Private of Software Company',
  'Largest take-private transaction of the year in software sector',
  'KKR & Co. announced the successful completion of its $8 billion take-private acquisition of Enterprise Software Solutions, a leading provider of business software. The transaction represents one of the largest private equity deals in the software sector this year.',
  'KKR',
  'https://kkr.com/news/take-private-complete',
  'lbo',
  ARRAY['kkr', 'take-private', 'software', 'pe'],
  'hash8',
  'published',
  'PRESS'
),
(
  'SEC Proposes New Disclosure Rules for Public Companies',
  'Enhanced transparency requirements aim to improve investor protection',
  'The Securities and Exchange Commission has proposed new disclosure rules that would require public companies to provide more detailed information about their environmental, social, and governance practices. The rules are subject to a 60-day comment period.',
  'Securities and Exchange Commission',
  'https://sec.gov/news/press-release',
  'reg',
  ARRAY['sec', 'disclosure', 'esg', 'regulation'],
  'hash9',
  'published',
  'SEC'
),
(
  'Amazon Web Services Launches New AI Services',
  'Cloud computing giant expands AI offerings to compete with Microsoft and Google',
  'Amazon Web Services announced the launch of several new artificial intelligence services, including advanced machine learning tools and AI-powered analytics. The services are designed to help businesses integrate AI into their operations more easily.',
  'Amazon Web Services',
  'https://aws.amazon.com/news/ai-services',
  'cap',
  ARRAY['aws', 'ai', 'cloud', 'amazon'],
  'hash10',
  'published',
  'PRESS'
);

-- Insert more posts to test the 30-post limit
insert into posts (
  title,
  summary,
  excerpt,
  source_name,
  source_url,
  section_slug,
  tags,
  content_hash,
  status,
  origin_type
) 
select 
  'Sample Post ' || generate_series,
  'This is a sample post for testing purposes',
  'This is a sample excerpt that demonstrates the content structure. It provides a brief overview of the news item and gives readers a quick understanding of the key points.',
  'Sample Source',
  'https://example.com/post/' || generate_series,
  CASE (generate_series % 5)
    when 0 then 'ma'
    when 1 then 'lbo'
    when 2 then 'reg'
    when 3 then 'cap'
    else 'rumor'
  end,
  ARRAY['sample', 'test', 'demo'],
  'sample_hash_' || generate_series,
  'published',
  'PRESS'
from generate_series(11, 40);
