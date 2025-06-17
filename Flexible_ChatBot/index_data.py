from scraper import scrape_site
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
# Liste des pages à indexer
urls = [
    "http://127.0.0.1:5000/",
    "http://127.0.0.1:5000/page2",   
    "http://127.0.0.1:5000/page3"
]

text = scrape_site(urls)

docs = [Document(page_content=text)]
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs_split = splitter.split_documents(docs)

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(docs_split, embedding)
db.save_local("vectordb")

print("Base vectorielle créée avec", len(docs_split), "documents.")
