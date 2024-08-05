# from langchain.embeddings import HuggingFaceEmbeddings

# embeddings = HuggingFaceEmbeddings()
# text = "This is a test document."

# query_result = embeddings.embed_query(text)

# print(query_result)
# print(len(query_result))
import pandas as pd 
import psycopg2
import pgvector
from pgvector.psycopg2 import register_vector




from langchain_huggingface import HuggingFaceEmbeddings
# embeddings = HuggingFaceEmbeddings()
# text = "This is a test document."

# query_result = embeddings.embed_query(text)

# print(query_result)
# print(len(query_result))
def get_embeddings(text):
    embeddings = HuggingFaceEmbeddings()
    query_result = embeddings.embed_query(text)
    return query_result

df = pd.read_csv('Listings_Details.csv')

all_embeddings = []

for index, row in df.iterrows():
    print(index)
    text_to_embed = row[1]
    final_embeddings = get_embeddings(text_to_embed)

    if row[2] != "NA":
        date = f"Date is {row[2]}"
        final_embeddings += get_embeddings(date)

    if row[3] != "NA":
        location = f"Location is {row[3]}"
        final_embeddings += get_embeddings(location)

    if row[4] != "NA":
        synopsis = row[4]
        final_embeddings += get_embeddings(synopsis)

    if row[5] != "NA":
        description = row[4]
        final_embeddings += get_embeddings(description)

    all_embeddings.append(final_embeddings)

df['embeddings'] = all_embeddings
# df.to_csv('Listings_Details_Embeddings.csv', index=False, encoding='utf-8-sig') #write to csv

print(df)



#connect to postgresql database 

connection_string = "postgresql://postgres:123456@localhost:5433/wateraid"

conn = psycopg2.connect(connection_string)
cur = conn.cursor() #creates a cursor object cur which allows you to execute SQL commands and queries

#install pgvector
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;") #executes a SQL command to create the pgvector extension if it is not already installed
conn.commit() #commit current transaction to database

# Register the vector type with psycopg2
register_vector(conn)


# Create table to store embeddings and metadata
table_create_command = """
CREATE TABLE listings (
            id bigserial primary key, 
            title text,
            url text,
            content text,
            tokens integer,
            embedding vector(1536)
            );
            """

cur.execute(table_create_command)
cur.close()
conn.commit()