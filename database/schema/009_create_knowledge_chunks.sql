CREATE TABLE knowledge_chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL,

    chunk_text TEXT NOT NULL,

    chunk_index INTEGER NOT NULL,

    section_title VARCHAR(255),

    content_type VARCHAR(50) NOT NULL DEFAULT 'text',

    language VARCHAR(20) NOT NULL DEFAULT 'en',

    token_count INTEGER,

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_knowledge_chunks_document
        FOREIGN KEY (document_id)
        REFERENCES knowledge_documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_knowledge_chunk_index
        UNIQUE (document_id, chunk_index),

    CONSTRAINT chk_knowledge_chunk_index
        CHECK (chunk_index >= 0),

    CONSTRAINT chk_knowledge_chunk_token_count
        CHECK (token_count IS NULL OR token_count >= 0)
);