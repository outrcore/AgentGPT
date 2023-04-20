const chatContainer = document.getElementById('messages-container');
const userInput = document.getElementById('user-input');
const showMoreButton = document.getElementById('show-more');
const submitButton = document.getElementById('submit');


function appendMessage(text, isUser) {
  const message = document.createElement('div');
  message.classList.add('message');
  message.classList.add(isUser ? 'user-message' : 'ai-message');

  const formattedText = formatChatbotOutput(text);

  const tempContainer = document.createElement('div');
  tempContainer.innerHTML = formattedText.replace(/\n/g, '<br>');

  while (tempContainer.firstChild) {
    if (tempContainer.firstChild.tagName === 'CODE-BLOCK') {
      const pre = document.createElement('pre');
      pre.textContent = tempContainer.firstChild.textContent;
      message.appendChild(pre);
    } else {
      message.appendChild(tempContainer.firstChild);
    }
  }

  chatContainer.appendChild(message);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function getResponse(inputText = '') {
  return await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: inputText })
  })
    .then(response => response.json())
    .then(data => {
      return data.response;
    });
}

submitButton.addEventListener('click', async () => {
  const inputText = userInput.value;
  userInput.value = '';

  appendMessage(inputText, true);
  appendMessage(await getResponse(inputText), false);
});

userInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    submitButton.click();
  }
});

showMoreButton.addEventListener('click', async () => {
  const numMessagesToFetch = 5;  // Define the number of messages to fetch here
  const response = await fetch('/api/retrieve', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ num_messages_to_fetch: numMessagesToFetch })  // Pass the number of messages to fetch as a parameter
  });
  const data = await response.json();
  const recentMessages = data.recent_messages;
  recentMessages.forEach(message => {
    appendMessage(message.content, message.role === 'user');
  });
});



function loadInitialConversationHistory() {
  fetch('/api/initial_conversation_history')
    .then(response => response.json())
    .then(data => {
      console.log('Initial conversation history:', data.initial_conversation_history); // Add this line
      let isUser = false;
      let messageText = '';

      const lines = data.initial_conversation_history.split("\n");
      lines.forEach(line => {
        if (line.startsWith("User: ")) {
          if (messageText) {
            appendMessage(messageText, isUser);
            messageText = '';
          }
          isUser = true;
          messageText = line.replace("User: ", "");
        } else if (line.startsWith("AI: ")) {
          if (messageText) {
            appendMessage(messageText, isUser);
            messageText = '';
          }
          isUser = false;
          messageText = line.replace("AI: ", "");
        } else if (!line.startsWith("Timestamp: ")) {
          messageText += '\n' + line;
        }
      });

      if (messageText) {
        appendMessage(messageText, isUser);
      }
    })
    .catch(error => {
      console.error('Error fetching initial conversation history:', error); // Add this line
    });
}

loadInitialConversationHistory();

function copyToClipboard(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.executeCommand('copy');
  document.body.removeChild(textarea);
}


function formatChatbotOutput(output) {
  const codeRegex = /''(<([^>]+)>)/g;
  const matches = [...output.matchAll(codeRegex)];

  if (matches.length > 0) {
    return output.replace(codeRegex, (match, code) => {
      return `<code-block>${code}</code-block>`;
    });
  } else {
    return output;
  }
}
