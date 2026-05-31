// Vercel serverless function — simple submission store
const fs = require('fs');

const DATA_FILE = '/tmp/submissions.json';

function readAll() {
  try {
    if (fs.existsSync(DATA_FILE)) {
      return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    }
  } catch (_) { /* ignore */ }
  return [];
}

function writeAll(list) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(list, null, 2));
}

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // GET — list all submissions (simple key auth)
  if (req.method === 'GET') {
    const key = req.query?.key || '';
    if (key !== 'ads2024') {
      return res.status(401).json({ error: 'Unauthorized. Add ?key=ads2024 to the URL.' });
    }
    return res.status(200).json(readAll());
  }

  // POST — store a new submission
  if (req.method === 'POST') {
    const { name, email, company, product, message } = req.body || {};
    if (!name || !email || !message) {
      return res.status(400).json({ error: 'name, email, and message are required' });
    }
    const entry = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      name, email, company, product, message,
      created_at: new Date().toISOString(),
    };
    const all = readAll();
    all.push(entry);
    writeAll(all);
    return res.status(201).json({ success: true, id: entry.id });
  }

  // DELETE — clear all submissions
  if (req.method === 'DELETE') {
    const key = req.query?.key || '';
    if (key !== 'ads2024') {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    writeAll([]);
    return res.status(200).json({ success: true, message: 'All submissions cleared' });
  }

  return res.status(405).json({ error: 'Method not allowed' });
};
