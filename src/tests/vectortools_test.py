import unittest
from unittest.mock import patch, MagicMock
from src.vectortools import load_api_key, process_documents
from pathlib import Path


class TestYourModule(unittest.TestCase):
    @patch('os.getenv')
    def test_load_api_key(self, mock_getenv):
        mock_getenv.return_value = 'fake_key'
        result = load_api_key()
        self.assertEqual(result, 'fake_key')

    @patch('langchain.OpenAI')  # Add this line
    @patch('langchain.text_splitter.CharacterTextSplitter')
    @patch('langchain.document_loaders.TextLoader')
    @patch('langchain.embeddings.openai.OpenAIEmbeddings')
    @patch('langchain.vectorstores.Chroma')
    def test_process_documents(self, mock_chroma, mock_embeddings, mock_loader, mock_splitter, mock_openai):
        mock_loader_inst = MagicMock()
        mock_loader.return_value = mock_loader_inst
        mock_splitter_inst = MagicMock()
        mock_splitter.return_value = mock_splitter_inst
        mock_embeddings_inst = MagicMock()
        mock_embeddings.return_value = mock_embeddings_inst
        mock_db_inst = MagicMock()
        mock_chroma.from_documents.return_value = mock_db_inst
        
        db, retriever = process_documents(mock_loader, Path("dummy_path"), "dummy_name", "dummy_dir")
        
        mock_loader.assert_called_once_with(Path("dummy_path"))
        mock_splitter.assert_called_once()
        mock_embeddings.assert_called_once()
        mock_chroma.from_documents.assert_called_once_with(
            mock_splitter_inst.split_documents.return_value,
            mock_embeddings_inst,
            collection_name="dummy_name",
            persist_directory="dummy_dir"
        )
        self.assertEqual(db, mock_db_inst)
        self.assertEqual(retriever, mock_db_inst.as_retriever.return_value)


if __name__ == '__main__':
    unittest.main()