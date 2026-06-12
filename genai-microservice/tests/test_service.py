from app.service import generate_chat, embed_texts

def test_chat_basic():
    text, in_tok, out_tok, model = generate_chat("hello", None, 64)
    assert "hello" in text and in_tok > 0 and out_tok <= 64 and isinstance(model, str)

def test_embed_basic():
    vecs, dim, _ = embed_texts(["abc", "defg"]) #model is _
    assert len(vecs) == 2 and dim == 3
