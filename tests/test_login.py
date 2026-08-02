from services import auth_service


def test_login_exitoso():
    usuario = auth_service.login("admin", "admin123")
    assert usuario is not None
    assert usuario["username"] == "admin"
    assert usuario["rol"] == "ADMIN"
    auth_service.logout()


def test_login_fallido_password():
    usuario = auth_service.login("admin", "wrongpass")
    assert usuario is None


def test_login_fallido_usuario():
    usuario = auth_service.login("noexiste", "admin123")
    assert usuario is None


def test_logout():
    auth_service.login("admin", "admin123")
    assert auth_service.esta_logueado() is True
    auth_service.logout()
    assert auth_service.esta_logueado() is False


def test_obtener_usuario_actual():
    auth_service.login("admin", "admin123")
    usuario = auth_service.obtener_usuario_actual()
    assert usuario is not None
    assert usuario["username"] == "admin"
    assert usuario["nombres"] == "Admin"
    auth_service.logout()


def test_es_admin():
    auth_service.login("admin", "admin123")
    assert auth_service.es_admin() is True
    auth_service.logout()
