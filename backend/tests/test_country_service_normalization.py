from types import SimpleNamespace
import pytest

from app.services.country_service import CountryService


class FakeRepo:
    def __init__(self):
        self.last_called = None

    def _record(self, name, country_id, *args, **kwargs):
        self.last_called = (name, country_id, args, kwargs)
        return []

    def get_ministries(self, country_id, *args, **kwargs):
        return self._record("get_ministries", country_id, *args, **kwargs)

    def get_tenders(self, country_id, *args, **kwargs):
        return self._record("get_tenders", country_id, *args, **kwargs)

    def get_budgets(self, country_id, *args, **kwargs):
        return self._record("get_budgets", country_id, *args, **kwargs)

    def get_projects(self, country_id, *args, **kwargs):
        return self._record("get_projects", country_id, *args, **kwargs)

    def get_companies(self, country_id, *args, **kwargs):
        return self._record("get_companies", country_id, *args, **kwargs)


class FakeResolver:
    def __init__(self, entity_id, canonical_name=None):
        self._entity_id = entity_id
        self._canonical_name = canonical_name or entity_id

    def resolve_country(self, text):
        return SimpleNamespace(entity_id=self._entity_id, canonical_name=self._canonical_name)


@pytest.mark.parametrize(
    "method_name, repo_attr",
    [
        ("ministries", "get_ministries"),
        ("tenders", "get_tenders"),
        ("budgets", "get_budgets"),
        ("projects", "get_projects"),
        ("companies", "get_companies"),
    ],
)
def test_country_service_normalizes_legacy_and_canonical(method_name, repo_attr):
    service = CountryService(db=None)
    fake_repo = FakeRepo()
    service.repo = fake_repo

    # Case A: resolver returns legacy prefixed id
    service.resolver = FakeResolver("country_kenya", "Kenya")
    getattr(service, method_name)("Kenya")
    assert fake_repo.last_called is not None
    assert fake_repo.last_called[1] == "kenya", f"Expected normalized 'kenya' but got {fake_repo.last_called[1]} for legacy id"

    # Case B: resolver returns canonical id already
    service.resolver = FakeResolver("kenya", "Kenya")
    getattr(service, method_name)("Kenya")
    assert fake_repo.last_called is not None
    assert fake_repo.last_called[1] == "kenya", f"Expected 'kenya' for canonical id but got {fake_repo.last_called[1]}"
