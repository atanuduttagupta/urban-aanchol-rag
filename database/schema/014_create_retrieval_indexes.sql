-- =========================================================
-- Urban Aanchol
-- Day 5 - Retrieval-Oriented Database Indexes
-- =========================================================

-- ---------------------------------------------------------
-- PRODUCTS
-- ---------------------------------------------------------

CREATE INDEX idx_products_category
    ON products (category);

CREATE INDEX idx_products_fabric
    ON products (fabric);

CREATE INDEX idx_products_colour
    ON products (colour);

CREATE INDEX idx_products_brand
    ON products (brand);

CREATE INDEX idx_products_collection
    ON products (collection);

CREATE INDEX idx_products_availability
    ON products (availability);

CREATE INDEX idx_products_price
    ON products (price);


-- ---------------------------------------------------------
-- PRODUCT MULTI-VALUE TABLES
-- ---------------------------------------------------------

CREATE INDEX idx_product_occasions_occasion
    ON product_occasions (occasion);

CREATE INDEX idx_product_styles_style
    ON product_styles (style);

CREATE INDEX idx_product_moods_mood
    ON product_moods (mood);

CREATE INDEX idx_product_tags_tag
    ON product_tags (tag);


-- ---------------------------------------------------------
-- MEDIA
-- ---------------------------------------------------------

CREATE INDEX idx_media_assets_type_status
    ON media_assets (media_type, status);

CREATE INDEX idx_product_media_product
    ON product_media (product_id);

CREATE INDEX idx_product_media_media
    ON product_media (media_id);


-- ---------------------------------------------------------
-- KNOWLEDGE DOCUMENTS
-- ---------------------------------------------------------

CREATE INDEX idx_knowledge_documents_type_status
    ON knowledge_documents (document_type, status);

CREATE INDEX idx_knowledge_documents_status_priority
    ON knowledge_documents (status, priority DESC);


-- ---------------------------------------------------------
-- KNOWLEDGE CHUNKS
-- ---------------------------------------------------------

CREATE INDEX idx_knowledge_chunks_document
    ON knowledge_chunks (document_id);


-- ---------------------------------------------------------
-- KNOWLEDGE ENTITIES
-- ---------------------------------------------------------

CREATE INDEX idx_knowledge_entities_type
    ON knowledge_entities (entity_type);

CREATE INDEX idx_knowledge_entities_name
    ON knowledge_entities (entity_name);


-- ---------------------------------------------------------
-- GRAPH RELATIONSHIPS
-- ---------------------------------------------------------

CREATE INDEX idx_entity_relations_source
    ON knowledge_entity_relations (source_entity_id);

CREATE INDEX idx_entity_relations_target
    ON knowledge_entity_relations (target_entity_id);

CREATE INDEX idx_entity_relations_type
    ON knowledge_entity_relations (relation_type);


-- ---------------------------------------------------------
-- DOCUMENT ↔ ENTITY
-- ---------------------------------------------------------

CREATE INDEX idx_document_entities_document
    ON knowledge_document_entities (document_id);

CREATE INDEX idx_document_entities_entity
    ON knowledge_document_entities (entity_id);

CREATE INDEX idx_document_entities_relationship
    ON knowledge_document_entities (relationship_type);


-- ---------------------------------------------------------
-- CHUNK ↔ ENTITY
-- ---------------------------------------------------------

CREATE INDEX idx_chunk_entities_entity
    ON knowledge_chunk_entities (entity_id);