"""
RAG Service using ChromaDB
Stores and retrieves company policy context for LLM enrichment.
"""

import os
from typing import List, Dict, Any, Optional
import hashlib

# Disable ChromaDB telemetry and set environment before import
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_SERVER_NOFILE", "1")

# Try to import ChromaDB - make it optional
CHROMADB_AVAILABLE = False
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except Exception as e:
    print(f"⚠️ ChromaDB not available: {e}")
    print("RAG functionality will be disabled. Company context retrieval will not work.")
    chromadb = None
    Settings = None

# Try to import sentence transformers
EMBEDDINGS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ SentenceTransformers not available: {e}")
    SentenceTransformer = None


class RAGService:
    """
    Retrieval-Augmented Generation service for company knowledge.
    Uses ChromaDB for vector storage and semantic search.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB and embedding model.
        
        Args:
            persist_directory: Path to store ChromaDB data
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_model = None
        
    def initialize(self):
        """Load embedding model and connect to ChromaDB."""
        # Check if dependencies are available
        if not CHROMADB_AVAILABLE or not EMBEDDINGS_AVAILABLE:
            print("⚠️ RAG Service: ChromaDB or SentenceTransformers not available")
            print("RAG functionality disabled - company context will not be available")
            self.client = None
            self.collection = None
            self.embedding_model = None
            return False
       
        try:
            print("Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            print("Initializing ChromaDB...")
            # Use PersistentClient without default embedding function
            # We handle embeddings ourselves with sentence-transformers
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection WITHOUT embedding function
            # We'll provide embeddings manually
            self.collection = self.client.get_or_create_collection(
                name="company_policies",
                metadata={"description": "Company policies and context for call intelligence"}
            )
            
            print(f"✅ RAG Service initialized (ChromaDB collection: {self.collection.count()} documents)")
            return True
        except Exception as e:
            print(f"❌ RAG Service initialization failed: {e}")
            print("Continuing without RAG functionality...")
            self.client = None
            self.collection = None
            self.embedding_model = None
            return False
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval.
        
        Args:
            text: Full text to chunk
            chunk_size: Target size of each chunk (characters)
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _generate_id(self, text: str, index: int) -> str:
        """Generate unique ID for document chunk."""
        hash_input = f"{text}_{index}".encode('utf-8')
        return hashlib.md5(hash_input).hexdigest()
    
    def store_company_context(
        self,
        policy_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store company policy text in ChromaDB.
        
        Args:
            policy_text: Company policy or context text
            metadata: Optional metadata (e.g., category, department)
        
        Returns:
            Storage result with chunk count
        """
        if not self.collection or not self.embedding_model:
            return {
                "success": False,
                "error": "RAG service not available (ChromaDB or embeddings not loaded)"
            }
        
        try:
            # Split into chunks
            chunks = self._chunk_text(policy_text)
            
            if not chunks:
                return {"success": False, "error": "No chunks generated from text"}
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            # Prepare documents
            ids = [self._generate_id(policy_text, i) for i in range(len(chunks))]
            metadatas = [
                {
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # Store in ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            
            return {
                "success": True,
                "chunks_stored": len(chunks),
                "total_documents": self.collection.count()
            }
        except Exception as e:
            print(f"Error storing company context: {e}")
            return {"success": False, "error": str(e)}
    
    def retrieve_relevant_context(
        self,
        query: str,
        top_k: int = 3
    ) -> List[str]:
        """
        Retrieve top-k most relevant policy chunks for a query.
        
        Args:
            query: Search query (e.g., call transcript excerpt)
            top_k: Number of chunks to retrieve
        
        Returns:
            List of relevant policy text chunks
        """
        if not self.collection or not self.embedding_model:
            return []
        
        try:
            # Check if collection has documents
            if self.collection.count() == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=min(top_k, self.collection.count())
            )
            
            # Extract documents
            if results and results.get('documents'):
                return results['documents'][0]  # First query's results
            
            return []
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    def get_context_for_llm(
        self,
        transcript: str,
        nlp_insights: Dict[str, Any],
        top_k: int = 3
    ) -> str:
        """
        Build formatted context string for LLM prompt injection.
        
        Args:
            transcript: Call transcript
            nlp_insights: NLP analysis output
            top_k: Number of policy chunks to retrieve
        
        Returns:
            Formatted context string for LLM
        """
        # Build search query from transcript + key insights
        intent = nlp_insights.get('intent', '')
        
        # Extract keywords from all categories
        all_keywords = []
        for category_keywords in nlp_insights.get('keywords', {}).values():
            all_keywords.extend(category_keywords)
        keywords = ', '.join(all_keywords[:5])
        
        search_query = f"{transcript[:500]} Intent: {intent} Keywords: {keywords}"
        
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_context(search_query, top_k)
        
        if not relevant_chunks:
            return "No company policy context available."
        
        # Format for LLM
        context_lines = [
            "=== COMPANY POLICY CONTEXT ===",
            "Use this company knowledge when making decisions:\n"
        ]
        
        for i, chunk in enumerate(relevant_chunks, 1):
            context_lines.append(f"Policy #{i}:")
            context_lines.append(chunk)
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def clear_all_context(self) -> bool:
        """
        Clear all stored company context (use with caution).
        
        Returns:
            Success boolean
        """
        if not self.client:
            return False
        
        try:
            # Delete and recreate collection
            self.client.delete_collection("company_policies")
            self.collection = self.client.get_or_create_collection(
                name="company_policies",
                metadata={"description": "Company policies and context for call intelligence"}
            )
            print("✅ All company context cleared")
            return True
        except Exception as e:
            print(f"Error clearing context: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG service statistics."""
        if not self.collection:
            return {
                "total_documents": 0,
                "embedding_model": "N/A",
                "collection_name": "N/A",
                "status": "disabled"
            }
        
        return {
            "total_documents": self.collection.count(),
            "embedding_model": "all-MiniLM-L6-v2",
            "collection_name": "company_policies",
            "status": "active"
        }
