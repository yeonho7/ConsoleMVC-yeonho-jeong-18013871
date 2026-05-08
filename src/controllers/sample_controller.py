from src.models.sample import Sample


class SampleController:
    def __init__(self, store):
        self.store = store

    def register(self, sample_id: str, name: str, avg_time: float, yield_rate: float) -> Sample:
        sample = Sample(sample_id=sample_id, name=name, avg_production_time=avg_time, yield_rate=yield_rate)
        self.store.samples[sample_id] = sample
        return sample

    def list_all(self) -> list[Sample]:
        return list(self.store.samples.values())

    def search(self, keyword: str) -> list[Sample]:
        lower = keyword.lower()
        return [s for s in self.store.samples.values() if lower in s.name.lower()]
