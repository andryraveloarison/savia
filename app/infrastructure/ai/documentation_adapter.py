import logging
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings

from app.core.config import get_settings

logger = logging.getLogger("savia")


class DocumentationAdapter:
    """
    Adaptateur pour la documentation produit avec index FAISS persistant.
    Charge les PDFs au démarrage et sauvegarde l'index pour ne pas le reconstruire.
    """

    def __init__(
        self,
        docs_path: str = "app/infrastructure/ai/docs",
        index_path: str = "app/infrastructure/ai/faiss_index"
    ):
        self.docs_path = Path(docs_path)
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.indexes = {}

        settings = get_settings()
        self.ai_cache_dir = Path(settings.ai_cache_dir)
        self.ai_cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📂 Utilisation du cache AI: {self.ai_cache_dir}")

        self.embeddings = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            cache_dir=str(self.ai_cache_dir)
        )

        self._load_or_build_indexes()

    def _load_or_build_indexes(self):
        logger.info("📄 Initialisation des indexes de documentation...")

        if not self.docs_path.exists():
            logger.warning(f"Dossier docs introuvable : {self.docs_path}")
            return

        for category_folder in self.docs_path.iterdir():
            if not category_folder.is_dir():
                continue

            category = category_folder.name
            faiss_file = self.index_path / f"{category}.faiss"

            # Charger depuis disque si déjà construit
            if faiss_file.exists():
                try:
                    faiss_index = FAISS.load_local(
                        str(faiss_file),
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    self.indexes[category] = faiss_index
                    logger.info(f"✅ Index FAISS chargé depuis disque pour {category}")
                    continue
                except Exception as e:
                    logger.warning(f"Reconstruction nécessaire pour {category}: {e}")

            # Construire l'index depuis les PDFs
            all_texts = []
            for pdf_file in category_folder.glob("*.pdf"):
                try:
                    loader = PyPDFLoader(str(pdf_file))
                    docs = loader.load()
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000,
                        chunk_overlap=100
                    )
                    chunks = splitter.split_documents(docs)
                    all_texts.extend(chunks)
                    logger.info(f"📄 {pdf_file.name} chargé ({len(chunks)} chunks)")
                except Exception as e:
                    logger.error(f"Erreur chargement {pdf_file}: {e}")

            if all_texts:
                faiss_index = FAISS.from_documents(all_texts, self.embeddings)
                self.indexes[category] = faiss_index
                faiss_index.save_local(str(faiss_file))
                logger.info(f"✅ Index FAISS construit pour {category} ({len(all_texts)} chunks)")
            else:
                logger.warning(f"Aucun PDF trouvé dans {category_folder}")

    def query(self, category: str, product_ref: str, user_message: str = "", top_k: int = 5) -> List[str]:
        if category not in self.indexes:
            logger.warning(f"Aucun index trouvé pour la catégorie {category}")
            return []

        faiss_index = self.indexes[category]
        query_text = f"Produit: {product_ref}. Problème: {user_message}"

        try:
            results = faiss_index.similarity_search(query_text, k=top_k)
            return [doc.page_content for doc in results]
        except Exception as e:
            logger.error(f"Erreur recherche FAISS: {e}")
            return []