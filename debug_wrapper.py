class DebugWrapper:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def as_retriever(self, *args, **kwargs):
        results = self.vectorstore.as_retriever(*args, **kwargs)
        print(type(results))
        return results
