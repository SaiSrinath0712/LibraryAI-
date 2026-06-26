from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.book import Book
from pydantic import BaseModel
from typing import List, Dict, Any
import re

router = APIRouter(tags=["Chatbot"])

class ChatbotRequest(BaseModel):
    query: str

KB = {
    'machine learning': 'Machine Learning (ML) is a branch of AI where algorithms learn patterns from data automatically. Key types: ① Supervised Learning — learns from labeled data (Linear Regression, SVM, Decision Trees, Random Forest). ② Unsupervised Learning — finds patterns without labels (K-Means Clustering, PCA). ③ Reinforcement Learning — learns from rewards/penalties. Used in: spam detection, Netflix recommendations, fraud detection, image recognition.',
    'deep learning': 'Deep Learning uses multi-layered neural networks (deep neural networks) to learn complex hierarchical representations. Key architectures: CNN (Convolutional Neural Networks — images), RNN/LSTM (sequences, text, time series), Transformers (language — basis of ChatGPT, BERT). Applications: image recognition, speech recognition, machine translation, autonomous driving. Requires large datasets and GPU computation.',
    'artificial intelligence': 'Artificial Intelligence (AI) is the simulation of human intelligence in machines. Branches: Machine Learning, Deep Learning, Natural Language Processing (NLP), Computer Vision, Robotics, Expert Systems, Planning. Historical milestones: Turing Test (1950), Expert Systems (1980s), Deep Blue (1997), Deep Learning revolution (2012), ChatGPT (2022). AI is classified as Narrow AI (specific tasks) vs AGI (human-level general intelligence — not yet achieved).',
    'cloud computing': 'Cloud Computing delivers computing resources over the internet. Service models: IaaS (Infrastructure — AWS EC2, Azure VMs), PaaS (Platform — Google App Engine, Heroku), SaaS (Software — Gmail, Office 365). Deployment: Public (AWS/Azure/GCP), Private (on-premise), Hybrid. Benefits: scalability, pay-per-use, global availability. AI on cloud: AWS SageMaker, Azure ML, Google Vertex AI allow training large models without owning hardware.',
    'big data': 'Big Data refers to datasets too large/complex for traditional software to handle. The 5 Vs: Volume (petabytes), Velocity (real-time), Variety (structured/unstructured), Veracity (accuracy), Value (insights). Tools: Hadoop (HDFS distributed storage + MapReduce), Apache Spark (100x faster than MapReduce), Kafka (streaming), Hive (SQL queries on Hadoop), HBase (NoSQL on HDFS). Applications: social media analytics, IoT sensor data, genomics, financial trading.',
    'data structures': 'Data Structures organise data for efficient access and modification. Key types: Arrays (O(1) access), Linked Lists (O(n) access, O(1) insert), Stacks (LIFO — function calls, undo), Queues (FIFO — scheduling), Trees (BST O(log n), AVL self-balancing), Graphs (networks — Dijkstra, BFS/DFS), Hash Tables (O(1) average lookup — Python dicts). Each has different time/space complexity. Choosing the right data structure is crucial for algorithm performance.',
    'neural network': 'Neural Networks are computing systems inspired by biological neurons. Structure: Input layer → Hidden layers (feature extraction) → Output layer. Each neuron applies: output = activation(weights·inputs + bias). Training uses: Forward Propagation (compute output), Loss calculation, Backpropagation (compute gradients), Gradient Descent (update weights). Activation functions: ReLU (hidden layers), Sigmoid/Softmax (output). Types: Feedforward (basic), CNN (spatial), RNN/LSTM (sequential), Transformer (attention-based).',
    'python': 'Python is a high-level interpreted language created by Guido van Rossum (1991). Features: simple syntax, dynamic typing, extensive library ecosystem. Key domains: Data Science (NumPy, Pandas, Matplotlib), Machine Learning (Scikit-learn, TensorFlow, PyTorch, Keras), Web Dev (Django, Flask, FastAPI), Automation/Scripting. Python is #1 most popular language (TIOBE 2024) due to readability and versatility. Interpreted (CPython) but can be compiled (Cython, PyPy) for performance.',
    'algorithms': 'An Algorithm is a sequence of well-defined instructions to solve a problem. Categories: Sorting — Bubble O(n²), Merge O(n log n), Quick O(n log n) avg. Searching — Linear O(n), Binary O(log n). Graph — BFS/DFS, Dijkstra. Dynamic Programming. Greedy algorithms. Complexity is analyzed using Big-O notation.',
}

@router.post("/chatbot/query")
def query_chatbot(req: ChatbotRequest, db: Session = Depends(get_db)):
    query_text = req.query.strip().lower()
    
    kb_key = None
    for key in KB.keys():
        if key in query_text:
            kb_key = key
            break
            
    is_explanation_query = any(phrase in query_text for phrase in ["what is", "explain", "tell me", "define", "how does", "describe"])
    
    if is_explanation_query and kb_key:
        return {"reply": KB[kb_key], "books": []}
        
    if kb_key and not any(phrase in query_text for phrase in ["book", "find", "recommend", "show", "get"]):
        return {"reply": KB[kb_key], "books": []}
        
    books = []
    reply = ""
    
    if "available" in query_text or "free" in query_text:
        books = db.query(Book).filter(Book.available_copies > 0).all()
        reply = "Currently <strong>available books</strong>:"
    elif any(word in query_text for word in ["top", "best", "popular", "rated"]):
        books = db.query(Book).order_by(Book.rating.desc()).all()
        reply = "Our <strong>top-rated books</strong>:"
    elif "fiction" in query_text or "novel" in query_text:
        books = db.query(Book).filter(Book.genre == "Fiction").all()
        reply = "<strong>Fiction books</strong>:"
    elif "science" in query_text:
        books = db.query(Book).filter(Book.genre == "Science").all()
        reply = "<strong>Science books</strong>:"
    elif "history" in query_text:
        books = db.query(Book).filter(Book.genre == "History").all()
        reply = "<strong>History books</strong>:"
    elif "self-help" in query_text or "motivation" in query_text or "habit" in query_text or "self help" in query_text:
        books = db.query(Book).filter(Book.genre == "Self-Help").all()
        reply = "<strong>Self-Help books</strong>:"
    elif any(word in query_text for word in ["technology", "ai", "machine learning", "python", "programming", "data", "algorithm", "computer"]):
        books = db.query(Book).filter(Book.genre == "Technology").all()
        reply = "<strong>Technology & AI books</strong>:"
    elif "biography" in query_text or "autobiography" in query_text:
        books = db.query(Book).filter(Book.genre == "Biography").all()
        reply = "<strong>Biography books</strong>:"
    elif "philosophy" in query_text:
        books = db.query(Book).filter(Book.genre == "Philosophy").all()
        reply = "<strong>Philosophy books</strong>:"
    elif any(word in query_text for word in ["maths", "math", "calculus", "algebra", "statistics"]):
        books = db.query(Book).filter(Book.genre == "Mathematics").all()
        reply = "<strong>Mathematics books</strong>:"
    else:
        search = f"%{query_text}%"
        books = db.query(Book).filter(
            Book.title.like(search) | 
            Book.author.like(search) | 
            Book.genre.like(search) | 
            Book.tags.like(search)
        ).all()
        reply = f"Results for \"<em>{req.query}</em>\":" if books else ""

    if not books and not reply:
        return {
            "reply": "I couldn't find info on that. Try: <em>machine learning, deep learning, Python, cloud, big data, algorithms, data structures, neural networks</em> — or ask for a specific genre!",
            "books": []
        }
        
    if not books:
        return {
            "reply": "No books matched that query. Try a different keyword!",
            "books": []
        }
        
    matched_books = []
    for b in books[:4]:
        matched_books.append({
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "genre": b.genre,
            "available": b.available_copies,
            "rating": b.rating
        })
        
    return {
        "reply": reply,
        "books": matched_books
    }
