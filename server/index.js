const express = require('express');
const cors = require('cors');
const axios = require('axios');
const { getPullRequests, getPullDiff } = require('./github');

const app = express();
const PORT = 4000;

app.use(cors());
app.use(express.json());

app.get('/api/pulls', async (req, res) => {
  try {
    const pulls = await getPullRequests();
    res.json(pulls);
  } catch (error) {
    console.error('Error fetching pull requests:', error);
    res.status(500).json({ error: 'Failed to fetch pull requests' });
  }
});

app.get('/api/pulls/:prNumber/diff', async (req, res) => {
  const prNumber = req.params.prNumber;
  try {
    const diff = await getPullDiff(prNumber);
    res.send(diff);
  } catch (error) {
    console.error(`Error fetching diff for PR #${prNumber}:`, error);
    res.status(500).json({ error: 'Failed to fetch pull request diff' });
  }
});

app.post('/api/analyze', async (req, res) => {
  const { code } = req.body;
  if (!code) {
    return res.status(400).json({ error: 'Code is required for analysis' });
  }
  try {
    const response = await axios.post('http://localhost:5000/analyze', { code });
    console.log('Python service response:', response.data);
    if (response.data.error) {
      return res.status(500).json({ error: response.data.error });
    }
    res.json(response.data);
  } catch (error) {
    console.error('Error analyzing code:', error);
    if (error.response && error.response.data && error.response.data.error) {
      return res.status(error.response.status || 500).json({ error: error.response.data.error });
    }
    res.status(500).json({ error: 'Failed to analyze code' });
  }
});

app.listen(PORT, () => {
  console.log(`GitHub API proxy server running on port ${PORT}`);
});
