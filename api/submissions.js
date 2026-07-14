export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { recaptcha_token } = req.body || {};

  if (recaptcha_token) {
    const verify = await fetch(
      'https://www.google.com/recaptcha/api/siteverify',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          secret: process.env.RECAPTCHA_SECRET,
          response: recaptcha_token,
        }).toString(),
      }
    ).then(r => r.json());

    if (!verify.success || verify.score < 0.5) {
      return res.status(400).json({ error: 'Verification failed', score: verify.score });
    }
  }

  return res.status(200).json({ success: true, score: recaptcha_token ? 'verified' : 'skipped' });
}
