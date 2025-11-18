"""
Vector store for semantic memory search using ChromaDB
"""
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()


class VectorMemoryStore:
    """
    Vector store for storing and retrieving memories semantically
    """

    def __init__(self, persist_directory: str = None):
        """
        Initialize vector store

        Args:
            persist_directory: Directory to persist the vector database
        """
        if persist_directory is None:
            persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        self.embeddings = OpenAIEmbeddings()

    def get_or_create_collection(self, character_id: int):
        """Get or create a collection for a specific character"""
        collection_name = f"character_{character_id}_memories"
        return self.client.get_or_create_collection(name=collection_name)

    def add_memory(
        self,
        character_id: int,
        memory_id: int,
        content: str,
        metadata: Dict[str, Any]
    ):
        """
        Add a memory to the vector store

        Args:
            character_id: Character ID
            memory_id: Memory ID from database
            content: Memory content text
            metadata: Additional metadata (category, timestamp, etc.)
        """
        collection = self.get_or_create_collection(character_id)

        # Generate embedding
        embedding = self.embeddings.embed_query(content)

        # Add to collection
        collection.add(
            ids=[str(memory_id)],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )

    def search_memories(
        self,
        character_id: int,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories using semantic similarity

        Args:
            character_id: Character ID
            query: Search query
            n_results: Number of results to return

        Returns:
            List of relevant memories with scores
        """
        collection = self.get_or_create_collection(character_id)

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # Format results
        memories = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                memories.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })

        return memories

    def delete_character_memories(self, character_id: int):
        """Delete all memories for a character"""
        collection_name = f"character_{character_id}_memories"
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            pass  # Collection doesn't exist
