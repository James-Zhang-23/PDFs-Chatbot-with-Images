# Private PDFs Chatbot with Image Output using Langchain and Llama 2

## How it works
1. PDFs as Input:
Upload multiple PDF files as input.
2. Text Chunk Extraction:
Content from the PDFs is chunked into 1000 characters smaller chucks with 200 characters overlap.
3. Embeddings with MiniLM-L6:
Each text chunk is processed using the MiniLM-L6 model to generate embeddings and stored in Faiss Vector Database.
4. Image Extraction:
Images are extracted from the PDFs with corresponding page number and stored in MongoDB.
5. Question Processing and Matching:
Upon receiving a user question:
The question is transformed into an embedding.
The question's embedding is compared with the vector database to find most similar text chunks.
6. LLM (Llama2) for Text Answer Generation:
The top 4 most similar text chunks and conversation history are sent to LLM for answer generation. 
7. Image Answer Generation:
The top 2 most similar text chunks are used to find the corresponding images from MongoDB.


## Requirements
1. Install the following Python packages:
```
pip install streamlit pymupdf langchain python-dotenv faiss-cpu sentence_transformers pymongo llama-cpp-python
```

2. Download the Llama2-chat-7B 5-bits quantized GGUF model from https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF
Place it in the models folder


## How to run
```
streamlit run app.py
```

### Evaluation
Average 30 seconds per question with inference on CPU
Average 10 seconds per embedding for 100 pages PDF file
Max RAM required: 7GB                                
Disk usage: 4.8GB
