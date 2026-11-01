// Percorso di Chromium per i video: CHROME se c'è, altrimenti il Chromium più recente in /opt/pw-browsers
// (nelle sessioni cloud la versione cambia: chromium-1194 nel 2026-10, chromium-1243 dal 2026-11).
const fs = require('fs');
module.exports = function chrome() {
  if (process.env.CHROME) return process.env.CHROME;
  const base = '/opt/pw-browsers';
  let dirs = [];
  try { dirs = fs.readdirSync(base).filter(n => /^chromium-\d+$/.test(n)).sort((a, b) => b.split('-')[1] - a.split('-')[1]); } catch (e) {}
  for (const d of dirs) for (const s of ['chrome-linux64/chrome', 'chrome-linux/chrome'])
    if (fs.existsSync(`${base}/${d}/${s}`)) return `${base}/${d}/${s}`;
  return undefined;   // playwright-core prova il suo percorso
};
