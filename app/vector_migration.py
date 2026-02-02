"""Migration utility to move persisted docs into a hosted Pinecone index.

This script expects these env vars to be set when using Pinecone:
- PINECONE_API_KEY
- PINECONE_ENV (region)
- PINECONE_INDEX (index name)

Embeddings are generated using OpenAI embeddings if OPENAI_API_KEY is available.
Alternatively, install sentence-transformers and the migration will use it.

Usage (python):
    from app.vector_migration import migrate_all_to_pinecone
    migrate_all_to_pinecone(db_path='data/db.sqlite')

This is a best-effort small utility for classroom/demo use.
"""
from typing import List
import os

try:
    import pinecone
except Exception:
    pinecone = None

try:
    import openai
except Exception:
    openai = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

from app import db as appdb


def _get_embeddings_texts(texts: List[str]):
    """Return embeddings for a list of texts. Prefer sentence-transformers locally, otherwise OpenAI embeddings."""
    if SentenceTransformer is not None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embs = model.encode(texts, convert_to_numpy=False).tolist()
        return embs
    if openai is not None and os.getenv('OPENAI_API_KEY'):
        model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        resp = openai.Embedding.create(model=model, input=texts)
        return [r['embedding'] for r in resp['data']]
    raise RuntimeError('No embedding provider available (install sentence-transformers or set OPENAI_API_KEY)')


def migrate_all_to_pinecone(db_path: str = 'data/db.sqlite'):
    if pinecone is None:
        raise RuntimeError('pinecone-client not installed')

    api_key = os.getenv('PINECONE_API_KEY')
    env = os.getenv('PINECONE_ENV')
    index_name = os.getenv('PINECONE_INDEX', 'budgetbuddy')
    if not api_key or not env:
        raise RuntimeError('PINECONE_API_KEY and PINECONE_ENV must be set')

    pinecone.init(api_key=api_key, environment=env)

    # create index if not exists
    if index_name not in pinecone.list_indexes():
        # dimension must match embeddings used
        # we'll try to infer embedding dim by generating one sample embedding
        sample_text = ['sample']
        emb = _get_embeddings_texts(sample_text)[0]
        dim = len(emb)
        pinecone.create_index(index_name, dimension=dim)

    idx = pinecone.Index(index_name)

    # fetch all users
    users = appdb.list_users(db_path)
    for user in users:
        docs = appdb.get_docs_by_user(db_path, user)
        texts = [d['text'] for d in docs]
        ids = [f"{user}_{d['id']}" for d in docs]
        metadatas = [d['metadata'] if 'metadata' in d and d['metadata'] else { 'user_id': d['user_id'], 'id': d['id']} for d in docs]
        print(f'Migrating {len(texts)} docs for user {user} -> index {index_name}')
        # compute embeddings in batches
        batch_size = 16
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            embs = _get_embeddings_texts(batch_texts)
            to_upsert = [(batch_ids[j], embs[j], batch_meta[j]) for j in range(len(batch_ids))]
            idx.upsert(vectors=to_upsert)

    print('Migration complete')