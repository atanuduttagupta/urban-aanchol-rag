CREATE TABLE knowledge_document_entities (
    document_entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL,

    entity_id UUID NOT NULL,

    relationship_type VARCHAR(50) NOT NULL DEFAULT 'applies_to',

    priority INTEGER NOT NULL DEFAULT 0,

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_entities_document
        FOREIGN KEY (document_id)
        REFERENCES knowledge_documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_document_entities_entity
        FOREIGN KEY (entity_id)
        REFERENCES knowledge_entities(entity_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_document_entity_relation
        UNIQUE (document_id, entity_id, relationship_type)
);