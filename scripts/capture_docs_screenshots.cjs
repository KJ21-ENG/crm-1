const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE = 'https://eshin.in';
const USER = 'Administrator';
const PASS = 'Eshin123';

const shots = [
  'dashboard/01-overview:/crm/dashboard',
  'dashboard/02-date-range:/crm/dashboard',
  'dashboard/03-performance:/crm/dashboard',
  'leads/01-list-create:/crm/leads',
  'leads/02-list-filters:/crm/leads',
  'leads/03-list-actions:/crm/leads',
  'leads/04-detail-activity:/crm/leads',
  'leads/05-detail-calls:/crm/leads',
  'leads/06-detail-tasks:/crm/leads',
  'leads/07-status-mandatory:/crm/leads',
  'tickets/01-list-create:/crm/tickets',
  'tickets/02-priority-status:/crm/tickets',
  'tickets/03-sla:/crm/tickets',
  'customers/01-search:/crm/customers',
  'customers/02-profile-edit:/crm/customers',
  'customers/03-interactions:/crm/customers',
  'tasks/01-create:/crm/tasks',
  'tasks/02-status-flow:/crm/tasks',
  'tasks/03-reminders:/crm/tasks',
  'calllogs/01-list-overview:/crm/call-logs',
  'calllogs/02-filters:/crm/call-logs',
  'calllogs/03-detail-links:/crm/call-logs',
  'notes/01-create:/crm/notes',
  'notes/02-linked:/crm/notes',
  'support-pages/01-create:/crm/support-pages',
  'support-pages/02-send:/crm/support-pages',
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  page.setDefaultTimeout(60000);
  await page.setViewport({ width: 1512, height: 982 });

  await page.goto(`${BASE}/login?redirect-to=/crm`, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await sleep(1500);

  const userSel = 'input[name="usr"], input[type="text"]';
  const pwdSel = 'input[name="pwd"], input[type="password"]';
  await page.waitForSelector(userSel, { timeout: 30000 });
  await page.type(userSel, USER, { delay: 20 });
  await page.type(pwdSel, PASS, { delay: 20 });

  const btnSel = 'button[type="submit"], button.btn-login, .btn-login, .btn-primary';
  await page.click(btnSel);
  await sleep(5000);

  if (!page.url().includes('/crm')) {
    await page.goto(`${BASE}/crm`, { waitUntil: 'domcontentloaded', timeout: 90000 });
    await sleep(4000);
  }

  for (const row of shots) {
    const [name, route] = row.split(':');
    const out = path.join(__dirname, '..', 'frontend', 'public', 'docs', 'screenshots', `${name}.png`);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await page.goto(`${BASE}${route}`, { waitUntil: 'domcontentloaded', timeout: 90000 });
    await sleep(3500);
    await page.screenshot({ path: out, fullPage: true });
    console.log('saved', out);
  }

  await browser.close();
})();