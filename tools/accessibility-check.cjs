const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const axe = require.resolve('axe-core/axe.min.js');
(async () => {
 const browser = await chromium.launch({headless:true});
 try {
  const page = await browser.newPage();
  for (const width of [390,1440]) {
   await page.setViewportSize({width,height:900});
   for (const name of ['index','about','solutions','products','projects','certifications','contact','quote','products.html#p-27']) {
    const path = name.includes('.html') ? name : name + '.html';
    await page.goto((process.env.SITE_URL || 'http://127.0.0.1:8080') + '/' + path);
    await page.addScriptTag({path:axe});
    const violations = await page.evaluate(async () => (await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','best-practice']}})).violations.map(v => ({id:v.id,nodes:v.nodes.map(n=>n.target)})));
    assert.deepEqual(violations,[],`${path} at ${width}px`);
   }
  }
  console.log('PASS: automated WCAG A/AA checks on eight pages and product dialog at mobile and desktop widths.');
 } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
