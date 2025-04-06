import re

def safe_patch_slice(text, max_chars=3000):
    lines = text.splitlines(keepends=True)
    result = ""
    total = 0
    for line in lines:
        if total + len(line) > max_chars:
            break
        result += line
        total += len(line)
    return result

def escape_backticks(text):
    return text.replace("```", "`\u200b``")

def split_into_safe_chunks(text, chunk_size=3900):
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current += para + "\n\n"
        else:
            chunks.append(current.strip())
            current = para + "\n\n"
    if current:
        chunks.append(current.strip())
    return chunks

def sanitize_prompt_text(text):
    # Remove markdown & HTML tags
    clean = re.sub(r"[*`_>#]", "", text)
    clean = re.sub(r"<[^>]+>", "", clean)
    return clean.strip()
