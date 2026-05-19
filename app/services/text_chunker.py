class TextChunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ) -> None:
        # Chunk size controls retrieval granularity; overlap preserves context
        # between adjacent chunks.
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        # Normalize the input first so empty or whitespace-only content exits fast.
        text = text.strip()

        if not text:
            return []

        chunks: list[str] = []
        start = 0

        while start < len(text):
            # Slice the next window, keep it if it contains content, then move
            # forward with overlap so neighboring chunks share context.
            end = start + self.chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

            if start < 0:
                start = 0

            if start >= len(text):
                break

        return chunks