// Minimal static file server + API routes
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const ROOT = __dirname;
const PORT = 8080;
const DATA_FILE = path.join(ROOT, 'data', 'submissions.json');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

// Ensure data directory
if (!fs.existsSync(path.join(ROOT, 'data'))) {
  fs.mkdirSync(path.join(ROOT, 'data'));
}

function readAll() {
  try {
    if (fs.existsSync(DATA_FILE)) return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch (_) {}
  return [];
}

function writeAll(list) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(list, null, 2));
}

function apiRouter(req, res) {
  const parsed = url.parse(req.url, true);
  const pathname = parsed.pathname;

  if (pathname !== '/api/submissions') return false;

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200); res.end(); return true;
  }

  // GET — list all
  if (req.method === 'GET') {
    if (parsed.query.key !== 'ads2024') {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Unauthorized' }));
      return true;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(readAll()));
    return true;
  }

  // POST — store
  if (req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const { name, email, company, product, message } = JSON.parse(body);
        if (!name || !email || !message) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          return res.end(JSON.stringify({ error: 'Missing fields' }));
        }
        const entry = {
          id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
          name, email, company, product, message,
          created_at: new Date().toISOString(),
        };
        const all = readAll();
        all.push(entry);
        writeAll(all);
        res.writeHead(201, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, id: entry.id }));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON' }));
      }
    });
    return true;
  }

  // DELETE — clear all
  if (req.method === 'DELETE') {
    if (parsed.query.key !== 'ads2024') {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Unauthorized' }));
      return true;
    }
    writeAll([]);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true }));
    return true;
  }

  res.writeHead(405); res.end(); return true;
}

http.createServer((req, res) => {
  // Try API routes first
  if (apiRouter(req, res)) return;

  // Get URL path, strip query string and hash
  let rawUrl = url.parse(req.url).pathname;

  // Default to /index.html
  if (rawUrl === '/' || rawUrl === '') {
    rawUrl = '/index.html';
  }

  // Build safe file path
  let filePath = path.join(ROOT, rawUrl);
  filePath = path.normalize(filePath);

  console.log(`${req.method} ${req.url} => ${filePath} (exists: ${fs.existsSync(filePath)})`);

  // Security: ensure file is inside ROOT
  if (!filePath.toLowerCase().startsWith(ROOT.toLowerCase())) {
    console.log('  -> 403 Forbidden');
    res.writeHead(403);
    return res.end('Forbidden');
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, data) => {
    if (err) {
      console.log(`  -> 404 Not Found (${err.code})`);
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end('<h1>404 Not Found</h1><p>The requested page does not exist.</p>');
    }
    console.log(`  -> 200 OK (${contentType})`);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}).listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
  console.log(`Root directory: ${ROOT}\n`);
});
