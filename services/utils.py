import json
import re

def parse_llm_json(content: str):
    if not content:
        return []
    
    cleaned = content.strip()
    
    # If code fence is present anywhere in content (e.g. conversational preamble + ```json ... ```)
    if "```" in cleaned:
        # Extract between first ``` and next ```
        parts = cleaned.split("```")
        if len(parts) >= 2:
            fenced = parts[1].strip()
            if fenced.lower().startswith("json"):
                fenced = fenced[4:].strip()
            cleaned = fenced
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Secondary fallback: normalize problematic whitespace / newlines
        try:
            normalized = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            return json.loads(normalized)
        except json.JSONDecodeError as e:
            print(f"JSON parse failed: {e}")
            print(f"Raw content: {content}")
            return []
