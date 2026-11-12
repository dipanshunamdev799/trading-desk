const {chromium}=require(require('path').join(require('os').tmpdir(),'trading-desk-ux-tools/node_modules/playwright'));
const assert=require('node:assert/strict');
const net=require('node:net');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/ME/AppData/Local/ms-playwright/chromium-1208/chrome-win64/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:3000/',{waitUntil:'networkidle',timeout:60000});await page.getByRole('heading',{name:'Make sense of the market.'}).waitFor();
  await page.locator('.nav a[href="/learn"]').click();await page.waitForURL('http://localhost:3000/learn');await page.locator('#learn-exit').fill('80');assert.match(await page.locator('.learn-example-result strong').innerText(),/-₹100/);
  const health=await (await page.request.get('http://localhost:3000/api/health')).json();assert.equal(health.ok,true);assert.deepEqual(errors,[]);
  const listens=port=>new Promise(resolve=>{const socket=net.createConnection({host:'127.0.0.1',port});socket.setTimeout(1000);socket.on('connect',()=>{socket.destroy();resolve(true)});socket.on('error',()=>resolve(false));socket.on('timeout',()=>{socket.destroy();resolve(false)})});
  const oldPorts={3100:await listens(3100),3101:await listens(3101)};assert.deepEqual(oldPorts,{3100:false,3101:false});console.log(JSON.stringify({url:'http://localhost:3000/',updatedUI:true,learningCalculator:true,api:health.ok,oldPreviewPortsListening:oldPorts,runtimeErrors:errors}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
