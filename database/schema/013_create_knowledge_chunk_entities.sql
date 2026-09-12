CREATE TABLE knowledge_chunk_entities (
    chunk_id UUID NOT NULL,

    entity_id UUID NOT NULL,

    mention_type VARCHAR(50),

    PRIMARY KEY (chunk_id, entity_id),

    CONSTRAINT fk_chunk_entities_chunk
        FOREIGN KEY (chunk_id)
        REFERENCES knowledge_chunks(chunk_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_chunk_entities_entity
        FOREIGN KEY (entity_id)
        REFERENCES knowledge_entities(entity_id)
        ON DELETE CASCADE
);