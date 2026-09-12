BEGIN;

-- Create the Order & Policies knowledge document
INSERT INTO knowledge_documents (
    title,
    document_type,
    source,
    language,
    status,
    priority
)
VALUES (
    'Urban Aanchol Order & Policies',
    'policy',
    'Urban Aanchol',
    'en',
    'Active',
    100
)
RETURNING document_id;

-- Store the document id for the chunks
\gset

-- Order process
INSERT INTO knowledge_chunks (
    document_id,
    chunk_text,
    chunk_index,
    section_title,
    content_type,
    language
)
VALUES (
    :'document_id',
    'Customers can place orders through WhatsApp. Product availability is confirmed before the order is finalized. Orders require prepayment through online payment methods.',
    0,
    'How to Order',
    'text',
    'en'
);

-- Delivery
INSERT INTO knowledge_chunks (
    document_id,
    chunk_text,
    chunk_index,
    section_title,
    content_type,
    language
)
VALUES (
    :'document_id',
    'Delivery normally takes 5 to 7 working days after order confirmation.',
    1,
    'Delivery',
    'text',
    'en'
);

-- Payment
INSERT INTO knowledge_chunks (
    document_id,
    chunk_text,
    chunk_index,
    section_title,
    content_type,
    language
)
VALUES (
    :'document_id',
    'Online payment is required. Cash on Delivery is not available.',
    2,
    'Payment',
    'text',
    'en'
);

-- Shipping
INSERT INTO knowledge_chunks (
    document_id,
    chunk_text,
    chunk_index,
    section_title,
    content_type,
    language
)
VALUES (
    :'document_id',
    'Shipping is free within West Bengal. Shipping charges apply for deliveries outside West Bengal.',
    3,
    'Shipping Charges',
    'text',
    'en'
);

-- Returns
INSERT INTO knowledge_chunks (
    document_id,
    chunk_text,
    chunk_index,
    section_title,
    content_type,
    language
)
VALUES (
    :'document_id',
    'Returns are accepted only for products that are physically damaged on delivery. Customers must provide a clear unboxing video showing the damage.',
    4,
    'Returns',
    'text',
    'en'
);

-- Verify the document and chunks
SELECT
    d.title,
    d.document_type,
    d.status,
    COUNT(c.chunk_id) AS chunk_count
FROM knowledge_documents d
LEFT JOIN knowledge_chunks c
    ON c.document_id = d.document_id
WHERE d.document_id = :'document_id'
GROUP BY d.document_id, d.title, d.document_type, d.status;

ROLLBACK;