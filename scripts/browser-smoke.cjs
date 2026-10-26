const {chromium}=require('../frontend/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.ORBITGUARD_CHROMIUM?{executablePath:process.env.ORBITGUARD_CHROMIUM}:{}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:5102');await page.getByRole('heading',{name:'Orbital theater'}).waitFor();
 await page.getByRole('button',{name:'Pause animation'}).click();await page.getByRole('slider',{name:'Simulation time'}).fill('45');await page.locator('.row').nth(2).click();await page.getByRole('slider',{name:'View tilt'}).fill('0.9');
 const canvas=page.locator('canvas');const before=await canvas.evaluate(c=>c.toDataURL());const box=await canvas.boundingBox();await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();await page.mouse.move(box.x+box.width/2+70,box.y+box.height/2,{steps:6});await page.mouse.up();await page.waitForTimeout(50);if(before===await canvas.evaluate(c=>c.toDataURL()))throw Error('3D rotation did not change rendered projection');
 if(await page.locator('.controls code').textContent()!=='T + 15.0 min')throw Error('time scrubber not connected');
 if(await page.locator('.row.active').count()!==1)throw Error('object selection not connected');
 await page.screenshot({path:'docs/images/app-screenshot.png',fullPage:true});await page.setViewportSize({width:390,height:844});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('mobile horizontal overflow');
 await page.screenshot({path:'docs/images/app-mobile.png',fullPage:true});if(errors.length)throw Error(errors.join('\n'));await browser.close();console.log('PASS: pause/scrub/object/tilt, desktop/mobile screenshot, no JS errors/overflow');
})().catch(e=>{console.error(e);process.exit(1)});
