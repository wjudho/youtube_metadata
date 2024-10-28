from playwright.sync_api import sync_playwright 
import logging
from urllib.parse import urljoin 
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            # url = "https://www.youtube.com/@hacktracecyberwolves/videos"
            # url = "https://www.youtube.com/@ChecklyHQ/videos"
            # url = "https://www.youtube.com/@SharingPajakMNCo/videos"
            # url = "https://www.youtube.com/@gurugembul/videos"
            # url = "https://www.youtube.com/@BossmanMardigu/videos"
            url = "https://www.youtube.com/@TechWithTim/videos"
            username = url.split('@')[-1].split('/')[0]
            file = f"{username}.csv"
            page.goto(url)
            page.wait_for_load_state("networkidle")
            logger.info(f"{page.url}")
            scroll_count = 0
            while True:
                logger.info(f"Scrolling down to load more items...({scroll_count + 1})")
                page.evaluate("window.scrollBy(0, document.documentElement.scrollHeight);")
                page.wait_for_load_state("networkidle")
                
                continuation_element = page.query_selector("#contents > ytd-continuation-item-renderer")
                page.wait_for_load_state("networkidle")
                if continuation_element is None:
                    logger.info("Reached the end of the page. No more content to load.")
                    break
                scroll_count += 1
                
            title_links = page.query_selector_all("//*[@id='video-title']")
            view_links = page.query_selector_all("//*[@id='metadata-line']/span[1]")
            date_links = page.query_selector_all("//*[@id='metadata-line']/span[2]")
            url_links = page.query_selector_all("//*[@id='video-title-link']")
            base_url = "https://www.youtube.com/"
            logger.info(f"Found {len(title_links)} title links")
            logger.info(f"Found {len(view_links)} view links")
            logger.info(f"Found {len(date_links)} date links")
            logger.info(f"Found {len(url_links)} date links")
            
            titles = [title_link.text_content().strip() for title_link in title_links]
            views = [view_link.text_content().strip() for view_link in view_links] 
            date = [date_link.text_content().strip() for date_link in date_links]    
            urls = [urljoin(base_url, url_link.get_attribute("href")) for url_link in url_links]
            
            logger.info(f"Titles: {len(titles)}")
            logger.info(f"Views: {len(views)}")
            logger.info(f"Date: {len(date)}")
            logger.info(f"urls: {len(urls)}")
                
            logger.info("Finished scrolling. Creating DataFrame...")
            data = {'Title': titles, 'Views': views, 'Date': date, 'URL': urls}
            df = pd.DataFrame(data)
            
            df.to_csv(file, index=True, encoding='utf-8')
            logger.info("Saved to csv")

    except KeyboardInterrupt:
        logging.info("Script interrupted by user. Exiting...")
        browser.close()
            
        
if __name__ == "__main__":
    main()