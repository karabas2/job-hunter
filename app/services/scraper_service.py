import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import logging

logger = logging.getLogger(__name__)

async def scrape_linkedin_jobs(url: str):
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5) # Give it some time to load cards
            for _ in range(3):
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(1)

            # Extract job cards
            # Try multiple selectors for job cards in guest view
            selectors = [".base-card", ".jobs-search__results-list li", ".base-search-card"]
            job_cards = []
            for selector in selectors:
                job_cards = await page.query_selector_all(selector)
                if job_cards:
                    logger.info(f"Using selector '{selector}' - Found {len(job_cards)} cards")
                    break
            
            initial_jobs = []
            for card in job_cards:
                # Try multiple selectors for title, company, etc.
                title_el = await card.query_selector(".base-search-card__title, .job-search-card__title")
                company_el = await card.query_selector(".base-search-card__subtitle, .job-search-card__subtitle")
                link_el = await card.query_selector("a.base-card__full-link, a.job-search-card__link")
                
                if title_el and company_el and link_el:
                    title = (await title_el.inner_text()).strip()
                    company = (await company_el.inner_text()).strip()
                    job_url = await link_el.get_attribute("href")
                    
                    # More robust ID extraction
                    job_id = "unknown"
                    if "view/" in job_url:
                        job_id = job_url.split("view/")[1].split("/")[0].split("?")[0]
                    elif "-" in job_url:
                        job_id = job_url.split("?")[0].split("-")[-1]

                    initial_jobs.append({
                        "linkedin_job_id": job_id,
                        "title": title,
                        "company": company,
                        "location": "Remote/Turkey", # Default if not found
                        "url": job_url
                    })
            
            # Fallback: If no cards found but the URL has a currentJobId, try fetching it directly
            if not job_cards and "currentJobId=" in url:
                import re
                match = re.search(r"currentJobId=(\d+)", url)
                if match:
                    job_id = match.group(1)
                    logger.info(f"No list found, but found Job ID {job_id} in URL. Fetching directly...")
                    initial_jobs.append({
                        "linkedin_job_id": job_id,
                        "title": "Specific Targeted Job",
                        "company": "See Description",
                        "location": "Turkey",
                        "url": f"https://www.linkedin.com/jobs/view/{job_id}/"
                    })

            # Limit to top 15 jobs
            for job_info in initial_jobs[:15]:
                try:
                    logger.info(f"Navigating to job: {job_info['url']}")
                    await page.goto(job_info['url'], wait_until="domcontentloaded", timeout=40000)
                    await asyncio.sleep(4)
                    
                    # Extensive description selectors
                    desc_selectors = [
                        ".show-more-less-html__markup", 
                        ".description__text", 
                        ".jobs-description__container",
                        ".jobs-description-content__text"
                    ]
                    
                    # Also try to get a better title if it was missing
                    title_el = await page.query_selector("h1, .top-card-layout__title")
                    if title_el:
                        job_info["title"] = (await title_el.inner_text()).strip()
                        
                    company_el = await page.query_selector(".topcard__org-name-link, .top-card-layout__rel-model-indicator")
                    if company_el:
                        job_info["company"] = (await company_el.inner_text()).strip()

                    description = ""
                    for d_sel in desc_selectors:
                        desc_el = await page.query_selector(d_sel)
                        if desc_el:
                            description = await desc_el.inner_text()
                            break
                    
                    job_info["description"] = description
                    jobs.append(job_info)
                except Exception as e:
                    logger.warning(f"Failed to fetch detail for {job_info.get('title', 'Unknown')}: {e}")
                    # Only add if we have at least partial info
                    if job_info.get("linkedin_job_id"):
                        jobs.append(job_info)
            
            logger.info(f"Successfully scraped {len(jobs)} jobs total")
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
        finally:
            await browser.close()
            
    return jobs
