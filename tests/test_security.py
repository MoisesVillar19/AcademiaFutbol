from utils.security import hash_password, verify_password, generate_temp_password


def test_hash_password():
    hashed = hash_password("test123")
    assert hashed != "test123"
    assert len(hashed) > 0
    assert hashed.startswith("$2")


def test_verify_password_correct():
    hashed = hash_password("test123")
    assert verify_password("test123", hashed) is True


def test_verify_password_incorrect():
    hashed = hash_password("test123")
    assert verify_password("wrongpass", hashed) is False


def test_verify_password_invalid_hash():
    assert verify_password("test", "invalid") is False
    assert verify_password("test", "") is False


def test_generate_temp_password():
    temp = generate_temp_password()
    assert len(temp) == 12
    assert temp != ""


def test_generate_temp_password_custom_length():
    temp = generate_temp_password(8)
    assert len(temp) == 8


def test_hash_unique():
    hash1 = hash_password("same_password")
    hash2 = hash_password("same_password")
    assert hash1 != hash2
