import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import OpenAI
import os
import json
from typing import List, Dict, Optional

class DialogMessage:
    def __init__(self, role: str, content: str, children: Optional[List['DialogMessage']] = None):
        self.role = role  # 'system' или 'user'
        self.content = content
        self.children = children or []  # Вложенные сообщения

    def to_dict(self) -> Dict:
        return {
            'role': self.role,
            'content': self.content,
            'children': [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DialogMessage':
        return cls(
            role=data['role'],
            content=data['content'],
            children=[cls.from_dict(child) for child in data.get('children', [])]
        )

class DialogHistory:
    def __init__(self):
        self.root_messages: List[DialogMessage] = []
        self.current_branch: List[DialogMessage] = []

    def add_message(self, role: str, content: str, is_new_branch: bool = False):
        new_msg = DialogMessage(role, content)

        if is_new_branch or not self.current_branch:
            self.root_messages.append(new_msg)
            self.current_branch = [new_msg]
        else:
            last_msg = self.current_branch[-1]
            last_msg.children.append(new_msg)
            self.current_branch.append(new_msg)

    def to_json(self) -> str:
        return json.dumps([msg.to_dict() for msg in self.root_messages], ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'DialogHistory':
        history = cls()
        data = json.loads(json_str)
        history.root_messages = [DialogMessage.from_dict(msg) for msg in data]
        return history

class DialogNode:
    def __init__(self, prompt_instruction, options=None, variable=None):
        self.prompt_instruction = prompt_instruction
        self.options = options or {}
        self.variable = variable

class DialogSystem:
    def __init__(self, api_key):
        self.api_key = api_key
        self.current_node = None
        self.context = {}
        self.history = DialogHistory()

        self.base_directory = "./data"
        os.makedirs(self.base_directory, exist_ok=True)

        # Создаем клиента с указанием пути
        self.chroma_client = chromadb.PersistentClient(path=os.path.join(self.base_directory, "chroma"))
        self.collection_name = "thermostat_collection"

        # Удаляем коллекцию, если уже существует
        existing_names = self.chroma_client.list_collections()

        if self.collection_name in existing_names:
            self.chroma_client.delete_collection(name=self.collection_name)


        # Создаем коллекцию с функцией для эмбеддингов
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L12-v2"
        )
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

        # Заполняем базу знаний
        self.setup_knowledge_base()
        # Указываем основную логику "хождения" по узлам
        self.nodes = {
            'start': DialogNode(
                "Ты ассистент диагностики термостата. Начни диалог с пользователем, спроси, какая проблема. Пиши кратко и по делу.",
                {
                    'temp': ("Скажи: 'Термостат не поддерживает нужную температуру'", 'ask_current_temp'),
                    'other': ("Скажи: 'Другая проблема'", 'end')
                }
            ),
            'ask_current_temp': DialogNode("Спроси кратко и четко - какая температура сейчас в комнате", variable='current_temp'),
            'ask_desired_temp': DialogNode("Спроси кратко и четко - какая температура должна быть в комнате", variable='desired_temp'),
            'ask_time': DialogNode("Спроси кратко и четко - когда это произошло (утром, днем или вечером)?", variable='time_of_day'),
            'ask_duration': DialogNode("Спроси кратко и четко - как долго длится проблема в часах?", variable='duration'),
            'check_duration': DialogNode("", options={
                'long': ("", 'offer_ticket'),
                'short': ("", 'wait_advice')
            }),
            'offer_ticket': DialogNode("Спроси кратко и четко - хочет ли пользователь создать заявку в техподдержку?", options={
                'yes': ("Скажи: 'Да'", 'create_ticket'),
                'no': ("Скажи: 'Нет'", 'end')
            }),
            'create_ticket': DialogNode("Спроси кратко и четко - что заявка создана, укажи данные , которые ввел пользователь- текущую температуру, желаемую температуру и время суток.", options={'ok': ("Скажи: 'ОК'", 'end')}),
            'wait_advice': DialogNode("Скажи пользователю, что нужно подождать 1 час и обратиться снова, если проблема останется.", options={'ok': ("Скажи: 'ОК'", 'end')}),
            'end': DialogNode("Скажи, что диагностика завершена. Теперь вы можете задать свои вопросы."),
        }
    # Функция для заполнения базы данных
    def setup_knowledge_base(self):
        """Инициализирует базу знаний с информацией о термостатах"""
        documents = [
            "Термостаты обычно поддерживают температуру в диапазоне 5-30°C.",
            "Если термостат не поддерживает нужную температуру, проверьте батарейки и соединение с системой.",
            "Разница между текущей и желаемой температурой более 1°C может указывать на проблему. ",
            "Проблемы с термостатом чаще возникают при экстремальных температурах (очень холодно или жарко).",
            "Перезагрузка термостата может решить временные проблемы с температурой.",
            "Термостаты могут некорректно работать при низком заряде батареи.",
            "Если проблема длится более 1 часа, рекомендуется создать заявку в техподдержку.",
            "Утренние и вечерние часы - пиковое время для работы систем отопления/охлаждения.",
            "Термостаты могут медленнее реагировать при большой разнице температур внутри и снаружи.",
            "Проверьте, не закрыт ли термостат мебелью или шторами, это влияет на точность измерений.",
            "Современные термостаты часто имеют Wi-Fi подключение для удаленного управления.",
            "Калибровка термостата может потребоваться, если показания температуры кажутся неточными.",
            "Некоторые термостаты имеют функцию геозоны для автоматической регулировки температуры.",
            "Рекомендуется устанавливать термостат на внутренней стене, вдали от источников тепла и холода."
        ]
        metadatas = [{"source": "manual", "type": "fact"} for _ in range(len(documents))]
        ids = [f"doc_{i}" for i in range(len(documents))]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    # Генерация ответа с учетом данных извлеченных из БД
    def generate_response(self, instruction):
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

    # Извлечение данных из БД
    def get_relevant_knowledge(self, query, n_results=1):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances"]
        )

        knowledge_parts = []
        for doc, dist in zip(results['documents'][0], results['distances'][0]):
            knowledge_parts.append(f"{doc} (релевантность: {1-dist:.2f})")

        return "\n".join(knowledge_parts)

    def start(self):
        self.current_node = self.nodes['start']
        self.context = {}
        self.process_node()

    # Обработка текущего узла
    def process_node(self):
        node = self.current_node

        if node == self.nodes['check_duration']:
            duration = float(self.context.get('duration', 0))
            self.current_node = self.nodes['offer_ticket'] if duration > 1 else self.nodes['wait_advice']
            self.process_node()
            return

        if node == self.nodes['create_ticket']:
            temp = self.context.get('current_temp', 'неизвестно')
            desired = self.context.get('desired_temp', 'неизвестно')
            time = self.context.get('time_of_day', 'неизвестно')
            instruction = f"Заявка создана. Текущая температура: {temp}°C, желаемая: {desired}°C, время суток: {time}."
        else:
            instruction = node.prompt_instruction

        prompt = self.generate_response(instruction)
        self.history.add_message('system', prompt)
        print(f"Система: {prompt}")

        if node.options:
            for key, (option_text, _) in node.options.items():
                option_text = self.generate_response(option_text)
                print(f"  {key}: {option_text}")

    # Обработка ответа пользователя
    def user_response(self, response):
        if not self.current_node:
            print("Диалог не начат. Используйте start().")
            return

        self.history.add_message('user', response)

        node = self.current_node

        if node.variable:
            self.context[node.variable] = response
            next_node_key = None

            if node == self.nodes['ask_current_temp']:
                next_node_key = 'ask_desired_temp'
            elif node == self.nodes['ask_desired_temp']:
                next_node_key = 'ask_time'
            elif node == self.nodes['ask_time']:
                next_node_key = 'ask_duration'
            elif node == self.nodes['ask_duration']:
                next_node_key = 'check_duration'

            if next_node_key:
                self.current_node = self.nodes[next_node_key]
        else:
            if response in node.options:
                _, next_node_key = node.options[response]
                self.current_node = self.nodes[next_node_key]
            else:
                print("Неверный вариант ответа")
                return

        self.process_node()

    # Реализация общения с LLM
    def chat_mode(self):
        print("Вы можете задать дополнительные вопросы. Введите 'exit' для выхода.")
        while True:
            user_input = input("Вы: ")
            if user_input.lower() == 'exit':
                print("Диалог завершен.")
                break
            response = self.generate_response(user_input)
            self.history.add_message('system', response)
            print(f"Система: {response}")

    #Сохранение истории
    def save_history(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.history.to_json())
            
    # Загрузка истории
    def load_history(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            self.history = DialogHistory.from_json(f.read())

if __name__ == "__main__":
    api_key = ""
    system = DialogSystem(api_key)
    system.start()

    responses = ['temp', '22', '24', 'день', '1.5', 'yes']
    for response in responses:
        print(f"Пользователь: {response}")
        system.user_response(response)

    # Сохраняем историю
    system.save_history("dialog_history.json")

    # Продолжаем диалог
    system.chat_mode()
