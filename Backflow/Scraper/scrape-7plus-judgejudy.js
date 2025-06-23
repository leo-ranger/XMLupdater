const fs = require('fs');
const puppeteer = require('puppeteer');

(async () => {
  const url = 'https://7plus.com.au/live-tv?channel-id=JudgeJudy';

  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();

  await page.goto(url, { waitUntil: 'networkidle2' });

  // Wait for guide data to appear - adjust selector if needed
  await page.waitForSelector('.GuideListing-listItem', { timeout: 15000 });

  // Extract program guide entries
  const guide = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('.GuideListing-listItem'));
    return items.map(item => {
      const titleEl = item.querySelector('.GuideListing-title') || item.querySelector('.Listing-title');
      const timeEl = item.querySelector('.GuideListing-time') || item.querySelector('.Listing-time');
      return {
        title: titleEl ? titleEl.textContent.trim() : null,
        startTime: timeEl ? timeEl.textContent.trim() : null
      };
    }).filter(e => e.title && e.startTime);
  });

  await browser.close();

  // Save JSON file in Backflow/Scraper
  const outputDir = 'Backflow/Scraper';
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  fs.writeFileSync(`${outputDir}/7plus_JudgeJudy_guide.json`, JSON.stringify(guide, null, 2));

  console.log(`Saved ${guide.length} guide entries.`);
})();
