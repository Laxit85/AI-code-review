const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

async function runTestsForPR(prNumber) {
  const repoUrl = `https://github.com/${process.env.GITHUB_REPO}.git`;
  const dir = `/tmp/pr-${prNumber}-${Date.now()}`;

  return new Promise((resolve, reject) => {
    exec(`
      git clone ${repoUrl} ${dir} &&
      cd ${dir} &&
      npm install &&
      npm test
    `, (err, stdout, stderr) => {
      if (err) return reject(stderr);
      resolve({ output: stdout });
    });
  });
}

module.exports = { runTestsForPR };
