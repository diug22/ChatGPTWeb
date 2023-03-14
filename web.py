import tornado.web
import tornado.websocket
import tornado.ioloop
import json
import pandas as pd
import secrets
import datetime
import os
import csv
from tornado.web import RequestHandler
import openai
import webbrowser

openai.api_key = os.environ.get('OPEN_AI_API_KEY')



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open("contexto.txt", "r", encoding="utf-8") as f:
            contexto = f.read()
        self.render("templates/index.html", contexto=contexto)

class ChatHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def open(self):
        ChatHandler.connections.add(self)
        self.init_conversation()
        
    def init_conversation(self):
        self.messages = []
        self.context = {
            "Hora" : [],
            "Message": [],
            "Role": [],
            "Id": []
        }
        self.id = secrets.token_hex(10)
        self.context_file()

    def context_file(self):
        contexto_archivo = open("contexto.txt", "r", encoding="utf-8")
        contexto = contexto_archivo.read()
        self.save_message('system',contexto)

    def chat_gpt(self):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        response_text = response.choices[0].message.content
        return response_text
    
    def save_message(self,role,message):
        self.context['Hora'].append(datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
        self.context['Message'].append(message)
        self.context['Role'].append(role)
        self.context['Id'].append(self.id)
        self.messages.append({"role": role, "content": message})


    def on_message(self, message):
        message = json.loads(message)
        if message['from'] == "user": 
            self.user_message(message)
        if message['from'] == "system": 
            self.context_message(message)
       
       
    def user_message(self,message):
        self.save_message('user',str(message['message']))
        for conn in ChatHandler.connections:
            conn.write_message(
               message
            )
        response = self.chat_gpt()
        for conn in ChatHandler.connections:
            conn.write_message(
               json.dumps({ "message": response, "from": "assistant" })
            )
        self.save_message('assistant',response)
        self.finish_process()
        
    def context_message(self,message):
        with open("contexto.txt", "w", encoding="utf-8") as f:
            f.write(message['message'])
        self.finish_process()
        self.init_conversation()

    def finish_process(self):
       
        archivo_csv = open('data/history.csv', mode='a', newline='', encoding="utf-8")

        escritor_csv = csv.writer(archivo_csv)
        for i in range(0,len(self.context["Message"])):
            escritor_csv.writerow([self.context["Hora"][i],
                            self.context["Message"][i],
                            self.context["Role"][i],
                            self.context["Id"][i]])
        archivo_csv.close()
        self.context = {
            "Hora" : [],
            "Message": [],
            "Role": [],
            "Id": []
        }

    def on_close(self):
        ChatHandler.connections.remove(self)


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/chat", ChatHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": tornado.web.StaticFileHandler.get_absolute_path(__file__, "static")}),
    ], debug=True, static_path='static')
    app.listen(8888)
    webbrowser.open('http://localhost:8888')
    tornado.ioloop.IOLoop.current().start() 