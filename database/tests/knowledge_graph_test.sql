BEGIN;

-- =========================================================
-- 1. Create representative entities
-- =========================================================

INSERT INTO knowledge_entities
    (entity_type, entity_key, entity_name, description)
VALUES
    ('business', 'urban-aanchol', 'Urban Aanchol',
        'Urban Aanchol boutique'),

    ('product', 'UA-0001', 'White & Grey Handloom Saree',
        'Representative product entity'),

    ('fabric', 'handloom-cotton', 'Handloom Cotton',
        'Representative fabric entity'),

    ('occasion', 'wedding', 'Wedding',
        'Representative occasion entity'),

    ('style', 'traditional', 'Traditional',
        'Representative style entity'),

    ('topic', 'washing', 'Saree Washing',
        'Representative care topic'),

    ('topic', 'colour-fading', 'Colour Fading',
        'Representative complaint topic');

-- =========================================================
-- 2. Create representative knowledge documents
-- =========================================================

INSERT INTO knowledge_documents
    (title, document_type, source, language, status, priority)
VALUES
    ('UA-0001 Care Instructions',
        'PRODUCT_CARE', 'Urban Aanchol', 'en', 'Active', 100),

    ('Handloom Cotton Care Guide',
        'CARE_GUIDE', 'Urban Aanchol', 'en', 'Active', 50),

    ('Return and Cancellation Policy',
        'POLICY', 'Urban Aanchol', 'en', 'Active', 100),

    ('Bengali Wedding Saree Guide',
        'SAREE_GUIDE', 'Urban Aanchol', 'en', 'Active', 30);

-- =========================================================
-- 3. Create representative chunks
-- =========================================================

INSERT INTO knowledge_chunks
    (document_id, chunk_text, chunk_index, section_title)
SELECT
    document_id,
    'UA-0001 should be washed separately using a mild detergent and dried in shade.',
    0,
    'Washing Instructions'
FROM knowledge_documents
WHERE title = 'UA-0001 Care Instructions';

INSERT INTO knowledge_chunks
    (document_id, chunk_text, chunk_index, section_title)
SELECT
    document_id,
    'Handloom cotton sarees should generally be handled gently and harsh detergents should be avoided.',
    0,
    'General Care'
FROM knowledge_documents
WHERE title = 'Handloom Cotton Care Guide';

INSERT INTO knowledge_chunks
    (document_id, chunk_text, chunk_index, section_title)
SELECT
    document_id,
    'Returns and cancellations are subject to the current Urban Aanchol policy.',
    0,
    'Policy'
FROM knowledge_documents
WHERE title = 'Return and Cancellation Policy';

INSERT INTO knowledge_chunks
    (document_id, chunk_text, chunk_index, section_title)
SELECT
    document_id,
    'Traditional sarees can be suitable choices for Bengali wedding occasions.',
    0,
    'Wedding Style'
FROM knowledge_documents
WHERE title = 'Bengali Wedding Saree Guide';

-- =========================================================
-- 4. Connect documents to applicable entities
-- =========================================================

INSERT INTO knowledge_document_entities
    (document_id, entity_id, relationship_type, priority)
SELECT d.document_id, e.entity_id, 'applies_to', 100
FROM knowledge_documents d
CROSS JOIN knowledge_entities e
WHERE d.title = 'UA-0001 Care Instructions'
  AND e.entity_type = 'product'
  AND e.entity_key = 'UA-0001';

INSERT INTO knowledge_document_entities
    (document_id, entity_id, relationship_type, priority)
SELECT d.document_id, e.entity_id, 'applies_to', 50
FROM knowledge_documents d
CROSS JOIN knowledge_entities e
WHERE d.title = 'Handloom Cotton Care Guide'
  AND e.entity_type = 'fabric'
  AND e.entity_key = 'handloom-cotton';

INSERT INTO knowledge_document_entities
    (document_id, entity_id, relationship_type, priority)
SELECT d.document_id, e.entity_id, 'applies_to', 100
FROM knowledge_documents d
CROSS JOIN knowledge_entities e
WHERE d.title = 'Return and Cancellation Policy'
  AND e.entity_type = 'business'
  AND e.entity_key = 'urban-aanchol';

INSERT INTO knowledge_document_entities
    (document_id, entity_id, relationship_type, priority)
SELECT d.document_id, e.entity_id, 'applies_to', 30
FROM knowledge_documents d
CROSS JOIN knowledge_entities e
WHERE d.title = 'Bengali Wedding Saree Guide'
  AND e.entity_type = 'occasion'
  AND e.entity_key = 'wedding';

-- =========================================================
-- 5. Connect chunks to entities they mention
-- =========================================================

INSERT INTO knowledge_chunk_entities
    (chunk_id, entity_id, mention_type)
SELECT c.chunk_id, e.entity_id, 'primary_subject'
FROM knowledge_chunks c
CROSS JOIN knowledge_entities e
WHERE c.section_title = 'Washing Instructions'
  AND e.entity_type = 'product'
  AND e.entity_key = 'UA-0001';

INSERT INTO knowledge_chunk_entities
    (chunk_id, entity_id, mention_type)
SELECT c.chunk_id, e.entity_id, 'fabric'
FROM knowledge_chunks c
CROSS JOIN knowledge_entities e
WHERE c.section_title = 'General Care'
  AND e.entity_type = 'fabric'
  AND e.entity_key = 'handloom-cotton';

INSERT INTO knowledge_chunk_entities
    (chunk_id, entity_id, mention_type)
SELECT c.chunk_id, e.entity_id, 'topic'
FROM knowledge_chunks c
CROSS JOIN knowledge_entities e
WHERE c.section_title = 'Washing Instructions'
  AND e.entity_type = 'topic'
  AND e.entity_key = 'washing';

INSERT INTO knowledge_chunk_entities
    (chunk_id, entity_id, mention_type)
SELECT c.chunk_id, e.entity_id, 'topic'
FROM knowledge_chunks c
CROSS JOIN knowledge_entities e
WHERE c.section_title = 'Policy'
  AND e.entity_type = 'business'
  AND e.entity_key = 'urban-aanchol';

-- =========================================================
-- 6. Create graph relationships
-- =========================================================

INSERT INTO knowledge_entity_relations
    (source_entity_id, target_entity_id, relation_type)
SELECT p.entity_id, f.entity_id, 'made_of'
FROM knowledge_entities p
CROSS JOIN knowledge_entities f
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001'
  AND f.entity_type = 'fabric'
  AND f.entity_key = 'handloom-cotton';

INSERT INTO knowledge_entity_relations
    (source_entity_id, target_entity_id, relation_type)
SELECT p.entity_id, o.entity_id, 'suitable_for'
FROM knowledge_entities p
CROSS JOIN knowledge_entities o
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001'
  AND o.entity_type = 'occasion'
  AND o.entity_key = 'wedding';

INSERT INTO knowledge_entity_relations
    (source_entity_id, target_entity_id, relation_type)
SELECT p.entity_id, s.entity_id, 'has_style'
FROM knowledge_entities p
CROSS JOIN knowledge_entities s
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001'
  AND s.entity_type = 'style'
  AND s.entity_key = 'traditional';

INSERT INTO knowledge_entity_relations
    (source_entity_id, target_entity_id, relation_type)
SELECT f.entity_id, t.entity_id, 'care_topic'
FROM knowledge_entities f
CROSS JOIN knowledge_entities t
WHERE f.entity_type = 'fabric'
  AND f.entity_key = 'handloom-cotton'
  AND t.entity_type = 'topic'
  AND t.entity_key = 'washing';

-- =========================================================
-- 7. Verification
-- =========================================================

SELECT 'Entities' AS object, COUNT(*) AS count
FROM knowledge_entities

UNION ALL

SELECT 'Documents', COUNT(*)
FROM knowledge_documents

UNION ALL

SELECT 'Chunks', COUNT(*)
FROM knowledge_chunks

UNION ALL

SELECT 'Document-Entity Links', COUNT(*)
FROM knowledge_document_entities

UNION ALL

SELECT 'Chunk-Entity Links', COUNT(*)
FROM knowledge_chunk_entities

UNION ALL

SELECT 'Graph Relations', COUNT(*)
FROM knowledge_entity_relations;

-- Show the graph
SELECT
    source.entity_type || ':' || source.entity_key AS source,
    r.relation_type,
    target.entity_type || ':' || target.entity_key AS target
FROM knowledge_entity_relations r
JOIN knowledge_entities source
    ON source.entity_id = r.source_entity_id
JOIN knowledge_entities target
    ON target.entity_id = r.target_entity_id
ORDER BY source, r.relation_type;

ROLLBACK;