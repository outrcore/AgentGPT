# Import necessary libraries
import openai
from datetime import datetime
import pytz
import pinecone

# Set OpenAI API key
openai.api_key = "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"
pinecone.init(api_key="c5b6f4ea-be3a-4a7b-8f1d-6cc992641e57", environment="us-east-1-aws")

# Define the models
CHAT_COMPLETIONS_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
COMPLETIONS_MODEL = "text-davinci-003"

# Define the Pinecone index
index_name = "chatbot-embeddings"
# Check if index already exists, if not, create it
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, metric="cosine", dimension=1536)
# Instantiate Pinecone client
pinecone_client = pinecone.Index(index_name)
# Below are functions to resume the conversation from the last vector index
# Function to read the vector index from a file
def read_vector_index(filename):
    try:
        with open(filename, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0
# Function to write the vector index to a file
def write_vector_index(filename, index):
    with open(filename, "w") as f:
        f.write(str(index))
# Read the current vector index from a file
VECTOR_INDEX_FILE = "vector_index.txt"
i = read_vector_index(VECTOR_INDEX_FILE)

# Number of messages to fetch from Pinecone when the program starts
initial_messages_to_fetch = 1
# Number of messages to fetch from Pinecone after the program has started
num_messages_to_fetch = 10

# Create timestamp
set_timezone = pytz.timezone('America/Chicago') 
timestamp = datetime.now(set_timezone)



messages = []

# Function to fetch stored messages from Pinecone
def fetch_stored_messages(num_messages):
    last_stored_ids = [str(i) for i in range(max(0, i - num_messages), i)]
    
    # Add this check to avoid querying Pinecone with an empty list of IDs
    if not last_stored_ids:
        return []
    
    fetched_data = pinecone_client.fetch(ids=last_stored_ids)  # Use fetch function
    messages = []
    sorted_data = sorted(fetched_data['vectors'].items(), key=lambda x: int(x[0]))

    for key, value in sorted_data:
        metadata = value['metadata']
        msg = {"role": metadata["role"][0], "content": metadata["content"][0]}
        messages.extend([msg])

    return messages

# Function to generate embeddings and store them in Pinecone
def store_embedding(role, input):
    global i # Declare i and messages as global to modify their values inside the function
  
    # get ids
    ids_batch = [str(i)]
    tracker = str(i) + role

    # create embeddings
    res = openai.Embedding.create(input=input, engine=EMBEDDING_MODEL)
    embeds = [record['embedding'] for record in res['data']]

    # cleanup metadata
    meta_batch = [{
        'role': [role],
        'content': [input],
        'timestamp': [timestamp],
        'tracker': [tracker],
    }]

    to_upsert = list(zip(ids_batch, embeds, meta_batch))

    # upsert to Pinecone
    pinecone_client.upsert(vectors=to_upsert)

    # Iterate the ID for the Pinecone Database 
    i += 1
    # Store the ID so we know where we're at in the Pinecone Database
    write_vector_index(VECTOR_INDEX_FILE, i)


############################
    
def store_initial_system_messages():
    global i, messages
    
    system_messages = [
        {"role": "system", "content": "You are BetBot"},
        {"role": "system", "content": "You are a betting expert."},
        {"role": "system", "content": "You are a sports expert."},
        {"role": "system", "content": "You are a sports betting expert."},
        {"role": "system", "content": "You are a sports betting odds expert."},
        {"role": "system", "content": "You are a mathmatical expert."},
        {"role": "system", "content": "You are a data-analyst."},
        {"role": "system", "content": "You are a general knowledge expert."},

        {"role": "system", "content": "You are fun and charming."},
        {"role": "system", "content": "You love to talk to people and engage in conversation."},
        {"role": "system", "content": "When giving information, you are throurgh and detailed, but do so in a simple or humorous way."},

        {"role": "system", "content": "Your main task is to provide betting assistance to the user."},
        {"role": "system", "content": "Your secondary task is to provide insight to betting odds to the user."},
        {"role": "system", "content": "Your additional task is to provide insight to betting outcomes to the user."},
        {"role": "system", "content": "Your additional task is to provide insight to betting probabilities to the user."},
        {"role": "system", "content": "Your primary task is to provide insight to the user to help them pick good bets based on odds, probability and statistics."},

        {"role": "system", "content": "You use your knowledge of sports to help complete your main task."},
        {"role": "system", "content": "You use your knowledge of sports betting to help complete your main task."},
        {"role": "system", "content": "You use your knowledge of sports betting odds to help complete your main task."},

        {"role": "system", "content": "You use insights from mathamatics of odds to help complete your main task."},
        {"role": "system", "content": "You use insights from mathamatics of outcomes to help complete your main task."},
        {"role": "system", "content": "You use insights from mathamatics of probabilities of outcomes to help complete your main task."},

        {"role": "system", "content": "You use relevant searchs on Google to help complete your main task."},
        {"role": "system", "content": "You use betting odds across multiple books to help complete your main task."},
    ]
    
    for message in system_messages:
        reply = message["content"]
        input = ""  # Empty input since these are system messages
        
        #store_embedding(reply, input, i)
        ids_batch = [str(i)]
        # get texts to encode
        texts = reply
         # create embeddings
        res = openai.Embedding.create(input=texts, engine=EMBEDDING_MODEL)
        embeds = [record['embedding'] for record in res['data']]

        # Using the reply in  under_input as well because I heard the system takes it in more
        # cleanup metadata
        #update to 
        # 'role': 'user' or 'assistant'
        # 'content': "content"
        #'timestamp': "timestamp"
        meta_batch = [{
            'role': ['system'],
            'content': [reply],
            'timestamp': [timestamp],
            'tracker': ['system'],
        }]

        to_upsert = list(zip(ids_batch, embeds, meta_batch))

        # upsert to Pinecone
        pinecone_client.upsert(vectors=to_upsert)

        messages.append({"role": "system", "content": reply, "timestamp": timestamp.isoformat()})
        
        i += 1
        write_vector_index(VECTOR_INDEX_FILE, i)


# Fetch the last 10 stored messages from Pinecone when the program starts
messages.extend(fetch_stored_messages(min(initial_messages_to_fetch, i * 2)))

# Fetch the last 5 stored messages from Pinecone
messages.extend(fetch_stored_messages(5))


def get_initial_conversation_history():
    conversation_history = ""
    for message in messages:
        if message["role"] == "user":
            conversation_history += "User: " + message["content"] + "\n"
        else:
            conversation_history += "AI: " + message["content"] + "\n"
    return conversation_history.strip()


def retrieve(num_messages_to_fetch):
    # Fetch the last stored messages from Pinecone
    recent_messages = fetch_stored_messages(num_messages_to_fetch)    

    return recent_messages


__all__ = ['read_vector_index', 'write_vector_index', 'fetch_stored_messages', 'store_embedding', 'store_initial_system_messages', 'get_initial_conversation_history', 'retrieve']
