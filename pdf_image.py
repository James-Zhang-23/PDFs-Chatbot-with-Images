from pymongo import MongoClient
import fitz
import os

def save_images_to_mongodb(pdf_docs, db_url, db_name, collection_name):

    # Connect to the MongoDB database
    client = MongoClient(db_url)
    db = client[db_name]
    collection = db[collection_name]

    # Create a unique index on the relevant fields
    collection.create_index([("file_name", 1), ("page_number", 1), ("image", 1)], unique=True)

    # Loop through the PDFs
    for pdf in pdf_docs:
        pdf_name = pdf.name
        # Iterating over the pages in the PDF
        for page_num in range(pdf.page_count):
            # Get the page
            page = pdf[page_num]

            # Get the images on the page
            img_list = page.get_images(full=True)
            for img in img_list:
                base_image = pdf.extract_image(img[0])
                image_data = base_image["image"]

                # Create a dictionary to store the image data and page number
                image_dict = {
                    "file_name": pdf_name,
                    "page_number": page_num+1,
                    "image": image_data
                }

                collection.update_one(image_dict, {"$setOnInsert": image_dict}, upsert=True)
    # print(collection.count_documents({}))

    # Close the MongoDB connection
    client.close()

def get_image(prompt_inputs):
    # Connect to the MongoDB database
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pdfs_chatbot"]
    collection = db["images"]

    # Find page number related to the each prompt input
    images = []
    processed_pages = set()
    for prompt_input in prompt_inputs:
        text_truck = prompt_input.page_content
        file_name, page_number = find_page_number_of_paragraph(text_truck)

        if file_name and page_number and (file_name, page_number) not in processed_pages:
            processed_pages.add((file_name, page_number))
            image_cursor = collection.find({"file_name": file_name, "page_number": page_number})
            for image in image_cursor:
                images.append(image["image"])

    # Close the MongoDB connection
    client.close()

    return images


def find_page_number_of_paragraph(text_truck):
    for file_name in os.listdir("processed_pdfs"):
        pdf = fitz.open("processed_pdfs/" + file_name)
        for page_num in range(pdf.page_count):
            if text_truck in pdf[page_num].get_text():
                return pdf.name, page_num + 1

    return None, None

if __name__ == "__main__":
    # clear the mongodb collection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pdfs_chatbot"]
    collection = db["images"]
    collection.delete_many({})
    client.close()

    pdf_docs = []
    # Open all the PDF file in the folder path processed_pdfs
    for file_name in os.listdir("processed_pdfs"):
        pdf_docs.append(fitz.open("processed_pdfs/" + file_name))

    save_images_to_mongodb(pdf_docs, "mongodb://localhost:27017/", "pdfs_chatbot", "images")
