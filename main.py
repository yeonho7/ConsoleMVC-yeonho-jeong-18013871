from src.store import InMemoryStore
from src.app import App

if __name__ == "__main__":
    store = InMemoryStore()
    app = App(store)
    app.run()
