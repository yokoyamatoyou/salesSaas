from providers.search_provider import WebSearchProvider


def test_search_none_provider(monkeypatch):
    monkeypatch.setenv("SEARCH_PROVIDER", "none")
    provider = WebSearchProvider()
    assert provider.search("anything") == []


def test_search_stub_provider(monkeypatch):
    monkeypatch.setenv("SEARCH_PROVIDER", "stub")
    provider = WebSearchProvider()
    results = provider.search("IT", num=2)
    assert len(results) == 2
    assert all("title" in r and "url" in r for r in results)
