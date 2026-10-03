// cattura i fotogrammi di KEY/video.html e li codifica in KEY/frames.mp4
const { chromium } = require('playwright-core'); const { spawn } = require('child_process');
(async () => {
  const K = process.env.KEY;
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--force-color-profile=srgb','--font-render-hinting=none','--disable-lcd-text'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('ERR', e.message));
  await p.goto('file://' + process.cwd() + '/' + K + '/video.html?render=1'); await p.waitForFunction('window.__ready === true');
  const T = await p.evaluate('window.TOTAL'); const n = Math.round(T*30)+1;
  const ff = spawn(process.env.FF, ['-v','error','-y','-f','image2pipe','-framerate','30','-c:v','png','-i','-','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-preset','medium','-crf','18','-profile:v','high','-level','4.1','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',K+'/frames.mp4'], { stdio: ['pipe','inherit','inherit'] });
  for (let i=0;i<n;i++){ await p.evaluate(`window.renderFrame(${i/30})`); const buf = await p.screenshot({ type:'png' }); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('FATTO');
})();
