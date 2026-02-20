# 🚀 Competitor Intelligence Profiler - Complete User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Understanding Your Data](#understanding-your-data)
3. [Category Breakdown](#category-breakdown)
4. [How to Use Each Category](#how-to-use-each-category)
5. [Strategic Analysis Tips](#strategic-analysis-tips)
6. [FAQ](#faq)

---

## Getting Started

### What is this tool?
The Competitor Intelligence Profiler analyzes your competitors across **74 data points** to give you actionable insights about their business, marketing, SEO, and online presence.

### What you'll get:
- **Competitor profiles** with contact info, traffic estimates, SEO metrics
- **Keyword analysis** showing what topics they focus on
- **Mention tracking** revealing where they're being discussed
- **Technical insights** about their website performance
- **Social media presence** across all major platforms
- **Business intelligence** including reviews, ratings, and growth signals

---

## Understanding Your Data

### 📊 Your CSV File Contains 74 Columns Organized Into 9 Categories:

| Category | # of Columns | What It Tells You |
|----------|--------------|-------------------|
| **Basic Information** | 7 | Who they are, where they're located |
| **Contact & Communication** | 3 | How to reach them, their email/phone |
| **Keyword Intelligence** | 3 | What topics they focus on |
| **Web Mentions & Brand Tracking** | 9 | Where they're being talked about |
| **Google Business Profile** | 8 | Local presence, reviews, ratings |
| **Website & SEO Metrics** | 15 | How visible they are in search |
| **Social Media Presence** | 6 | Their social media footprint |
| **Technical & Performance** | 10 | Website quality and technical setup |
| **Competitive Intelligence** | 13 | Market position, growth signals |

---

## Category Breakdown

### 📋 1. BASIC INFORMATION
**What it is:** Core identifying information about the competitor.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **name** | Company/business name | Primary identifier for the competitor |
| **address** | Physical location | See if they're local, regional, or national |
| **domain** | Website domain (e.g., company.com) | Visit their site for deeper research |
| **url** | Full URL where data was found | Original source of information |
| **title** | Page title from search results | See how they position themselves |
| **query** | Your original search query | Remember what you searched for |
| **source** | Where data came from (web_scraping/google_cse) | Understand data reliability |

**💡 Use Case Example:**
> You search "real estate investors jacksonville fl" and find 12 competitors. Sort by **address** to see which ones are actually in Jacksonville vs. serving it remotely.

---

### 📞 2. CONTACT & COMMUNICATION
**What it is:** Ways to reach the competitor or monitor their communications.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **phones** | Phone numbers found on their site | Call for mystery shopping or market research |
| **emails** | Email addresses discovered | Contact for partnerships or monitoring |
| **email_patterns** | Common email formats (@domain.com) | Guess employee emails for outreach |

**💡 Use Case Example:**
> Use **phones** to call as a prospect and evaluate their sales process. Use **emails** to sign up for their newsletter and monitor their marketing campaigns.

---

### 🔑 3. KEYWORD INTELLIGENCE (NEW!)
**What it is:** The topics and keywords your competitors focus on.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **top_keywords** | Top 20 single keywords they use most | Topics they focus on (e.g., "investment, property, rental") |
| **top_phrases** | Top 10 two-word phrases | Their key messages (e.g., "passive income, cash flow") |
| **keyword_density_top5** | Most frequent keywords with counts | See emphasis (e.g., "investment:45" means "investment" appears 45 times) |

**💡 Use Case Example:**
> Competitor uses "passive income" 35 times but you never mention it. This reveals a messaging gap you should fill. Create content around passive income to compete.

**🎯 Strategic Actions:**
- **Content Ideas:** Use their top_keywords to find topics you're missing
- **SEO Gaps:** If they rank for keywords you don't mention, add those to your site
- **Ad Copy:** Use their top_phrases in your Google Ads for competitive conquesting

---

### 📣 4. WEB MENTIONS & BRAND TRACKING (NEW!)
**What it is:** Where and how often your competitors are being discussed online.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **mention_count_total** | Total web mentions found | Overall brand awareness indicator |
| **mention_count_social** | Mentions on Facebook/Twitter/LinkedIn | Social media buzz level |
| **mention_count_news** | Mentions in news articles | PR and media coverage |
| **mention_count_reviews** | Mentions on Yelp/BBB/review sites | Customer feedback volume |
| **mention_count_forums** | Mentions on Reddit/Quora/forums | Community discussion level |
| **mention_urls_social** | Actual URLs of social mentions | Visit to see what people say on social |
| **mention_urls_news** | URLs of news articles | Read press coverage about them |
| **mention_urls_reviews** | URLs of review sites | See customer reviews and complaints |
| **mention_urls_forums** | URLs of forum discussions | See unfiltered opinions about them |

**💡 Use Case Example:**
> Competitor has 45 news mentions while you have 3. Click **mention_urls_news** to see which publications cover them. Pitch those same journalists your story.

**🎯 Strategic Actions:**
- **PR Strategy:** If they have high news mentions, investigate their PR tactics
- **Reputation Management:** Check review mentions to see common complaints
- **Community Engagement:** High forum mentions? They're active in online communities
- **Partnership Opportunities:** Social mentions might reveal influencer partnerships

**🔔 Set Up Alerts:**
Visit https://www.talkwalker.com/alerts and create alerts for:
- Competitor brand names
- Their top keywords
- Their executives' names
Get notified instantly when they're mentioned online!

---

### 🏢 5. GOOGLE BUSINESS PROFILE DATA
**What it is:** Information from their Google Maps/Local listing.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **g_name** | Business name on Google | Official business name |
| **g_address** | Address from Google Maps | Verified physical location |
| **g_phone** | Phone from Google listing | Primary contact number |
| **g_rating** | Google star rating (0-5) | Overall customer satisfaction |
| **g_reviews** | Number of Google reviews | Review volume (more = more established) |
| **g_latitude** | Map latitude coordinate | Plot on a map to see coverage areas |
| **g_longitude** | Map longitude coordinate | Geographic analysis |
| **g_status** | Business status (OPERATIONAL/CLOSED) | Whether they're still active |

**💡 Use Case Example:**
> Sort by **g_rating** descending. The top competitor has 4.8 stars and 250 reviews. Read their reviews to see what customers love and replicate it.

**🎯 Strategic Actions:**
- **Review Analysis:** Click reviews to find strengths/weaknesses
- **Local SEO:** If they have high reviews, invest in getting more reviews yourself
- **Service Gaps:** Negative reviews reveal what they do poorly = your opportunity

---

### 🔍 6. WEBSITE & SEO METRICS
**What it is:** How well they rank in search engines and their SEO strength.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **word_count** | Total words on their homepage | Content depth indicator |
| **indexed_pages** | Pages indexed by Google | Site size (more = more authority) |
| **backlinks** | Number of links pointing to their site | SEO authority level |
| **referring_domains** | Unique sites linking to them | Link diversity (higher = better) |
| **domain_authority** | SEO authority score (0-100) | Overall SEO strength |
| **trust_flow** | Link quality score | Trustworthiness of their backlinks |
| **citation_flow** | Link quantity score | Volume of backlinks |
| **directory_count** | Business directory listings | Local SEO presence |
| **h1_tags** | Main headings on page | SEO structure quality |
| **meta_description** | Page description for search | How they attract clicks |
| **robots_txt** | Robot instructions | Technical SEO setup |
| **sitemap** | XML sitemap presence | Search engine accessibility |
| **title_tag_length** | Title character count | SEO optimization (50-60 is ideal) |
| **meta_desc_length** | Description character count | SEO optimization (150-160 is ideal) |
| **page_load_speed** | Load time in seconds | User experience quality |

**💡 Use Case Example:**
> Competitor has **domain_authority: 65** and **backlinks: 5,200** while you have DA 28 and 400 backlinks. They're crushing you in SEO. You need a link building strategy.

**🎯 Strategic Actions:**
- **Content Strategy:** Low word_count = opportunity to outrank with deeper content
- **Link Building:** High backlinks? Study their link profile with Ahrefs/Moz
- **Directory Listings:** Low directory_count? Easy wins by listing in the same directories
- **Technical SEO:** Compare title/meta lengths to optimize your own pages

---

### 📱 7. SOCIAL MEDIA PRESENCE
**What it is:** Their social media accounts and activity.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **facebook** | Facebook page URL | Follow to monitor their posts |
| **twitter** | Twitter/X profile URL | See their messaging and engagement |
| **linkedin** | LinkedIn company page | Professional content and hiring signals |
| **instagram** | Instagram profile | Visual content strategy |
| **youtube** | YouTube channel | Video marketing presence |
| **social_summary** | Overview of social presence | Quick snapshot of their social footprint |

**💡 Use Case Example:**
> Competitor has active Instagram (1,000+ posts) but you don't use Instagram. They're reaching an audience you're missing. Start an Instagram account.

**🎯 Strategic Actions:**
- **Content Inspiration:** Follow their social accounts to see what content works
- **Posting Frequency:** Check how often they post to benchmark your own activity
- **Platform Priority:** Focus on platforms where they're most active
- **Engagement Tactics:** See what posts get the most likes/comments

---

### ⚙️ 8. TECHNICAL & PERFORMANCE
**What it is:** Website quality, speed, and technical infrastructure.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **mobile_friendly** | Works well on phones | Mobile optimization status |
| **ssl_certificate** | HTTPS security enabled | Site security level |
| **page_load_speed** | Load time in seconds | User experience (under 3s is good) |
| **performance_score** | Overall speed score (0-100) | PageSpeed Insights score |
| **first_contentful_paint** | Time to first content (seconds) | Perceived speed |
| **canonical_tags** | Duplicate content handling | SEO technical setup |
| **open_graph_tags** | Social sharing optimization | How links look when shared |
| **schema_markup** | Structured data presence | Rich snippets in search |
| **header_structure** | H2/H3/H4 heading hierarchy | Content organization quality |
| **content_freshness** | Last updated date | How often they update content |

**💡 Use Case Example:**
> Competitor's **page_load_speed: 1.2s** vs. your **4.5s**. Their site loads 3x faster. Users are more likely to stay. Optimize your site speed immediately.

**🎯 Strategic Actions:**
- **Speed Optimization:** Slow load speed? They're losing customers. Outperform them with faster hosting
- **Mobile Priority:** No mobile_friendly? Huge opportunity if you're mobile-optimized
- **Technical SEO:** Missing schema_markup? Add it to your site for better search visibility

---

### 📊 9. COMPETITIVE INTELLIGENCE
**What it is:** Market position, growth signals, and business health indicators.

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **traffic_estimate** | Estimated monthly visitors | Relative traffic volume |
| **confidence_score** | Data quality score (0-100) | How reliable this data is |
| **hiring_signals** | Hiring activity score (0-1) | Are they growing? (0.7 = active hiring) |
| **hiring_growth_signal** | Growth trend score (0-1) | Expansion indicator |
| **reviews_bbb_signal** | BBB review presence | Established business indicator |
| **reviews_google_signal** | Google review activity | Customer feedback presence |
| **reviews_yelp_signal** | Yelp review presence | Consumer review activity |
| **ai_analysis** | AI-generated competitive insights | Strategic recommendations |
| **strengths** | Identified competitive advantages | What they do well |
| **weaknesses** | Identified vulnerabilities | Your opportunities to compete |
| **opportunities** | Market gaps they could fill | Threats to watch |
| **threats** | Risks to their business | Your competitive advantages |
| **strategy_recommendations** | Suggested actions | How to compete effectively |

**💡 Use Case Example:**
> Competitor has **hiring_signals: 0.9** and **traffic_estimate: 75,000**. They're rapidly growing. Read their **ai_analysis** to understand why and counter their strategy.

**🎯 Strategic Actions:**
- **Market Positioning:** High traffic? Study what's working for them
- **Growth Monitoring:** High hiring signals? They're expanding - prepare for increased competition
- **Weakness Exploitation:** Read **weaknesses** column to find gaps you can fill
- **Strategic Planning:** Use **strategy_recommendations** for actionable next steps

---

## How to Use Each Category

### 🎯 SCENARIO 1: You Want to Steal Their Customers

**Follow this workflow:**

1. **Check Reviews** (g_rating, g_reviews, reviews_*)
   - Sort by lowest rating
   - Read negative reviews
   - Find common complaints
   - Advertise that you solve those problems

2. **Analyze Keywords** (top_keywords, top_phrases)
   - See what they rank for
   - Create better content on those topics
   - Use their keywords in your Google Ads

3. **Study Mentions** (mention_urls_reviews, mention_urls_forums)
   - Visit review sites
   - See what customers complain about
   - Position yourself as the solution

**Example:**
> Competitor has g_rating: 3.2 with complaints about "slow response times" in reviews. Your ad: "Need faster service? We respond in under 2 hours, guaranteed."

---

### 🎯 SCENARIO 2: You Want to Outrank Them in SEO

**Follow this workflow:**

1. **Assess SEO Gap** (domain_authority, backlinks, indexed_pages)
   - Compare your metrics to theirs
   - If they're way ahead, this will take time
   - If you're close, you can catch up quickly

2. **Keyword Opportunities** (top_keywords, top_phrases)
   - Extract their keywords
   - Search for those keywords in Google
   - Create better, longer content than theirs

3. **Build Better Links** (referring_domains, directory_count)
   - Get listed in the same directories
   - Find sites linking to them (use Ahrefs)
   - Reach out for links to your site

4. **Technical Wins** (page_load_speed, mobile_friendly, schema_markup)
   - Beat them on speed (faster = better SEO)
   - Ensure your site is mobile-friendly
   - Add schema markup for rich snippets

**Example:**
> They rank for "real estate investment Jacksonville" with domain_authority: 35. You have DA 28. Write a 3,000-word guide on that topic (vs. their 1,200 words) and build 10 backlinks to it.

---

### 🎯 SCENARIO 3: You Want to Monitor Their Growth

**Follow this workflow:**

1. **Traffic Benchmark** (traffic_estimate)
   - Note their current traffic
   - Re-run profiler monthly
   - Track if they're growing or shrinking

2. **Growth Signals** (hiring_signals, hiring_growth_signal)
   - High scores = they're expanding
   - Monitor their LinkedIn for job postings
   - Prepare for increased competition

3. **Content Activity** (content_freshness)
   - See when they last updated
   - Frequent updates = active marketing
   - Rare updates = opportunity to outpace them

4. **Social Momentum** (facebook, twitter, linkedin)
   - Follow their social accounts
   - Track follower growth
   - See what content performs well

**Example:**
> January: traffic_estimate: 50,000, hiring_signals: 0.3
> March: traffic_estimate: 75,000, hiring_signals: 0.8
> **Action:** They're growing fast! Double down on your marketing before they dominate the market.

---

### 🎯 SCENARIO 4: You Want to Find Partnership Opportunities

**Follow this workflow:**

1. **Identify Strong Players** (domain_authority, g_rating, traffic_estimate)
   - Sort by highest scores
   - These are established, credible businesses
   - Good partnership candidates

2. **Check Compatibility** (top_keywords, ai_analysis)
   - Do they serve the same market but different need?
   - Example: You do mortgages, they do property management
   - Complementary = partnership opportunity

3. **Contact Them** (emails, phones, linkedin)
   - Use contact info to reach out
   - Propose referral partnership
   - "You refer mortgage clients to us, we refer property management to you"

**Example:**
> You find a competitor with traffic_estimate: 100,000 and top_keywords includes "property management" (which you don't offer). Partner with them to cross-refer clients.

---

### 🎯 SCENARIO 5: You Want to Create Better Content

**Follow this workflow:**

1. **Topic Analysis** (top_keywords, top_phrases)
   - See what topics they focus on
   - Identify gaps in your content

2. **Content Depth** (word_count, h1_tags, header_structure)
   - See how deep their content goes
   - Create longer, more comprehensive content

3. **Keyword Density** (keyword_density_top5)
   - See which keywords they emphasize
   - Match or exceed that emphasis

4. **Content Freshness** (content_freshness)
   - Old content? You can outrank with fresh content
   - Fresh content? You need to update more frequently

**Example:**
> They have 800-word blog posts on "real estate investing tips". You create a 3,000-word ultimate guide with more detail, better structure, and fresh 2025 data.

---

## Strategic Analysis Tips

### 📊 How to Prioritize Competitors

**Tier 1 - Direct Threats (Focus Here First):**
- High traffic_estimate (over 50,000/month)
- High domain_authority (over 40)
- High g_rating (4.0+) with many reviews
- Same geographic location (address field)
- Similar top_keywords to yours

**Tier 2 - Growing Competitors (Monitor Closely):**
- High hiring_signals (over 0.7)
- Frequent content_freshness updates
- Growing mention_count_total
- Active on social media

**Tier 3 - Aspirational (Learn From):**
- Very high domain_authority (70+)
- Massive traffic_estimate (200,000+)
- Excellent g_rating with thousands of reviews
- Study but don't directly compete yet

**Tier 4 - Weak Competitors (Easy Wins):**
- Low g_rating (under 3.5)
- Low domain_authority (under 20)
- Few indexed_pages
- Steal their customers by being better

---

### 🔄 Monthly Monitoring Routine

**Week 1:**
- Re-run competitor profiler
- Compare new data to last month
- Track changes in traffic_estimate, g_reviews, hiring_signals

**Week 2:**
- Visit mention_urls from all categories
- Read new reviews, news articles, forum posts
- Note any PR wins or reputation issues

**Week 3:**
- Check their social accounts (facebook, twitter, linkedin)
- See what content they posted this month
- Identify trends in messaging

**Week 4:**
- Update your strategy based on findings
- Create content targeting their top_keywords
- Adjust your positioning based on their weaknesses

---

### 💡 Pro Tips

**1. Combine Multiple Data Points:**
Don't look at columns in isolation. Example:
- High traffic + Low reviews = Not converting visitors to customers (opportunity!)
- High hiring + High social mentions = Aggressive growth phase (threat!)
- Low speed + High traffic = You can outperform with faster site

**2. Use Filters in Excel/Sheets:**
- Filter by g_rating > 4.0 to find best-in-class
- Filter by traffic_estimate > 50000 to find major players
- Filter by hiring_signals > 0.7 to find growing competitors

**3. Create Comparison Dashboards:**
Export key metrics for yourself vs. top 3 competitors:
| Metric | You | Competitor A | Competitor B | Competitor C |
|--------|-----|--------------|--------------|--------------|
| Traffic | 10K | 50K | 30K | 75K |
| DA | 25 | 45 | 35 | 60 |
| Reviews | 12 | 200 | 89 | 450 |

**4. Set Up Alerts:**
- Visit https://www.talkwalker.com/alerts
- Create alerts for each competitor name
- Create alerts for their top_keywords
- Get notified when they make moves

---

## FAQ

**Q: How often should I run the profiler?**
A: Monthly for active monitoring, quarterly for general awareness.

**Q: Which columns are most important?**
A: For most businesses: g_rating, traffic_estimate, top_keywords, mention_count_total, domain_authority

**Q: What if a competitor has no data in some columns?**
A: Common reasons:
- They don't have a Google Business Profile (g_* fields)
- They're not on social media (social fields)
- They're a new business (low backlinks, reviews)
- Website blocking (check robots_txt)

**Q: How accurate is traffic_estimate?**
A: It's an estimate based on multiple signals. Use it for relative comparison, not absolute numbers.

**Q: Can I track my own business?**
A: Yes! Search for your own business to benchmark against competitors.

**Q: What's a "good" domain_authority score?**
A: 
- 0-20: New/weak site
- 20-40: Established site
- 40-60: Strong site
- 60-80: Very strong site
- 80-100: Industry leader (rare)

**Q: How do I use the URLs in mention_urls_* columns?**
A: Click each URL to visit the site where they're mentioned. Read what people are saying about them.

**Q: What should I do if a competitor has way better metrics?**
A: Focus on their weaknesses column. Find what they do poorly and excel there. Compete on service, not established authority.

**Q: Can I export this data to other tools?**
A: Yes! The CSV works with Excel, Google Sheets, Tableau, Power BI, etc.

---

## Next Steps

1. **Run your first search** - Start with your main business keyword + location
2. **Sort by traffic_estimate** - Find your biggest competitors
3. **Read the top 3 profiles** - Focus on their strengths, weaknesses, top_keywords
4. **Set up alerts** - Use Talkwalker to monitor them
5. **Create action plan** - Use the scenario guides above
6. **Re-run monthly** - Track changes over time

---

## Need Help?

- Review this guide whenever you're analyzing competitors
- Each column has a specific use case - refer to the category sections
- Use the scenario guides for step-by-step workflows
- Combine multiple data points for deeper insights

**Remember:** This tool gives you intelligence. What you do with it determines your success. Focus on competitors' weaknesses, track their growth, and stay one step ahead.

---

*Last Updated: February 2025*
*Version: 2.0 - Now includes Keyword Intelligence & Mention Tracking*
