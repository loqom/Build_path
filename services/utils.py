import json
import re

def parse_llm_json(content: str):
    content = content.strip()
    if not content:
        return []
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        content = content.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON parse failed: {e}")
            print(f"Raw content: {content[:300]}")
            return []
