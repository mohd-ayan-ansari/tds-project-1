1.Execute scrapper.py to scrap data from the discourse threads that were uploaded between 1 Jan 2025 and 1 April 2025
2.Next run qa_extractor.py to exctract and filter out only the relevant data (Questions asked on the threads and the replies given to them)
3.Next run generate_faiss.py - Reads the CSV, generates embeddings (via AI Pipe), and builds the FAISS index + metadata.
