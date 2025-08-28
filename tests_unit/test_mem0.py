from mem0 import Memory
from dotenv import load_dotenv

load_dotenv()

config = {
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "user": "skim",
            "password": "",
            "host": "127.0.0.1",
            "port": "5432",
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-large"
        }
    }
}

m = Memory.from_config(config)

def add_memories(m, user_id: str = "skim"):
    contents = [
        "My name is Sung-Cheol Kim.",
        "I am a Data Scientist.",
        "I like to code with cursor ai.",
        "my favorite computer language is python.",
        "I am interested in LLM and AI.",
    ]
    for content in contents:
        m.add(content, user_id=user_id, metadata={"category": "personal"})

# Get all memories
# all_memories = m.get_all(user_id="skim")
# print(all_memories)

related_memories = m.search(query="favorite computer language?", user_id="skim")
# print(related_memories)

for item in related_memories['results']:
    if item['score'] < 0.5:
        # print(item['id'])
        print(f"{item['memory']} (score: {item['score']})")