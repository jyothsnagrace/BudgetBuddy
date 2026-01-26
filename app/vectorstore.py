import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """Vector store with optional sentence-transformers + faiss backend.

    Falls back to a TF-IDF + cosine similarity implementation if the heavy
    dependencies aren't installed (useful for Windows or CI).
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Try to use sentence-transformers + faiss if available
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            import numpy as np

            self._backend = "faiss"
            self.model = SentenceTransformer(model_name)
            self.dim = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(self.dim)
            self.metadatas: List[Dict] = []
        except Exception as e:
            logger.warning("Faiss backend unavailable, falling back to TF-IDF: %s", e)
            # Lightweight fallback
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            self._backend = "tfidf"
            self.vectorizer = TfidfVectorizer()
            self.docs: List[str] = []
            self.metadatas: List[Dict] = []
            self.cosine_similarity = cosine_similarity

    def add_documents(self, docs: List[str], metadatas: List[Dict]):
        # Ensure each metadata carries the original text for easier retrieval
        for i, m in enumerate(metadatas):
            if 'text' not in m:
                m['text'] = docs[i]

        if self._backend == "faiss":
            embeddings = self.model.encode(docs, convert_to_numpy=True)
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(1, -1)
            self.index.add(embeddings.astype('float32'))
            self.metadatas.extend(metadatas)
        else:
            # TF-IDF fallback: store docs and rebuild vectorizer
            self.docs.extend(docs)
            self.metadatas.extend(metadatas)
            # rebuild vectorizer on every add (ok for small demo)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.docs)

    def query(self, text: str, k: int = 5):
        if self._backend == "faiss":
            emb = self.model.encode([text], convert_to_numpy=True).astype('float32')
            D, I = self.index.search(emb, k)
            results = []
            for idx in I[0]:
                if idx < len(self.metadatas):
                    results.append(self.metadatas[idx])
            return results
        else:
            if not hasattr(self, 'tfidf_matrix') or self.tfidf_matrix.shape[0] == 0:
                return []
            qv = self.vectorizer.transform([text])
            sims = self.cosine_similarity(qv, self.tfidf_matrix)[0]
            top_idx = sims.argsort()[::-1][:k]
            results = [self.metadatas[i] for i in top_idx if i < len(self.metadatas)]
            return results

    def save(self, path: str):
        """Persist the vector store to disk.

        For the faiss backend this writes the index and metadatas. For the TF-IDF
        backend it writes the docs + metadatas.
        """
        import json
        import os
        os.makedirs(path, exist_ok=True)
        meta_path = os.path.join(path, "metadatas.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadatas, f, ensure_ascii=False, indent=2)

        if self._backend == "faiss":
            try:
                import faiss
                idx_path = os.path.join(path, "index.faiss")
                faiss.write_index(self.index, idx_path)
            except Exception:
                # best-effort: skip if write not available
                pass
        else:
            docs_path = os.path.join(path, "docs.json")
            with open(docs_path, "w", encoding="utf-8") as f:
                json.dump(self.docs, f, ensure_ascii=False, indent=2)

    def load(self, path: str):
        """Load a persisted vector store (best-effort)."""
        import json
        import os
        meta_path = os.path.join(path, "metadatas.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadatas = json.load(f)

        if self._backend == "faiss":
            try:
                import faiss
                idx_path = os.path.join(path, "index.faiss")
                if os.path.exists(idx_path):
                    self.index = faiss.read_index(idx_path)
            except Exception:
                pass
        else:
            docs_path = os.path.join(path, "docs.json")
            if os.path.exists(docs_path):
                with open(docs_path, "r", encoding="utf-8") as f:
                    self.docs = json.load(f)
                if len(self.docs) > 0:
                    self.tfidf_matrix = self.vectorizer.fit_transform(self.docs)
