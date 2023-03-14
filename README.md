# ChatGPT en Web
Uso de la api de ChatGPT en el navegador con estilo de chat.

## Prerequisitos
`pip install -r requirements.txt`  

Añadir la API de OpenAI.

### Windows
`setx OPEN_AI_API_KEY {API_KEY_OPEN_AI}`  

### Linux/Mac
`export OPEN_AI_API_KEY {API_KEY_OPEN_AI}`  


## Lanzamiento
`python web.py` 

## Uso
Se abrira una nueva pestaña donde se podra chatear con la API de ChatGPT, además es posible modificar el contexto de la misma. Reiniciando la conversación. 

## Archivos relevantes  

### Contexto.txt
Contendra el contexto al inicializar la conversación, siempre que se haga un cambio este se reflejara en el fichero.

### History.csv
Almacenamiento de las diferentes conversaciones que se estan teniendo.
Formato: 
- **Hora**: Hora del mensaje
- **Message** : Mensaje en texto
- **Role** : Quien ha mandado el mensaje. Puede ser User,Assitant o System.
- **Id** : Identificador unico de la conversación


## Ejemplo de comportamiento
![image](https://user-images.githubusercontent.com/25454965/224962256-c911868e-bdb0-41d8-9712-52cd75618aa4.png)
