import openai
from datetime import datetime
from helpers import messages, i, num_messages_to_fetch, timestamp, CHAT_COMPLETIONS_MODEL, retrieve  # Add this line


# Chatbot function that takes input from user, adds it to messages list, sends to the model and generates a response
#def chatbot(input, recent_messages_summarized, historical_messages_summarized, promptbot, message_buffer):
def chatbot(input, message_buffer, recent_convo_summarized):
    global i, messages, num_messages_to_fetch, timestamp  # Declare i and messages as global to modify their values inside the function
    
    print("Starting chatbot function...")  # <-- Add this

    reply = ''

    if input:
        print("Message Buffer:")
        print(message_buffer)
        print("Recent Convo Summerized:")
        print(recent_convo_summarized)
        print("Recent Convo Summerized:")
        #print(input_context)
        print("Input:")
        print(input)

        #print("Generating response with OpenAI...")
        # Generate a response with OpenAI using the context-infused query
        chat = openai.ChatCompletion.create(
            model=CHAT_COMPLETIONS_MODEL,
            messages=[{"role": "system", "content": "You are BetBot. Your job is to take the provided context from your assistant chatGPT3.5-turbo chatbot models and respond to the user input. One model gives historical context based on conversation history, the other gives you a summery of the last 15 messages. You are also given a message buffer than shows the last 5 conversational texts, this should be taken into account more than the other two models. The context from each assistant will be on new lines, with Historical Context Bot first, then Recent Conversation Context second, then the message buffer with the most recent messages, so you can determine which is which. You take the previous conversation context, recent message summery, message buffer and provide a response to the users input."},
                    #{"role": "assistant", "content": historical_messages_summarized + "\n" + recent_messages_summarized  + "\n" + message_buffer},
                    {"role": "assistant", "content": message_buffer},
                    {"role": "assistant", "content": recent_convo_summarized},
                    #{"role": "assistant", "content": input_context},
                    {"role": "user", "content": input}],
            temperature=0.5,
            max_tokens=2500,
            top_p=.90,
            frequency_penalty=-0.1,
            presence_penalty=-0.1,
            stop=None
        )

        # Get the response
        reply = chat.choices[0].message.content

        # Add OpenAI response to messages list
        messages.append({"role": "assistant", "content": reply, "timestamp": timestamp.isoformat()})

    
    print("=========Reply:============")
    print(reply)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    
    return reply

__all__ = ['chatbot']
