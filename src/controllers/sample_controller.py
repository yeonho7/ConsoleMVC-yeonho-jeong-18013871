from src.models.sample import Sample
from src.store import InMemoryStore


class SampleController:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def register(self, sample_id: str, name: str, avg_time: float, yield_rate: float) -> Sample:
        sample = Sample(sample_id=sample_id, name=name, avg_production_time=avg_time, yield_rate=yield_rate)
        self._store.samples[sample_id] = sample
        return sample

    def list_all(self) -> list[Sample]:
        return list(self._store.samples.values())

    def search(self, keyword: str) -> list[Sample]:
        kw = keyword.lower()
        return [s for s in self._store.samples.values() if kw in s.name.lower()]
