from pathlib import Path
from typing import Dict, Any, List
import logging
from dataclasses import dataclass

from src.core.models import Project
from src.services.pdf_annotation_service import PDFAnnotationService
from src.rag.llm_chain import LLMChain, RAGResponse
from src.rag.config import RAGConfig
from src.rag.retrieval import RetrievalEngine
from src.rag.llm_provider import OllamaProvider
from src.rag.prompt_builder import PromptBuilder
from src.rag.vector_store import VectorStore
from src.rag.embeddings import EmbeddingGenerator
from src.services.project_service import project_service

logger = logging.getLogger(__name__)

@dataclass
class Criterion:
    id: str
    name: str
    description: str

class ValidationService:
    def __init__(self):
        self.annotation_service = PDFAnnotationService()
        self._init_llm_chain()
        
    def _init_llm_chain(self):
        try:
            config = RAGConfig.from_yaml()
            embedder = EmbeddingGenerator(model_name=config.embedding_model)
            vector_store = VectorStore(
                collection_name=config.collection_name,
                persist_directory=config.vector_store_path,
                embedding_function=embedder
            )
            retrieval_engine = RetrievalEngine(vector_store=vector_store, config=config)
            llm_provider = OllamaProvider(
                model_name=config.llm_model,
                base_url=config.llm_base_url
            )
            prompt_builder = PromptBuilder(retrieval_engine=retrieval_engine)
            
            self.llm_chain = LLMChain(
                retrieval_engine=retrieval_engine,
                llm_provider=llm_provider,
                prompt_builder=prompt_builder,
                config=config
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM Chain: {e}")
            self.llm_chain = None

    def _load_criteria(self) -> List[Criterion]:
        """Load criteria catalog (Mock for now)."""
        return [
            Criterion(id="K001", name="Innovationsgehalt", description="Ist das Projekt innovativ und geht über den Stand der Technik hinaus?"),
            Criterion(id="K002", name="Marktpotenzial", description="Gibt es einen klaren Markt und Verwertungspotenzial?"),
            Criterion(id="K003", name="Arbeitsplan", description="Ist der Arbeitsplan realistisch und nachvollziehbar?"),
            Criterion(id="K004", name="Finanzierung", description="Ist die Finanzierung gesichert und angemessen?")
        ]

    async def validate_project(self, project: Project) -> Dict[str, Any]:
        """
        Run validation on a project's documents using LLM/RAG.
        """
        if not self.llm_chain:
            logger.error("LLM Chain not initialized. Cannot validate.")
            return {"status": "error", "message": "LLM Service unavailable"}

        logger.info(f"Starting validation for project {project.id}")
        
        criteria = self._load_criteria()
        results = []
        all_citations = []
        
        for criterion in criteria:
            question = f"Erfüllt das Projekt das Kriterium: {criterion.description}?"
            
            try:
                rag_response: RAGResponse = self.llm_chain.query_with_citations(
                    question=question,
                    project_id=project.id
                )
                
                # Simple status parsing
                answer_lower = rag_response.answer.lower()
                if "ja" in answer_lower[:20] or "erfüllt" in answer_lower:
                    status = "pass"
                elif "nein" in answer_lower[:20] or "nicht" in answer_lower:
                    status = "fail"
                else:
                    status = "unclear"
                
                result = {
                    "id": criterion.id,
                    "name": criterion.name,
                    "question": question,
                    "answer": rag_response.answer,
                    "status": status,
                    "citations": [
                        {
                            "doc_id": c.doc_id,
                            "doc_name": c.doc_name,
                            "page": c.page,
                            "text_snippet": c.text_snippet,
                            "score": c.score
                        }
                        for c in rag_response.citations
                    ]
                }
                results.append(result)
                all_citations.extend(rag_response.citations)
                
            except Exception as e:
                logger.error(f"Error validating criterion {criterion.id}: {e}")
                results.append({
                    "id": criterion.id,
                    "name": criterion.name,
                    "status": "error",
                    "answer": f"Fehler bei der Analyse: {str(e)}",
                    "citations": []
                })

        # Annotate documents
        annotated_docs = await self._annotate_documents(project, all_citations)
        
        # Save results to project (in memory or persist if needed)
        # For now, we just return them, but ideally we should save them to the project object
        # project.validation_results = results
        # project_service.update_project(project) # Assuming update exists
        
        return {
            "project_id": project.id,
            "status": "completed",
            "criteria": results,
            "annotated_documents": annotated_docs,
            "total_citations": len(all_citations)
        }

    async def _annotate_documents(self, project: Project, citations: List) -> Dict[str, str]:
        """
        Create annotated copies of documents based on citations.
        """
        annotated_docs = {}
        
        # Group citations by document
        citations_by_doc = {}
        for cit in citations:
            # cit is either Citation object or dict if we serialized it? 
            # It is Citation object from RAGResponse
            doc_id = cit.doc_id
            if doc_id not in citations_by_doc:
                citations_by_doc[doc_id] = []
            
            citations_by_doc[doc_id].append({
                "page": cit.page,
                "quote": cit.text_snippet,
                "comment": "RAG Citation"
            })
            
        for doc in project.documents:
            input_path = Path(doc.path)
            # Use document ID for matching if possible, otherwise filename
            doc_id = doc.id
            
            if doc_id in citations_by_doc:
                output_dir = input_path.parent
                output_filename = f"annotated_{input_path.name}"
                output_path = output_dir / output_filename
                
                success = self.annotation_service.create_annotated_pdf(
                    input_path=input_path,
                    output_path=output_path,
                    citations=citations_by_doc[doc_id]
                )
                
                if success:
                    annotated_docs[doc_id] = str(output_path)
                    # Also map by filename for easier lookup in frontend
                    annotated_docs[doc.filename] = str(output_path)
                    
        return annotated_docs
