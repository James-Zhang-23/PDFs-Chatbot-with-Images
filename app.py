import streamlit as st
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from htmlTemplates import css, bot_template, user_template
from langchain.llms import LlamaCpp
from langchain.embeddings import HuggingFaceEmbeddings
from pymongo import MongoClient
import pdf_text
import pdf_image


def get_conversation_chain(vectorstore):
    # llm = ChatOpenAI()
    llm = LlamaCpp(
        model_path="models/llama-2-7b-chat.Q5_K_M.gguf",  n_ctx=2048, n_batch=512, temperature=0.9, top_p=0.2)

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}),
        memory=memory,
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    prompt_inputs = st.session_state.vector_db.as_retriever(
        search_type="similarity", search_kwargs={"k": 2}).get_relevant_documents(user_question)
    related_images = pdf_image.get_image(prompt_inputs)

    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

    # streamlit add images below the chat
    if related_images:
        st.subheader("Related images")
        for image in related_images:
            st.image(image, use_column_width=False)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with PDFs",
                       page_icon=":robot_face:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "db" not in st.session_state:
        st.session_state.db = None

    st.header("Chat with PDFs :robot_face:")
    user_question = st.text_input("Ask questions about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):

                # check if this pdf file is already in "processed_pdfs" folder
                # if yes, delete it from pdf_docs to avoid duplicate processing
                # if not, save it to "processed_pdfs" folder
                for pdf in pdf_docs:
                    if os.path.exists("processed_pdfs/" + pdf.name):
                        pdf_docs.remove(pdf)
                        print(pdf.name + " is already processed.")
                    else:
                        with open(os.path.join('processed_pdfs', pdf.name), "wb") as f:
                            f.write(pdf.getvalue())
                        print(pdf.name + " is saved to processed_pdfs folder.")

                if len(pdf_docs) != 0:
                    # get pdf text
                    raw_text = pdf_text.get_pdf_text(pdf_docs)
                    # get the text chunks
                    text_chunks = pdf_text.get_text_chunks(raw_text)
                    # generate embeddings
                    vectorstore = pdf_text.generate_embedding(text_chunks)
                    # save images to mongodb
                    pdf_image.save_images_to_mongodb(
                        pdf_docs, "mongodb://localhost:27017/", "pdfs_chatbot", "images")
                else:
                    embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2")
                    vectorstore = FAISS.load_local("faiss_index", embeddings)

                st.session_state.vector_db = vectorstore

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)


if __name__ == '__main__':
    main()
