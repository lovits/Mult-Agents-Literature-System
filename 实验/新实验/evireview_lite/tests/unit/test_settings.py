from evireview.conf.settings import Settings


def test_settings_never_require_a_committed_api_key():
    settings = Settings(
        llm_base_url="http://localhost:8001/v1",
        llm_model="test-model",
    )

    assert settings.llm_api_key is None
    assert settings.random_seed == 42
