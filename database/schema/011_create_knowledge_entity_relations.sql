CREATE TABLE knowledge_entity_relations (
    relation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_entity_id UUID NOT NULL,

    target_entity_id UUID NOT NULL,

    relation_type VARCHAR(100) NOT NULL,

    weight DECIMAL(5,4),

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_relation_source
        FOREIGN KEY (source_entity_id)
        REFERENCES knowledge_entities(entity_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_relation_target
        FOREIGN KEY (target_entity_id)
        REFERENCES knowledge_entities(entity_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_entity_relation
        UNIQUE (source_entity_id, target_entity_id, relation_type),

    CONSTRAINT chk_no_self_relation
        CHECK (source_entity_id <> target_entity_id),

    CONSTRAINT chk_relation_weight
        CHECK (weight IS NULL OR (weight >= 0 AND weight <= 1))
);