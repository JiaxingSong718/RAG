import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from text_retrieval import Text2EmbedStore
from llm import Baidullm
load_dotenv()

qa_prompt = PromptTemplate.from_template("""
仅根据给出的上下文信息回答问题，如果从上下文信息找不到答案就说不知道。

上下文信息:
{context}

问题：{question}
""")


class RAG(object):
    def __init__(self) -> None:
        self.model_name = os.environ.get("MODEL_NAME")

        self.model_init()
    def model_init(self):
        embedding_model_name = os.environ.get("EMBEDDING_MODEL_NAME")
        self.DataBase = Text2EmbedStore(embedding_model_name)

        if self.model_name == 'baidu-yi_34b_chat':
            model_name = self.model_name.replace('baidu-','')
            llm = Baidullm(model_name = model_name)
        else:
            raise ValueError("no llm to call")

        self.qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.DataBase.as_reteiever(),
            verbose=False,
            chain_type_kwargs={"prompt": qa_prompt}
        )
    def as_retrieval_qa(self):
        return self.qa