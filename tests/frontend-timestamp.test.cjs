const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const start = html.lastIndexOf('<script>');
const end = html.indexOf('</script>', start);
assert.ok(start >= 0 && end > start, 'Daily source feed script must exist');
const script = html.slice(start + '<script>'.length, end);

async function renderWith(daily, researched) {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {
      value: '', textContent: '', innerHTML: '', addEventListener() {},
    });
    return elements.get(id);
  };
  const document = {
    createElement: () => ({ id: '', style: '', innerHTML: '' }),
    body: { appendChild() {} },
    getElementById: element,
  };
  const fetch = async url => ({
    json: async () => url.includes('daily_sources.json') ? daily : researched,
  });
  vm.runInNewContext(script, { document, fetch, Date, URL }, { timeout: 2000 });
  await new Promise(resolve => setImmediate(resolve));
  return { status: element('live-source-status').textContent,
    items: element('live-source-items').innerHTML };
}

test('timestamp comes from daily JSON, not the Promise.all array', async () => {
  const data = {last_checked_utc: '2026-10-30T07:20:00+00:00', records: [{
    actor: 'Actor 1', platform: 'News', title: 'Daily record',
    url: 'https://example.com/1', published: '2026-10-30',
  }]};
  const researched = {updated: '2026-10-09', records: [{
    actor: 'Actor 2', platform: 'News', title: 'Research record',
    url: 'https://example.com/2', published: '2026-10-09',
  }]};
  const result = await renderWith(data, researched);
  assert.match(result.status, /Indexed links: 2/);
  assert.match(result.status, /2026-10-30T07:20:00\+00:00/);
  assert.doesNotMatch(result.status, /First run pending/);
  assert.match(result.items, /Daily record/);
  assert.match(result.items, /Research record/);
});

test('missing timestamp retains the pending fallback', async () => {
  const result = await renderWith({records: []}, {records: []});
  assert.match(result.status, /First run pending/);
});
