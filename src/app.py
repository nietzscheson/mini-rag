from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter

chat = ChatOllama(model="mistral")

# 1. Split data
urls = [
    "https://ollama.com/",
    "https://ollama.com/blog",
    "https://ollama.com/blog/windows-preview",
    "https://ollama.com/blog/openai-compatibility",
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
doc_splits = text_splitter.split_documents(docs_list)

# 2. Convert docs to embeddings and store in Chroma
vectorstore = Chroma.from_documents(
    documents=doc_splits, 
    collection_name="mini-rag",
    embedding=OllamaEmbeddings(model="nomic-embed-text")
)

retriever = vectorstore.as_retriever()

# 3. Response before RAG
print("### Before RAG Response ###\n")

before_rag_response_template = "What is {topic}?"

before_rag_prompt = ChatPromptTemplate.from_template(before_rag_response_template)

before_rag_chain = before_rag_prompt | chat | StrOutputParser()

print(before_rag_chain.invoke({"topic": "Ollama"}))

# 4. Response after RAG
print("### After RAG Response ###\n")

after_rag_response_template = """Answer the question based only on the following context: 
{context}
Question: {question}
"""

after_rag_prompt = ChatPromptTemplate.from_template(after_rag_response_template)

after_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | after_rag_prompt
    | chat
    | StrOutputParser()
)

print(after_rag_chain.invoke({"question": "What is Ollama?"}))
