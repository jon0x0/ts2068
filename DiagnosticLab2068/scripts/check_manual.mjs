import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require('C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{
 const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(process.cwd()+'/docs/manual/index.html').href);
 const chapterCount=JSON.parse(fs.readFileSync('docs/manual/content.json','utf8')).chapters.length;
 assert.equal(await page.locator('main section').count(),chapterCount+1);
 assert.equal(await page.locator('img').count(),9);
 assert.equal(await page.locator('img').evaluateAll(imgs=>imgs.every(i=>i.complete&&i.naturalWidth===768)),true);
 const pico=page.locator('section').filter({has:page.locator('h2',{hasText:'PicoROM: download and program'})});
 assert.equal(await pico.locator('pre code').count(),3);
 assert.equal(await pico.locator('pre code').nth(1).textContent(),'.\\picorom.exe upload 2068 -s diagnostic-v02-picorom.bin 512KBit');
 assert.equal(await pico.locator('a[href="https://github.com/wickerwaka/PicoROM/releases"]').count(),1);
 await page.locator('#chip').selectOption('6');await page.locator('#bit').selectOption('2');
 assert.match(await page.locator('#decoded').textContent(),/U18 path: D5/);
 await page.screenshot({path:'tmp/pdfs/web-desktop.png'});
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.screenshot({path:'tmp/pdfs/web-mobile.png'});
 assert.deepEqual(errors,[]);
 fs.writeFileSync('build/manual-verification.json',JSON.stringify({result:'PASS',offline:true,sections:chapterCount+1,actual_capture_images:9,decoder:'chip6/bit2=U18D5',layouts:['1280x900','390x844'],javascript_errors:errors},null,2)+'\n');
 console.log('Offline manual images, decoder and desktop/mobile layouts PASS');
}finally{await browser.close();}

