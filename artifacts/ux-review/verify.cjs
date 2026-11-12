const { chromium } = require(require('path').join(require('os').tmpdir(), 'trading-desk-ux-tools/node_modules/playwright'));
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/ME/AppData/Local/ms-playwright/chromium-1208/chrome-win64/chrome.exe'});
 const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 const page=await context.newPage(); const errors=[], checks=[]; page.on('pageerror',e=>errors.push(e.message));
 const base='http://localhost:3000';
 page.setDefaultTimeout(15000);
 const go=async route=>{await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:90000});await page.locator('h1').waitFor();await page.waitForFunction(()=>document.title.includes('· Trading Desk'));await page.waitForTimeout(750)};
 const pass=name=>{checks.push(name);console.log('PASS '+name)};
 await page.route('**/api/**',route=>{if(!['GET','HEAD','OPTIONS'].includes(route.request().method())){throw new Error('Unexpected mutation '+route.request().url())}return route.continue()});
 await go('/');
 await page.keyboard.press('Control+k');await page.locator('.desk-search-dialog[open]').waitFor();
 await page.getByRole('textbox',{name:'Find a tool',exact:true}).fill('paper');
 await page.locator('.desk-search-results a[href="/paper"]').click();
 await page.waitForURL('**/paper');pass('Tool search opens the selected route');
 await page.locator('#paper-quantity').fill('0');assert(await page.getByRole('button',{name:'Place paper buy',exact:true}).isDisabled());
 await page.locator('#paper-quantity').fill('1.5');assert(await page.getByRole('button',{name:'Place paper buy',exact:true}).isDisabled());
 await page.locator('#paper-quantity').fill('1');
 await page.locator('#paper-instrument').selectOption('NSE_EQ|INE467B01029');assert.match(await page.locator('.paper-review').innerText(),/TCS/);
 await page.locator('#paper-order-type').selectOption('LIMIT');assert(await page.getByRole('button',{name:'Place paper buy',exact:true}).isDisabled());
 await page.locator('#paper-limit-price').fill('100');assert(await page.getByRole('button',{name:'Place paper buy',exact:true}).isEnabled());
 assert.match(await page.locator('#paper-type-help').innerText(),/immediately/);
 await page.locator('#paper-instrument').selectOption('custom');assert(await page.getByRole('button',{name:'Place paper buy',exact:true}).isDisabled());
 await page.locator('#paper-custom-key').fill('NSE_INDEX|Nifty 50');assert(await page.getByRole('button',{name:'Place paper buy',exact:true}).isEnabled());
 pass('Paper order review and invalid quantities/custom keys/price validation, without placing orders');
 await page.locator('.desk-page-guide summary').click();assert(await page.getByRole('heading',{name:'Try this workflow'}).isVisible());
 await page.getByRole('link',{name:'Practise the P&L calculation'}).click();await page.waitForURL('**/learn#learn-playground');assert(await page.locator('#learn-playground').isVisible());pass('Context guide links reach real learning sections');
 await page.locator('#learn-exit').fill('80');assert.match(await page.locator('.learn-example-result strong').innerText(),/-₹100/);
 await page.locator('#learn-quantity').fill('0');assert.equal(await page.locator('.learn-example-result strong').innerText(),'—');
 await page.locator('#learn-quantity').fill('');assert.equal(await page.locator('.learn-example-result strong').innerText(),'—');
 await page.locator('#learn-quantity').fill('1.5');assert.equal(await page.locator('.learn-example-result strong').innerText(),'—');
 await page.locator('#learn-quantity').fill('5');
 await page.locator('#learn-term-query').fill('zzzx');assert(await page.locator('.learn-no-terms').isVisible());
 await page.getByRole('button',{name:'Clear search',exact:true}).click();assert.equal(await page.locator('.learn-term-grid > div').count(),16);
 await page.locator('#learn-term-query').fill('drawdown');assert.equal(await page.locator('.learn-term-grid dt').innerText(),'Drawdown');pass('Offline P&L calculator and searchable glossary');
 for (const id of ['paper-1','paper-2','paper-3']) await page.locator('#'+id).check();
 await page.reload({waitUntil:'domcontentloaded'});await page.waitForTimeout(500);assert(await page.locator('#paper-3').isChecked());
 const secondLearn=await context.newPage();await secondLearn.goto(base+'/learn',{waitUntil:'domcontentloaded'});await secondLearn.locator('#observe-1').check();await page.locator('#backtest-1').check();await secondLearn.waitForTimeout(150);assert(await secondLearn.locator('#backtest-1').isChecked());assert(await page.locator('#observe-1').isChecked());await secondLearn.close();pass('Learning checklist merges and syncs changes across tabs');
 await go('/');assert.equal(await page.locator('.overview-path-items .is-complete').count(),1);assert.match(await page.locator('.overview-path-items .is-complete').innerText(),/Practise/);pass('Learning progress persists and marks the correct chapter');
 await go('/nifty');assert.equal(await page.locator('#nifty-factor-map').count(),0);
 await page.getByRole('button',{name:'What else affects the market?',exact:false}).click();await page.locator('#nifty-factor-map').waitFor();
 assert.equal(await page.getByRole('button',{name:'Full research',exact:true}).getAttribute('aria-pressed'),'true');
 await page.getByRole('button',{name:'Overview',exact:true}).click();assert.equal(await page.locator('#nifty-factor-map').count(),0);pass('NIFTY research expands on demand and returns to overview');
 await go('/maxpain');assert.equal(await page.locator('.maxpain-more-options').getAttribute('open'),null);assert(await page.locator('#maxpain-underlying').isVisible());assert(!await page.locator('#maxpain-search').isVisible());
 await page.locator('.maxpain-more-options summary').click();assert(await page.locator('#maxpain-search').isVisible());pass('Options secondary controls are disclosed on demand');
 const selectedUnderlying=await page.locator('#maxpain-underlying').inputValue();
 for(const name of ['Volatility','Option Greeks','Hypothetical P&L','History','Positioning']) { await page.getByRole('group',{name:'Options analysis views'}).getByRole('button',{name,exact:true}).click(); assert.equal(await page.locator('#maxpain-underlying').inputValue(), selectedUnderlying); assert.equal(await page.locator('#maxpain-analysis-content').getAttribute('aria-label'),name+' analysis'); }
 pass('All five options analysis views are reachable and preserve shared selections');
 await go('/backtests?slug=sample-momentum-nifty');await page.getByRole('button',{name:'Sample Momentum Nifty',exact:true}).waitFor();assert.equal(await page.getByRole('button',{name:'Sample Momentum Nifty',exact:true}).getAttribute('aria-pressed'),'true');pass('Sample backtest is keyboard accessible and selected from deep link');
 await page.setViewportSize({width:390,height:844});await go('/');
 const trigger=page.getByRole('button',{name:'Open navigation',exact:true});await trigger.click();await page.waitForTimeout(250);
 assert.equal(await page.locator('#desk-navigation').getAttribute('aria-modal'),'true');assert(await page.locator('.main').evaluate(e=>e.inert));
 assert(await page.locator('#desk-navigation').evaluate(e=>e.contains(document.activeElement)));
 for(let n=0;n<24;n++){await page.keyboard.press('Tab');assert(await page.locator('#desk-navigation').evaluate(e=>e.contains(document.activeElement)))}
 await page.keyboard.press('Escape');assert.equal(await trigger.getAttribute('aria-expanded'),'false');assert(await trigger.evaluate(e=>e===document.activeElement));pass('Mobile navigation traps focus, closes with Escape and restores focus');
 await trigger.click();await page.keyboard.press('Control+k');await page.locator('.desk-search-dialog[open]').waitFor();assert.equal(await trigger.getAttribute('aria-expanded'),'false');assert(await page.getByRole('textbox',{name:'Find a tool',exact:true}).evaluate(e=>e===document.activeElement));await page.keyboard.press('Escape');assert.equal(await page.locator('.desk-search-dialog').getAttribute('open'),null);pass('Tool search opens from the mobile menu and closes with Escape');
 await trigger.click();await page.locator('.desk-advanced-toggle').click();await page.getByRole('link',{name:'Data & connections',exact:true}).click();await page.waitForURL('**/data');assert.equal(await page.locator('.desk-mobile-menu').getAttribute('aria-expanded'),'false');pass('Advanced tools remain reachable on mobile');
 await page.evaluate(()=>localStorage.setItem('trading-desk.learn-progress.v1','{broken'));await go('/learn');assert.equal(await page.locator('.learn-page input[type=checkbox]:checked').count(),0);pass('Malformed saved progress falls back to an empty checklist');
 const offline=await context.newPage();await offline.route('**/api/**',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Offline QA fixture'})}));
 await offline.goto(base,{waitUntil:'domcontentloaded'});await offline.waitForTimeout(1300);assert.match(await offline.locator('.overview-practice-value').innerText(),/connection unavailable/);assert.equal(await offline.locator('.overview-practice-stats strong').first().innerText(),'—');assert(await offline.getByRole('link',{name:/Start learning|Continue learning/}).isVisible());
 await offline.goto(base+'/learn',{waitUntil:'domcontentloaded'});await offline.locator('#learn-exit').fill('80');assert.match(await offline.locator('.learn-example-result strong').innerText(),/-₹100/);pass('Unavailable API never invents zero balances and local exercises remain usable');
 const layout=[];
 for(const width of [1440,1024,768,390,320]){
   await page.setViewportSize({width,height:width<600?844:1000});
   for(const [route,name] of [['/','overview'],['/learn','learn'],['/paper','paper'],['/nifty','nifty'],['/maxpain','maxpain'],['/backtests?slug=sample-momentum-nifty','backtests']]){
     await go(route);
     const overflow=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));layout.push({route,width,...overflow});
     if(overflow.scroll>width+1) console.log('OVERFLOW '+JSON.stringify({route,width,...overflow}));
     if(width===390)await page.screenshot({path:'artifacts/ux-review/'+name+'-mobile.png',fullPage:true});
   }
 }
 const limitedContext=await browser.newContext({viewport:{width:390,height:844}});await limitedContext.addInitScript(()=>{Storage.prototype.setItem=function(){throw new DOMException('Quota exceeded','QuotaExceededError')}});const limited=await limitedContext.newPage();await limited.goto(base+'/learn',{waitUntil:'domcontentloaded'});await limited.locator('#observe-1').check();await limited.locator('#observe-2').check();assert(await limited.locator('#observe-1').isChecked());assert(await limited.locator('#observe-2').isChecked());await limitedContext.close();pass('Learning exercises keep all local progress when browser storage rejects writes');
 assert.deepEqual(layout.filter(x=>x.scroll>x.width+1),[]);pass('No horizontal page overflow from 320px through 1440px');
 assert.deepEqual(errors,[]);pass('No browser runtime errors');
 fs.writeFileSync('artifacts/ux-review/verification.json',JSON.stringify({checks,layout,errors},null,2));
 console.log(JSON.stringify({checks:checks.length,overflow:layout.filter(x=>x.scroll>x.width+1),errors}));await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
