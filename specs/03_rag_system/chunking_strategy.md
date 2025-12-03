# Chunking Strategy

## 1. Chunk Size & Overlap
- **Algorithm**: Recursive Character Text Splitter.
- **Chunk Size**: 500 tokens (approx. 2000 characters).
    - *Rationale*: Large enough to contain a full paragraph/regulation, small enough to fit multiple chunks in context.
- **Overlap**: 50 tokens (approx. 200 characters).
    - *Rationale*: Ensures context isn't lost at split boundaries.

## 2. Boundary Handling
The splitter should respect the following hierarchy when splitting:
1.  `\n\n` (Paragraphs)
2.  `\n` (Lines)
3.  `. ` (Sentences)
4.  ` ` (Words)
5.  `` (Characters)

## 3. Special Content Handling
- **Tables**: Should ideally be kept together. If a table is larger than chunk size, it will be split, but the header should ideally be repeated (Future optimization). For MVP, standard text splitting is accepted.
- **Lists**: Keep list items together with their introductory sentence if possible.

## 4. Metadata Preservation
Each chunk must retain the metadata of its parent document:
- `source`: Filename
- `page`: Page number (critical for citations)
- `doc_type`: File extension

## 5. Quality Metrics
- **Coherence**: Does the chunk make sense on its own?
- **Completeness**: Does it cut off in the middle of a critical sentence?
- **Validation**: Random sampling of chunks during testing to verify readability.
