const { chromium } = require(require('path').join(require('os').tmpdir(), 'trading-desk-ux-tools/node_modules/playwright'));
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Users/ME/AppData/Local/ms-playwright/chromium-1208/chrome-win64/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  for (const [route, name] of [['/', 'overview'], ['/learn', 'learn'], ['/paper','paper'], ['/nifty','nifty'], ['/maxpain','maxpain']]) {
    await page.goto('http://localhost:3000' + route, {waitUntil:'networkidle', timeout: 90000}).catch(async error => { if (!error.message.includes('Timeout')) throw error; });
    await page.waitForTimeout(1200);
    await page.screenshot({path:'artifacts/ux-review/' + name + '-desktop.png', fullPage:true});
    console.log(JSON.stringify({ route, title: await page.title(), heading:await page.locator('h1').innerText(), overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth), errors:[...errors] }));
  }
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
