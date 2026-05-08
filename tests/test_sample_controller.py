from src.store import InMemoryStore
from src.controllers.sample_controller import SampleController
from src.models.sample import Sample


class TestSampleController:
    def setup_method(self):
        self.store = InMemoryStore()
        self.ctrl = SampleController(self.store)

    def test_register_returns_sample_instance(self):
        sample = self.ctrl.register("S001", "Alpha", 30.0, 0.85)
        assert isinstance(sample, Sample)

    def test_register_stores_sample_in_store(self):
        self.ctrl.register("S001", "Alpha", 30.0, 0.85)
        assert "S001" in self.store.samples

    def test_register_sample_fields_correct(self):
        sample = self.ctrl.register("S001", "Alpha", 30.0, 0.85)
        assert sample.sample_id == "S001"
        assert sample.name == "Alpha"
        assert sample.avg_production_time == 30.0
        assert sample.yield_rate == 0.85

    def test_list_all_empty_initially(self):
        assert self.ctrl.list_all() == []

    def test_list_all_returns_all_samples(self):
        self.ctrl.register("S001", "Alpha", 30.0, 0.85)
        self.ctrl.register("S002", "Beta", 20.0, 0.90)
        result = self.ctrl.list_all()
        assert len(result) == 2

    def test_search_by_keyword_matches_name(self):
        self.ctrl.register("S001", "Alpha Chip", 30.0, 0.85)
        self.ctrl.register("S002", "Beta Chip", 20.0, 0.90)
        self.ctrl.register("S003", "Gamma", 25.0, 0.88)
        result = self.ctrl.search("Chip")
        assert len(result) == 2

    def test_search_returns_empty_on_no_match(self):
        self.ctrl.register("S001", "Alpha", 30.0, 0.85)
        assert self.ctrl.search("Zeta") == []

    def test_search_is_case_insensitive(self):
        self.ctrl.register("S001", "Alpha Chip", 30.0, 0.85)
        result = self.ctrl.search("alpha")
        assert len(result) == 1
