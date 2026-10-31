// Optional real-browser QA. Install Playwright for development only; the site
// itself has no npm dependencies. Serve the repository root before running.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),base=process.env.SCLD_URL||'http://127.0.0.1:8772/demos/SCLD/';
const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_EXECUTABLE?{executablePath:process.env.CHROME_EXECUTABLE}:{}),args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1080}}),errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
  await page.goto(base,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.querySelector('#screen').dataset.demo==='evolution');
  const data=JSON.parse(fs.readFileSync(path.join(root,'catalog.json')));
  assert(await page.locator('.demo-button').count()===12,'Twelve families');
  assert(await page.locator('iframe').count()===0,'Minimal player should not reload an iframe');
  const times=[];
  for(const d of data.families){
   const start=Date.now();await page.locator(`.demo-button[data-demo="${d.id}"]`).click();
   await page.waitForFunction(id=>document.querySelector('#screen').dataset.demo===id,d.id);times.push({id:d.id,clickToReadyMs:Date.now()-start});
   assert(await page.locator('#demo-title').innerText()===d.title,'Explanation follows selection');
   for(const v of d.variants){await page.selectOption('#variant',v.id);await page.waitForFunction(id=>document.querySelector('#screen').dataset.variant===id,v.id);assert((await page.locator('#cartridge-download').getAttribute('href'))===v.cartridge,'Variant download follows selection');}
  }
  await page.locator('.demo-button[data-demo="evolution"]').click();await page.waitForFunction(()=>document.querySelector('#screen').dataset.demo==='evolution');
  await page.click('#pause');const frame=await page.locator('#screen').getAttribute('data-frame');await page.waitForTimeout(150);assert(await page.locator('#screen').getAttribute('data-frame')===frame,'Pause stops the machine');await page.click('#pause');
  await page.waitForFunction(f=>document.querySelector('#screen').dataset.frame!==f,frame);
  // Last requested selection wins even if earlier promises resolve later.
  await page.evaluate(()=>{for(const id of ['atlas','evolution','macaw','triple'])document.querySelector(`.demo-button[data-demo="${id}"]`).click();});
  await page.waitForFunction(()=>document.querySelector('#screen').dataset.demo==='triple');assert(await page.locator('#demo-title').innerText()==='Triple Personality Mosaic','Rapid switch race');
  await page.locator('#screen').focus();await page.keyboard.press('ArrowRight');await page.waitForFunction(()=>document.querySelector('#screen').dataset.demo==='split');
  await page.goto(base+'?variant=push#probe',{waitUntil:'networkidle'});await page.waitForFunction(()=>document.querySelector('#screen').dataset.variant==='push');
  assert(await page.locator('#screen').getAttribute('data-crt')==='off','CRT remains off');
  assert(await page.evaluate(()=>getComputedStyle(document.querySelector('#screen')).filter==='none'&&!document.querySelector('#screen').getContext('2d').imageSmoothingEnabled),'Unfiltered nearest-neighbor Canvas');
  await page.click('#fullscreen');await page.waitForFunction(()=>Boolean(document.fullscreenElement));await page.evaluate(()=>document.exitFullscreen());
  const invalidLinks=await page.evaluate(async()=>{const links=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(h=>h&&!h.startsWith('http')&&!h.startsWith('#'));const bad=[];for(const h of links){const r=await fetch(h);if(!r.ok)bad.push([h,r.status]);}return bad;});assert(!invalidLinks.length,'Broken links '+JSON.stringify(invalidLinks));
  await page.goto(base+'#evolution',{waitUntil:'networkidle'});await page.waitForFunction(()=>document.querySelector('#screen').dataset.demo==='evolution');
  if(process.env.SCLD_SCREENSHOTS){fs.mkdirSync(process.env.SCLD_SCREENSHOTS,{recursive:true});await page.screenshot({path:path.join(process.env.SCLD_SCREENSHOTS,'desktop.png'),fullPage:true});}
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile horizontal overflow');
  await page.locator('.demo-button[data-demo="macaw"]').click();await page.waitForFunction(()=>document.querySelector('#screen').dataset.demo==='macaw');
  if(process.env.SCLD_SCREENSHOTS)await page.screenshot({path:path.join(process.env.SCLD_SCREENSHOTS,'mobile.png'),fullPage:true});
  await page.click('#native-space');await page.waitForTimeout(500);assert(await page.locator('#error').isHidden(),'On-screen native control');
  assert(!errors.length,'Browser errors '+JSON.stringify(errors));
  // A failed fetch must show an error and allow retry, not leave a stale
  // cartridge masquerading as the newly selected experiment.
  const failure=await browser.newPage();await failure.route('**/cartridges/split-personality-evolution.dck',r=>r.abort());await failure.goto(base);await failure.locator('#error').waitFor({state:'visible'});await failure.unroute('**/cartridges/split-personality-evolution.dck');await failure.click('#retry');await failure.waitForFunction(()=>document.querySelector('#screen').dataset.demo==='evolution',{},{timeout:5000}).catch(async e=>{console.error('Retry state',await failure.locator('#status').innerText(),await failure.locator('#error-detail').innerText());throw e;});await failure.close();
  const report={browser:await browser.version(),families:12,variants:18,crt:false,iframeCount:0,pauseResume:true,rapidSwitch:true,deepLinks:true,variantDownloads:true,keyboardNavigation:true,mobileNoHorizontalOverflow:true,fetchFailureRetry:true,fullscreen:true,nearestNeighbor:true,allLocalLinksOk:true,pageErrors:errors,switchChecks:times};
  fs.writeFileSync(path.join(root,'validation/gallery-browser.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
