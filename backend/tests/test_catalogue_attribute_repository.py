from unittest.mock import MagicMock, patch


from backend.app.database.catalogue_attribute_repository import (
    get_borders,
    get_brands,
    get_catalogue_vocabulary,
    get_categories,
    get_collections,
    get_colours,
    get_fabrics,
    get_moods,
    get_occasions,
    get_patterns,
    get_secondary_colours,
    get_styles,
    get_tags,
)

from backend.app.database.catalogue_attribute_repository import (
    get_moods,
    get_occasions,
    get_styles,
    get_tags,
)


def _mock_connection(rows):
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.fetchall.return_value = rows
    return connection


def test_get_occasions_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Wedding",),
            ("Festival",),
            ("Party",),
        ]
    )

    assert get_occasions(connection) == [
        "Wedding",
        "Festival",
        "Party",
    ]


def test_get_styles_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Traditional",),
            ("Contemporary",),
        ]
    )

    assert get_styles(connection) == [
        "Traditional",
        "Contemporary",
    ]


def test_get_moods_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Elegant",),
            ("Vibrant",),
        ]
    )

    assert get_moods(connection) == [
        "Elegant",
        "Vibrant",
    ]


def test_get_tags_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Handloom",),
            ("Festive",),
        ]
    )

    assert get_tags(connection) == [
        "Handloom",
        "Festive",
    ]

def test_get_categories_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Saree",),
            ("Blouse",),
        ]
    )

    assert get_categories(connection) == [
        "Saree",
        "Blouse",
    ]


def test_get_brands_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Brand A",),
            ("Brand B",),
        ]
    )

    assert get_brands(connection) == [
        "Brand A",
        "Brand B",
    ]


def test_get_collections_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Festive Collection",),
            ("Wedding Collection",),
        ]
    )

    assert get_collections(connection) == [
        "Festive Collection",
        "Wedding Collection",
    ]


def test_get_fabrics_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Cotton",),
            ("Silk",),
        ]
    )

    assert get_fabrics(connection) == [
        "Cotton",
        "Silk",
    ]


def test_get_colours_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Blue",),
            ("Red",),
        ]
    )

    assert get_colours(connection) == [
        "Blue",
        "Red",
    ]


def test_get_secondary_colours_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Gold",),
            ("Green",),
        ]
    )

    assert get_secondary_colours(connection) == [
        "Gold",
        "Green",
    ]


def test_get_patterns_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Floral",),
            ("Geometric",),
        ]
    )

    assert get_patterns(connection) == [
        "Floral",
        "Geometric",
    ]


def test_get_borders_returns_distinct_values():
    connection = _mock_connection(
        [
            ("Zari",),
            ("Temple",),
        ]
    )

    assert get_borders(connection) == [
        "Zari",
        "Temple",
    ]

def test_get_catalogue_vocabulary_returns_all_attribute_types():
    connection = MagicMock()

    expected = {
        "category": ["Saree", "Blouse"],
        "brand": ["Brand A"],
        "collection": ["Festive Collection"],
        "fabric": ["Cotton", "Silk"],
        "colour": ["Blue", "Red"],
        "secondary_colour": ["Gold"],
        "pattern": ["Floral"],
        "border": ["Zari"],
        "occasion": ["Wedding"],
        "style": ["Traditional"],
        "mood": ["Elegant"],
        "tag": ["Handloom"],
    }

    with (
        patch(
            "backend.app.database.catalogue_attribute_repository.get_categories",
            return_value=expected["category"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_brands",
            return_value=expected["brand"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_collections",
            return_value=expected["collection"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_fabrics",
            return_value=expected["fabric"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_colours",
            return_value=expected["colour"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_secondary_colours",
            return_value=expected["secondary_colour"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_patterns",
            return_value=expected["pattern"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_borders",
            return_value=expected["border"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_occasions",
            return_value=expected["occasion"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_styles",
            return_value=expected["style"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_moods",
            return_value=expected["mood"],
        ),
        patch(
            "backend.app.database.catalogue_attribute_repository.get_tags",
            return_value=expected["tag"],
        ),
    ):
        assert get_catalogue_vocabulary(connection) == expected