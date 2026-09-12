CREATE TABLE knowledge_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    title VARCHAR(255) NOT NULL,

    document_type VARCHAR(50) NOT NULL,

    source VARCHAR(100) NOT NULL,

    source_url TEXT,

    language VARCHAR(20) NOT NULL DEFAULT 'en',

    status VARCHAR(20) NOT NULL DEFAULT 'Active'
        CHECK (status IN ('Active', 'Inactive', 'Draft', 'Archived')),

    priority INTEGER NOT NULL DEFAULT 0,

    effective_from DATE,

    effective_to DATE,

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);