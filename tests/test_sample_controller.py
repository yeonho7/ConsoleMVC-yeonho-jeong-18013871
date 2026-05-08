import pytest
from src.store import InMemoryStore
from src.controllers.sample_controller import SampleController
from src.models.sample import Sample


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def ctrl(store):
    return SampleController(store)


class TestSampleControllerRegister:
    def test_register_saves_sample_to_store(self, ctrl, store):
        ctrl.register("S-001", "GaAs Wafer", 30.0, 0.9)
        assert "S-001" in store.samples

    def test_register_returns_sample(self, ctrl):
        sample = ctrl.register("S-001", "GaAs Wafer", 30.0, 0.9)
        assert isinstance(sample, Sample)
        assert sample.sample_id == "S-001"
        assert sample.name == "GaAs Wafer"
        assert sample.avg_production_time == 30.0
        assert sample.yield_rate == 0.9
        assert sample.stock == 0


class TestSampleControllerListAll:
    def test_list_all_returns_empty_when_no_samples(self, ctrl):
        assert ctrl.list_all() == []

    def test_list_all_returns_all_registered_samples(self, ctrl):
        ctrl.register("S-001", "GaAs Wafer", 30.0, 0.9)
        ctrl.register("S-002", "InP Wafer", 45.0, 0.85)
        result = ctrl.list_all()
        assert len(result) == 2


class TestSampleControllerSearch:
    def test_search_returns_matching_samples_by_name(self, ctrl):
        ctrl.register("S-001", "GaAs Wafer", 30.0, 0.9)
        ctrl.register("S-002", "InP Wafer", 45.0, 0.85)
        ctrl.register("S-003", "Silicon Die", 20.0, 0.95)
        result = ctrl.search("Wafer")
        assert len(result) == 2

    def test_search_returns_empty_when_no_match(self, ctrl):
        ctrl.register("S-001", "GaAs Wafer", 30.0, 0.9)
        result = ctrl.search("Germanium")
        assert result == []

    def test_search_is_case_insensitive(self, ctrl):
        ctrl.register("S-001", "GaAs Wafer", 30.0, 0.9)
        result = ctrl.search("gaas")
        assert len(result) == 1
