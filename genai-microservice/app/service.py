from typing import List, Tuple

def generate_chat(prompt: str, system: str | None, max_tokens: int) -> Tuple[str, int, int, str]:
    text = f"{system + ': ' if system else ''}{prompt}".strip()
    in_tok = max(1, len(prompt) // 4)  # fake token count
    out_tok = min(max_tokens, 128)
    return text, in_tok, out_tok, "dummy-llm"

def embed_texts(texts: List[str]) -> Tuple[List[list[float]], int, str]:
    vecs = [[float(len(t) % 7), 0.0, 1.0] for t in texts]  # dummy 3-d vectors
    return vecs, 3, "dummy-embedder"
