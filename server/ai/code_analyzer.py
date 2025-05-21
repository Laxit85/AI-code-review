import openai
import os
import logging
import time
import hashlib

# Import transformers and torch for open-source model
try:
    from transformers import pipeline
except ImportError:
    pipeline = None

openai.api_key = os.getenv("OPENAI_API_KEY")

# Toggle to use openai or open-source model
USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true"

_quota_exceeded_cooldown = 300  # seconds
_last_quota_exceeded_time = 0

# Simple in-memory cache for analysis results
_analysis_cache = {}

def analyze_code_open_source(code):
    if pipeline is None:
        return "request changes", "Error: transformers library not installed. Please install it to use open-source model."

    # Use a text-generation pipeline as a placeholder for code analysis
    generator = pipeline("text-generation", model="gpt2", max_length=512, truncation=True)
    prompt = f"Review the following code and provide feedback:\n\n{code}\n\nSummary, bugs, suggestions, verdict:"
    outputs = generator(prompt, max_length=512, num_return_sequences=1, truncation=True)
    content = outputs[0]['generated_text']
    # Simple heuristic to determine verdict
    if "no bugs" in content.lower() or "looks good" in content.lower():
        verdict = "approve"
    else:
        verdict = "request changes"
    return verdict, content

import re

def parse_ai_response(content):
    import logging
    # Initialize fields
    summary = ""
    bugs = ""
    suggestions = ""
    verdict = ""

    # Try to extract sections based on numbering or keywords with fallback
    summary_match = re.search(r"(?:1\.|Summary:)(.+?)(?=(?:2\.|Bugs:|$))", content, re.DOTALL | re.IGNORECASE)
    bugs_match = re.search(r"(?:2\.|Bugs:)(.+?)(?=(?:3\.|Suggestions:|$))", content, re.DOTALL | re.IGNORECASE)
    suggestions_match = re.search(r"(?:3\.|Suggestions:)(.+?)(?=(?:4\.|Verdict:|$))", content, re.DOTALL | re.IGNORECASE)
    verdict_match = re.search(r"(?:5\.|Verdict:)(.+)", content, re.DOTALL | re.IGNORECASE)

    if summary_match:
        summary = summary_match.group(1).strip()
    if bugs_match:
        bugs = bugs_match.group(1).strip()
    if suggestions_match:
        suggestions = suggestions_match.group(1).strip()
    if verdict_match:
        verdict = verdict_match.group(1).strip()

    # Clean verdict to standard values
    if "APPROVE" in verdict.upper():
        verdict = "approve"
    elif "REQUEST CHANGES" in verdict.upper():
        verdict = "request changes"
    else:
        verdict = "request changes"

    # If all fields empty, fallback to full content in summary
    if not (summary or bugs or suggestions or verdict):
        logging.warning("Failed to parse AI response, returning full content as summary")
        summary = content.strip()
        verdict = "request changes"

    return {
        "summary": summary,
        "bugs": bugs,
        "suggestions": suggestions,
        "verdict": verdict
    }

import logging

def analyze_code(code):
    global _last_quota_exceeded_time

    logging.info(f"Analyzing code:\n{code}")

    # Check cache first
    code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
    # Clear cache to force fresh analysis every time
    # if code_hash in _analysis_cache:
    #     logging.info("Returning cached analysis result")
    #     return _analysis_cache[code_hash]

    if USE_OPENAI:
        current_time = time.time()
        if current_time - _last_quota_exceeded_time < _quota_exceeded_cooldown:
            logging.error("OpenAI API quota exceeded cooldown active")
            return {
                "summary": "",
                "bugs": "",
                "suggestions": "",
                "verdict": "request changes",
                "error": "You have exceeded your OpenAI API quota. Please check your plan and billing details."
            }

        max_retries = 3
        backoff_factor = 2
        delay = 1  # initial delay in seconds

        for attempt in range(max_retries):
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"""You're a senior software engineer. Review the following code:\n\n{code}\n\nPlease provide:\n1. A summary of the code.\n2. Detailed list of bugs or issues, including line numbers or exact locations if possible.\n3. Suggestions for fixing the bugs.\n4. If the code has no bugs, provide a greeting message praising the code quality.\n5. Final Verdict: APPROVE or REQUEST CHANGES."""}],
                    temperature=0.2,
                )
                content = response.choices[0].message.content
                logging.info(f"OpenAI response content:\n{content}")
                parsed = parse_ai_response(content)
                _analysis_cache[code_hash] = parsed
                return parsed
            except openai.error.RateLimitError as e:
                logging.error(f"OpenAI API rate limit error on attempt {attempt + 1}: {str(e)}")
                _last_quota_exceeded_time = time.time()
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= backoff_factor
                else:
                    return {
                        "summary": "",
                        "bugs": "",
                        "suggestions": "",
                        "verdict": "request changes",
                        "error": "You have exceeded your OpenAI API quota. Please check your plan and billing details."
                    }
            except Exception as e:
                logging.error(f"OpenAI API error: {str(e)}")
                return {
                    "summary": "",
                    "bugs": "",
                    "suggestions": "",
                    "verdict": "request changes",
                    "error": f"Error during analysis: {str(e)}"
                }
    else:
        # Use open-source model
        verdict, content = analyze_code_open_source(code)
        logging.info(f"Open-source model response:\n{content}")
        parsed = {
            "summary": "",
            "bugs": content,
            "suggestions": "",
            "verdict": verdict
        }
        _analysis_cache[code_hash] = parsed
        return parsed
