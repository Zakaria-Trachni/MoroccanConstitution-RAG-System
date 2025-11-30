from groq import Groq
from sentence_transformers import SentenceTransformer
import numpy as np
from faiss import read_index
import sqlite3

class PromptVector():
    def __init__(self):
        self.model = SentenceTransformer('multi-qa-mpnet-base-cos-v1')
        # Load the saved FAISS index
        self.index = read_index("databases/constitution_index.faiss")
        return

    def Prompt_Preprocess(self, prompt:str):
        self.doc = self.nlp(u"{}".format(prompt))

        entity_tokens = {token for ent in self.doc.ents for token in ent}
        preprosseced_tokens = [token.lemma_.lower() if token not in entity_tokens else token.lemma_ for token in self.doc if token.is_punct == False and token.is_stop == False ]
        self.preprosseced_prompt = " ".join(preprosseced_tokens)
        return self.preprosseced_prompt

    def Vectorize_Prompt(self, prompt:str):
        prompt_embedding = self.model.encode([prompt], normalize_embeddings=True)
        return prompt_embedding
    
    def get_articles(self):
        conn = sqlite3.connect("databases/articles.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Articles")
        rows = cursor.fetchall()
        conn.close()

        return rows
    
    def search(self, prompt:str, k:int = 1):
        D, I = self.index.search(np.array(self.Vectorize_Prompt(prompt)), k)
        
        articles = []
        article_numbers = []

        rows = self.get_articles()
        for id, num, row in rows:
            articles.append(row)
            article_numbers.append(id)

        results = []
        for rank, index_in_articles in enumerate(I[0]):
            article_num = article_numbers[index_in_articles]
            article_text = articles[index_in_articles]
            similarity_score = float(D[0][rank])
            results.append((article_num, article_text, similarity_score))
        return results

class LLM:
    def __init__(self):
        self.GROQ_API_KEY = "GROQ_API_KEY"

        self.client = Groq(
            api_key= self.GROQ_API_KEY
        )
        return
    
    def chatbot(self, prompt:str):
        self.prompt = PromptVector()
        self.answer = self.prompt.search(prompt, 1)

        self.article_number = self.answer[0][0]
        self.article = self.answer[0][1]
        self.similarity = self.answer[0][2]

        self.chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        You are a helpful AI assistant designed to answer questions strictly related to the Moroccan Constitution. Please follow these rules:
                        1. Answer only if the question is a greeting or thanks expression or if the similarity score is greater than 0.4. If the score is 0.4 or below and the question is not a greeting or thanks expression, respond politely with: "I'm here to assist with questions related to the Moroccan Constitution, but I couldn't find enough relevant information for your request. Please try rephrasing your question."
                        2. Only answer questions that are clearly about the Moroccan Constitution. Do not provide responses to unrelated topics.
                        3. For greeting expressions: Respond with a friendly and short greeting, and explain your role, such as: "Hello! I'm here to help you understand the Moroccan Constitution. Ask me anything related to it!"
                        4. For thanks expressions: Reply kindly.
                        5. Always keep your tone formal, polite, and informative.
                        6. Always mention the article number.
                        Article: {self.article}
                        Article content: {self.article_number}
                        Similarity: {self.similarity}"""
                },
                {
                    "role": "user",
                    "content": f"""Question: {prompt}"""
                }
            ],
            model="llama-3.1-8b-instant",
        )

        answer = str(self.chat_completion.choices[0].message.content)
        html_answer = answer.replace("\n", "<br>")

        return html_answer, self.article_number, self.similarity

def get_answer(question, language='en'):
    chat = LLM()
    answer, article_number, relevance = chat.chatbot(question)
    print("--------------------------------\n")
    print(">> Article ", article_number)
    print(">>", answer)
    print(">> Relevance: ", relevance)
    print("--------------------------------")
    return answer
