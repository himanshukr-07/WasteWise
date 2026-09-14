from backend.services.rag import index_knowledge_base


if __name__ == "__main__":
    print(index_knowledge_base(force=True))
