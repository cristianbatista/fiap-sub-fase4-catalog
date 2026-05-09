from infrastructure.database.mongodb import _extract_db_name


def test_extract_db_name_from_full_uri():
    assert _extract_db_name("mongodb://localhost:27017/catalog") == "catalog"


def test_extract_db_name_with_query_params():
    assert _extract_db_name("mongodb://localhost:27017/mydb?authSource=admin") == "mydb"


def test_extract_db_name_no_db_returns_default():
    assert _extract_db_name("mongodb://localhost:27017/") == "catalog"


def test_extract_db_name_empty_path_returns_default():
    assert _extract_db_name("mongodb://localhost:27017") == "catalog"
