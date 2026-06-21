class FakeCollection:
    def query(self, **_kwargs):
        return {
            "ids": [["strong", "weak"]],
            "documents": [["relevant text", "irrelevant text"]],
            "metadatas": [[{"filename": "manual.pdf"}, {"filename": "notes.pdf"}]],
            "distances": [[0.1, 0.95]],
        }


def test_vector_store_query_filters_below_min_score(test_data_dir) -> None:
    from app.services.vector_store import VectorStore

    store = VectorStore.__new__(VectorStore)
    store._collection = FakeCollection()

    matches = store.query([0.1, 0.2], top_k=2, min_score=0.2)

    assert len(matches) == 1
    assert matches[0]["chunk_id"] == "strong"
    assert matches[0]["score"] == 0.9
    assert matches[0]["metadata"]["filename"] == "manual.pdf"
