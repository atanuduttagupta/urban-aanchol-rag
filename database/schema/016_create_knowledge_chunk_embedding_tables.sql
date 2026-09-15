CREATE TABLE knowledge_chunk_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    dimensions INTEGER NOT NULL,
    embedding VECTOR(384) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_knowledge_chunk_embeddings_chunk
        FOREIGN KEY (chunk_id)
        REFERENCES knowledge_chunks(chunk_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_knowledge_chunk_embeddings_dimensions
        CHECK (dimensions = 384),

    CONSTRAINT uq_knowledge_chunk_embeddings_model
        UNIQUE (chunk_id, model_name, model_version)
);