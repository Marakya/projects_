import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import OpenAI
import os
import json

class SimpleDialogSystem:
    def __init__(self, api_key):
        self.api_key = api_key

        # Создаем  клиента Chroma
        self.base_directory = "./data"
        os.makedirs(self.base_directory, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(path=os.path.join(self.base_directory, "chroma"))
        self.collection_name = "thermostat_collection"

        # Удаляем коллекцию, если она существует
        existing_names = self.chroma_client.list_collections()
        if self.collection_name in existing_names:
            self.chroma_client.delete_collection(name=self.collection_name)

        # Создаем коллекцию с указанием модели по созданию  эмбеддингов
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L12-v2"
        )
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

        # Инициализация базы знаний
        self.setup_knowledge_base()

    def setup_knowledge_base(self):
        """Заполнение базы знаний термостатами"""
        documents = [
            "Термостаты обычно поддерживают температуру в диапазоне 5-30°C.",
            "Если термостат не поддерживает нужную температуру, проверьте батарейки и соединение с системой.",
            "Разница между текущей и желаемой температурой более 1°C может указывать на проблему.",
            "Проблемы с термостатом чаще возникают при экстремальных температурах (очень холодно или жарко).",
            "Перезагрузка термостата может решить временные проблемы с температурой."
        ]
        metadatas = [{"source": "manual", "type": "fact"} for _ in range(len(documents))]
        ids = [f"doc_{i}" for i in range(len(documents))]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
               
    def get_relevant_knowledge(self, query, n_results=1):
        """Извлечение релевантных документов из базы данных Chroma"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances"]
        )

        knowledge_parts = []
        for doc, dist in zip(results['documents'][0], results['distances'][0]):
            knowledge_parts.append(f"{doc} (релевантность: {1-dist:.2f})")

        return "\n".join(knowledge_parts)

    def generate_response(self, instruction):
        """Генерация ответа с использованием OpenRouter"""
        knowledge = self.get_relevant_knowledge(instruction)
        full_prompt = f"""Контекстная информация о термостатах:
{knowledge}

На основе этой информации выполни следующую задачу: {instruction}"""

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        model = "google/gemini-2.0-flash-exp:free"
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": full_prompt}]
        )
        return completion.choices[0].message.content

    def chat_mode(self):
        """Режим общения с пользователем"""
        print("Вы можете задать дополнительные вопросы. Введите 'exit' для выхода.")
        while True:
            user_input = input("Вы: ")
            if user_input.lower() == 'exit':
                print("Диалог завершен.")
                break
            response = self.generate_response(user_input)
            print(f"Система: {response}")

if __name__ == "__main__":
    api_key = ""
    dialog_system = SimpleDialogSystem(api_key)

    # Запуск чата
    dialog_system.chat_mode()
