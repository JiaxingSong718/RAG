import os
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, JSONLoader, CSVLoader
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()

embedding_model_map = {
    "text2vec-base":"./EmbeddingModel"
}
class Text2EmbedStore(object):
    def __init__(self,model_name) -> None:
        self.model_name = model_name
        file_path = os.environ.get("FILE_NAME")

        self.text_split = None
        self.text_split_init()
        self.embedding_model_init()
        if file_path:
            self.load_dir(file_path=file_path)

    def text_split_init(self):
        text_split_name = os.environ.get("TEXT_SPLIT_METHOD")
        chunk_size = int(os.environ.get("CHUNK_SIZE", 256))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", 128))
        if text_split_name == 'char':
            self.text_split = CharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
        else:
            self.text_split = CharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)

    def embedding_model_init(self):
        persist_directory = os.environ.get("PERSIST_DIRECTOR",'./DataBase')
        self.embedding_model = self.load_embedding_model(self.model_name)

        db_name = os.environ.get("VECTOR_DB_NAME",'chroma')
        if db_name == 'chroma':
            self.db = Chroma(persist_directory=persist_directory,embedding_function=self.embedding_model)
        else:
            self.db = Chroma(persist_directory=persist_directory,embedding_function=self.embedding_model)

    def load_embedding_model(self,model_name):
        if model_name not in embedding_model_map:
            raise ValueError("Embedding model not set right, you can select from {}".format(list(embedding_model_map.keys())))
        embedding_model = HuggingFaceBgeEmbeddings(model_name=embedding_model_map[model_name])
        return embedding_model

    def load_dir(self,file_path):
        if os.path.isdir(file_path):
            for root,ds,fs in os.walk(file_path):
                for f in fs:
                    self.load_file(file_name=f)
        else:
            self.load_file(file_path)

    def load_file(self,file_name):
        print("file_name:",file_name)
        if file_name.endswith('.pdf') or file_name.endswith('.PDF'):
            loader = PyPDFLoader(file_name, extract_images=True) # 使用OCR解析pdf中图片里面的文字
        elif file_name.endswith('.txt') or file_name.endswith('.TXT'):
            loader = TextLoader(file_name,encoding='utf-8')
        elif file_name.endswith('.json') or file_name.endswith('.JSON'):
            loader = JSONLoader(file_name, '.key[].text')
        elif file_name.endswith('.csv') or file_name.endswith('.CSV'):
            loader = CSVLoader(file_name)
        else:
            raise ValueError("no support this type file, {}, you can upload file type {}".format(file_name, ['.pdf','.txt','.json','.csv']))
        documents = loader.load()
        docs = self.text_split.split_documents(documents)
        if docs:
            self.db.add_documents(docs)

    def as_reteiever(self):
        return self.db.as_retriever()
    def as_db(self):
        return self.db