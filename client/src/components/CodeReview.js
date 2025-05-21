import React, { useState } from 'react';
import { analyzeCode } from '../api/analyzeCode';

function CodeReview() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const analysis = await analyzeCode(code);
      setResult(analysis);
    } catch (err) {
      setError('Failed to analyze code');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictClass = (verdict) => {
    if (!verdict) return '';
    const v = verdict.toLowerCase().replace(/\s/g, '-');
    return `review-result verdict-${v}`;
  };

  return (
    <div className="section">
      <h2>Code Review</h2>
      <textarea
        className="code-input"
        rows={10}
        cols={80}
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Paste your code here"
      />
      <br />
      <button
        className="submit-button"
        onClick={handleAnalyze}
        disabled={loading || !code.trim()}
      >
        {loading ? 'Analyzing...' : 'Analyze Code'}
      </button>
      {error && <p className="error-message">{error}</p>}
      {result && (
        <div className={getVerdictClass(result.verdict)}>
          <h3>Analysis Result</h3>
          <p><strong>Summary:</strong> {result.summary}</p>
          <p><strong>Bugs:</strong></p>
          <pre className="code-block">{result.bugs}</pre>
          <p><strong>Suggestions:</strong></p>
          <pre className="code-block">{result.suggestions}</pre>
          <p><strong>Verdict:</strong> {result.verdict}</p>
        </div>
      )}
    </div>
  );
}

export default CodeReview;
