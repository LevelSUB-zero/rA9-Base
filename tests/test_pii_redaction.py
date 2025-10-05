from ra9.memory.memory_manager import get_memory_manager


def test_pii_redaction_basic_regex():
    mm = get_memory_manager()
    text = "Contact me at john.doe@example.com or +1-555-234-5678"
    mem_id = mm.write_memory("episodic", text, tags=["pii"], importance=0.6, consent=True)
    # read back stored raw_text is encrypted or redacted; we cannot decrypt here, but chunk_text should be redacted
    c = mm.conn.cursor()
    row = c.execute("SELECT chunk_text FROM embeddings WHERE memory_id=? ORDER BY position ASC LIMIT 1", (mem_id,)).fetchone()
    assert row and "[email]" in row[0] or "[phone]" in row[0]

