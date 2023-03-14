var ws = new WebSocket("ws://localhost:8888/chat");

ws.onopen = function(evt) {
  console.log("WebSocket connection established.");
};

function sendMessage() {
  var message = document.getElementById("message_input").value;
  console.log(message)

  if (message.length === 0) {
    return false;
  }
  ws.send(JSON.stringify({ message: message, from: "user" }));
  document.getElementById("message_input").value = "";
  return false;
}

function sendContext() {
  var message = document.getElementById("contexto").value;
  console.log(message)
  ws.send(JSON.stringify({ message: message, from: "system" }));
  location.reload();
  return false;
  return false
}

ws.onmessage = function(evt) {
  var message = JSON.parse(evt.data);
  var node = document.createElement("LI");
  node.classList.add("mb-2");
  node.classList.add(message.from === "user" ? "from-me" : "from-them");

  // Si el mensaje contiene código, lo resaltamos y le agregamos un botón para copiarlo
  if (message.message.match(/```(.|\n)*```/g)) {
    // Resaltar el código con Highlight.js
    var code = message.message.replace(/```(.|\n)*```/g, function(match) {
      return '<pre><code class="python">' + match.substring(3, match.length - 3) + '</code></pre>';
    });
    var div = document.createElement("div");
    div.innerHTML = code;
    div.classList.add("code-container");

    // Agregar botón para copiar el código
    var copyButton = document.createElement("button");
    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
    copyButton.classList.add("copy-button");
    copyButton.addEventListener("click", function() {
      var codeElement = this.parentNode.querySelector("code");
      var code = codeElement.innerText;
      navigator.clipboard.writeText(code);
    });
    div.appendChild(copyButton);

    node.appendChild(div);
  } else {
    var textnode = document.createTextNode(message.message);
    node.appendChild(textnode);
  }

  document.getElementById("lista_messages").appendChild(node);
  document.getElementById("message_input").focus();
  // Resaltar el código con Highlight.js
  hljs.highlightAll();
};


document.getElementById("button_send").onclick = sendMessage;

document.getElementById("message_input").onkeypress = function(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    sendMessage();
  }
};

document.getElementById("message_input").focus();

document.getElementById("context-form").onsubmit = sendContext;

var recognition = new window.webkitSpeechRecognition();

recognition.onresult = function(event) {
  var message = event.results[0][0].transcript;
  document.getElementById("message_input").value = message;
  sendMessage();
};

var buttonRecord = document.getElementById("button_record");

buttonRecord.onclick = function() {
  if (recognition.recording) {
    recognition.stop();
  } else {
    recognition.start();
  }
};

recognition.onstart = function() {
  buttonRecord.classList.add("btn-record-recording");
};

recognition.onend = function() {
  buttonRecord.classList.remove("btn-record-recording");
};