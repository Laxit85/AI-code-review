const { getPullDiff } = require('./github');
const parseDiff = require('parse-diff');
const axios = require('axios');

async function analyzePRDiff(prNumber) {
  const diffText = await getPullDiff(prNumber);
  const files = parseDiff(diffText);
  const results = [];

  for (const file of files) {
    const code = file.chunks.map(chunk => chunk.content).join('\n');

    if (code.trim().length === 0) continue;

    const { data } = await axios.post('http://localhost:5000/analyze', { code });

    results.push({
      file: file.to,
      verdict: data.verdict,
      feedback: data.feedback,
    });
  }

  return results;
}

module.exports = { analyzePRDiff };
