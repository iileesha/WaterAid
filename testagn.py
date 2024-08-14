from langchain.vectorstores.pgvector import PGVector
import pandas as pd
import numpy as np
from langchain.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.pgvector import DistanceStrategy
from langchain.schema import Document


CONNECTION_STRING = "postgresql://postgres:123456@localhost:5433/wateraid"
df = pd.read_csv('Listings_Details.csv')
df.fillna("NA", inplace=True)
df.head()
combined = []

for index, row in df.iterrows():
    text_to_embed = row[1] + ". Location is " + row[3] + ". " + row[4] + " " + row[5]
    combined.append(text_to_embed)

df['combined'] = combined
# page_content_column is the column name in the dataframe to create embeddings for
loader = DataFrameLoader(df, page_content_column = 'combined')
docs = loader.load()


embeddings = HuggingFaceEmbeddings()


db = PGVector.from_documents(
    documents= docs,
    embedding = embeddings,
    collection_name= "test_listings",
    distance_strategy = DistanceStrategy.COSINE,
    connection_string=CONNECTION_STRING)

query = "I am based in Newcastle. I am a accountant. I like to watch variety shows in my free time."

#Fetch the k=3 most similar documents
docs =  db.similarity_search(query, k=3)


for doc in docs:
    doc_content = doc.page_content
    print(doc_content)

    doc_metadata = doc.metadata
    print(doc_metadata['Name of Activity'])
    print(doc_metadata['Listing URL'])