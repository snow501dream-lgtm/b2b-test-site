// Minimal static file server — zero URL rewriting
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = 8080;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

http.createServer((req, res) => {
  // Get URL path, strip query string and hash
  let rawUrl = req.url.split('?')[0].split('#')[0];

  // Default to /index.html
  if (rawUrl === '/' || rawUrl === '') {
    rawUrl = '/index.html';
  }

  // Build safe file path
  let filePath = path.join(ROOT, rawUrl);

  // Normalize separators to Windows backslash for comparison
  filePath = path.normalize(filePath);

  // Debug log
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
