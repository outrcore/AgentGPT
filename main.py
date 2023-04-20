from promptBot import promptBot
from chatbot import chatbot
from helpers import store_embedding, retrieve, store_initial_system_messages, i, messages, timestamp
from historical_context_bot import historical_context_bot
from recent_context_bot import recent_context_bot
from task_bot import task_bot



def main(input_text):
    global i, messages
    # Display User Input in terminal
    print("Input:")
    print(input_text)

    # Initialize list of messages to the system to give it an identity
    if i==0:
        store_initial_system_messages()

    # Think about adding a {"role": 'system', "name": "context", "content": '{additional_context}'}
    # To the bots somewhere. This is supposedly a better way to give context to the bots

    # Use this website as a breakdown. Can impliment another type of bot that uses bots for all of these?
    #https://gptforwork.com/tools/prompt-generator

    # Provide pure message history buffer
    message_buffer = retrieve(10)

    # Create a string containing the recent conversation history
    conversation_history = ""
    for message in message_buffer:
        if message["role"] == "user":
            conversation_history += "User: " + message["content"] + "\n"
            messages.append({"role": "User", "content": conversation_history, "timestamp": timestamp.isoformat()})
        else:
            conversation_history += "AI: " + message["content"] + "\n"
            messages.append({"role": "AI", "content": conversation_history, "timestamp": timestamp.isoformat()})

    # Get tasks from task_bot
    #task_list = task_bot(input)

    # Use the retrieve function to get the context-infused query
    #query_with_contexts = historical_context_bot(input)

    # Use the retrieve function to get the context-infused query
    # This works, but can sometimes provide weird, unexpected responses because the bot will start talking about something that is relevant a few messages ago
    recent_messages = retrieve(15)
    summerize_recent_messages = recent_context_bot(recent_messages)

    # Call the promptBot Function to build the prompt
    #promptbot_output = promptBot(input_text)

    # Call the chatBot Function to demonstrate the response
    #chatbot_output = chatbot(input_text, summerize_recent_messages, query_with_contexts, promptbot_output, conversation_history) # need Task List
    chatbot_output = chatbot(input_text, conversation_history, summerize_recent_messages)

    # Store the User Input in the Pinecone Database
    store_embedding('User', input_text)

    # Store the promptBot response in the Pinecone Database
    #store_embedding('promptBot', promptbot_output)

    # Store the chatBot response in the Pinecone Database
    store_embedding('chatBot', chatbot_output)


    return {"chatbot_response": chatbot_output}