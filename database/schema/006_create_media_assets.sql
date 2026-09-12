CREATE TABLE media_assets (
    media_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    media_type VARCHAR(20) NOT NULL
        CHECK (media_type IN (
            'image',
            'video',
            'audio'
        )),

    media_url TEXT NOT NULL,
    thumbnail_url TEXT,

    title VARCHAR(255),
    description TEXT,

    source VARCHAR(100),

    published_at TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL DEFAULT 'Active'
        CHECK (status IN (
            'Active',
            'Inactive'
        )),

    sort_order INTEGER NOT NULL DEFAULT 0,

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);