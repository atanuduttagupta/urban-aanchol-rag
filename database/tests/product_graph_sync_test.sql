BEGIN;

-- 1. Create the product entity
INSERT INTO knowledge_entities (
    entity_type,
    entity_key,
    entity_name,
    description
)
SELECT
    'product',
    product_id,
    product_name,
    description
FROM products
WHERE product_id = 'UA-0001';

-- 2. Create related entities
INSERT INTO knowledge_entities (
    entity_type,
    entity_key,
    entity_name
)
VALUES
    ('fabric', 'handloom-cotton', 'Handloom Cotton'),
    ('style', 'traditional', 'Traditional'),
    ('occasion', 'wedding', 'Wedding');

-- 3. Create product relationships
INSERT INTO knowledge_entity_relations (
    source_entity_id,
    target_entity_id,
    relation_type
)
SELECT
    p.entity_id,
    f.entity_id,
    'made_of'
FROM knowledge_entities p
JOIN knowledge_entities f
    ON f.entity_type = 'fabric'
   AND f.entity_key = 'handloom-cotton'
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001';

INSERT INTO knowledge_entity_relations (
    source_entity_id,
    target_entity_id,
    relation_type
)
SELECT
    p.entity_id,
    s.entity_id,
    'has_style'
FROM knowledge_entities p
JOIN knowledge_entities s
    ON s.entity_type = 'style'
   AND s.entity_key = 'traditional'
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001';

INSERT INTO knowledge_entity_relations (
    source_entity_id,
    target_entity_id,
    relation_type
)
SELECT
    p.entity_id,
    o.entity_id,
    'suitable_for'
FROM knowledge_entities p
JOIN knowledge_entities o
    ON o.entity_type = 'occasion'
   AND o.entity_key = 'wedding'
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001';

-- 4. Verify the graph
SELECT
    p.entity_key AS product,
    r.relation_type,
    t.entity_key AS related_entity,
    t.entity_name
FROM knowledge_entity_relations r
JOIN knowledge_entities p
    ON p.entity_id = r.source_entity_id
JOIN knowledge_entities t
    ON t.entity_id = r.target_entity_id
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001'
ORDER BY r.relation_type;

ROLLBACK;