const axios = require('axios');
require('dotenv').config();

const GITHUB_API = 'https://api.github.com';
const headers = {
  Authorization: `token ${process.env.GITHUB_TOKEN}`,
  'User-Agent': 'AI-Code-Reviewer',
};

async function getPullRequests() {
  try {
    const { data } = await axios.get(`${GITHUB_API}/repos/${process.env.GITHUB_REPO}/pulls`, { headers });
    return data;
  } catch (error) {
    console.error('Error fetching pull requests from GitHub:', error.message || error);
    throw error;
  }
}

async function getPullDiff(prNumber) {
  try {
    const { data } = await axios.get(
      `${GITHUB_API}/repos/${process.env.GITHUB_REPO}/pulls/${prNumber}`,
      { headers: { ...headers, Accept: 'application/vnd.github.v3.diff' } }
    );
    return data;
  } catch (error) {
    console.error(`Error fetching diff for PR #${prNumber} from GitHub:`, error.message || error);
    throw error;
  }
}

module.exports = { getPullRequests, getPullDiff };
