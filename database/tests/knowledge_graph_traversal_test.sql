BEGIN;

-- =========================================================
-- 1. Representative entities
-- =========================================================

INSERT INTO knowledge_entities
    (entity_type, entity_key, entity_name)
VALUES
    ('product', 'UA-0001', 'White & Grey Handloom Saree'),
    ('fabric', 'handloom-cotton', 'Handloom Cotton'),
    ('topic', 'washing', 'Saree Washing'),
    ('topic', 'colour-fading', 'Colour Fading');

-- =========================================================
-- 2. Relationships
-- =========================================================

INSERT INTO knowledge_entity_relations
    (source_entity_id, target_entity_id, relation_type)
SELECT p.entity_id, f.entity_id, 'made_of'
FROM knowledge_entities p
JOIN knowledge_entities f
    ON f.entity_type = 'fabric'
   AND f.entity_key = 'handloom-cotton'
WHERE p.entity_type = 'product'
  AND p.entity_key = 'UA-0001';

INSERT INTO knowledge_entity_relations
    (source_entity_id, target_entity_id, relation_type)
SELECT f.entity_id, t.entity_id, 'care_topic'
FROM knowledge_entities f
JOIN knowledge_entities t
    ON t.entity_type = 'topic'
   AND t.entity_key = 'washing'
WHERE f.entity_type = 'fabric'
  AND f.entity_key = 'handloom-cotton';

INSERT INTO knowledge_entity_relations
    (source_entity_id, target_entity_id, relation_type)
SELECT t1.entity_id, t2.entity_id, 'related_to'
FROM knowledge_entities t1
JOIN knowledge_entities t2
    ON t2.entity_type = 'topic'
   AND t2.entity_key = 'colour-fading'
WHERE t1.entity_type = 'topic'
  AND t1.entity_key = 'washing';

-- =========================================================
-- 3. Recursive graph traversal
--
-- Start at UA-0001 and follow relationships.
-- =========================================================

WITH RECURSIVE graph_path AS (
    SELECT
        e.entity_id,
        e.entity_type,
        e.entity_key,
        e.entity_name,
        0 AS depth,
        e.entity_name::TEXT AS path
    FROM knowledge_entities e
    WHERE e.entity_type = 'product'
      AND e.entity_key = 'UA-0001'

    UNION ALL

    SELECT
        target.entity_id,
        target.entity_type,
        target.entity_key,
        target.entity_name,
        gp.depth + 1,
        gp.path || ' -> ' || target.entity_name
    FROM graph_path gp
    JOIN knowledge_entity_relations r
        ON r.source_entity_id = gp.entity_id
    JOIN knowledge_entities target
        ON target.entity_id = r.target_entity_id
    WHERE gp.depth < 5
)
SELECT
    depth,
    entity_type,
    entity_key,
    entity_name,
    path
FROM graph_path
ORDER BY depth;

ROLLBACK;