CREATE TABLE knowledge_entities (
    entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    entity_type VARCHAR(50) NOT NULL,

    entity_key VARCHAR(150) NOT NULL,

    entity_name VARCHAR(255) NOT NULL,

    description TEXT,

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_knowledge_entity
        UNIQUE (entity_type, entity_key)
);