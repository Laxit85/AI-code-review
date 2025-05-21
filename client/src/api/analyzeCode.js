export async function analyzeCode(code) {
  try {
    const response = await fetch('http://localhost:4000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code })
    });
    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error calling analyze API:", error);
    throw error;
  }
}
