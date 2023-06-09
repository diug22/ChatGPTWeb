import os
import csv
import json
import time
import secrets
import datetime
import webbrowser
import tornado.web
import tornado.websocket
import tornado.ioloop
import openai

openai.api_key = os.environ.get('OPEN_AI_API_KEY')

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open("contexto.txt", "r", encoding="utf-8") as f:
            self.render("templates/index.html", contexto=f.read())

class ChatHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def open(self):
        self.connections.add(self)
        self.init_conversation()

    def init_conversation(self):
        self.messages, self.id = [], secrets.token_hex(10)
        self.context = {"Hora": [], "Message": [], "Role": [], "Id": []}
        with open("contexto.txt", "r", encoding="utf-8") as f:
            self.save_message('system', f.read())

    def chat_gpt(self):
        try: return openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages).choices[0].message.content
        except: time.sleep(2); self.chat_gpt()

    def save_message(self, role, message):
        current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        self.context['Hora'].append(current_time)
        self.context['Message'].append(message)
        self.context['Role'].append(role)
        self.context['Id'].append(self.id)
        self.messages.append({"role": role, "content": message})

    def on_message(self, message):
        message = json.loads(message)
        if message['from'] == "user": self.user_message(message)
        elif message['from'] == "system": self.context_message(message)

    def user_message(self, message):
        self.save_message('user', str(message['message']))
        for conn in self.connections: conn.write_message(message)
        response = self.chat_gpt()
        for conn in self.connections: conn.write_message(json.dumps({"message": response, "from": "assistant"}))
        self.save_message('assistant', response)
        self.finish_process()

    def context_message(self, message):
        with open("contexto.txt", "w", encoding="utf-8") as f: f.write(message['message'])
        self.finish_process()
        self.init_conversation()

    def finish_process(self):
        with open('data/history.csv', mode='a', newline='', encoding="utf-8") as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            for i in range(len(self.context["Message"])):
                escritor_csv.writerow([self.context[k][i] for k in ["Hora", "Message", "Role", "Id"]])
        self.context = {"Hora": [], "Message": [], "Role": [], "Id": []}

    def on_close(self): self.connections.remove(self)


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/chat", ChatHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": tornado.web.StaticFileHandler.get_absolute_path(__file__, "static")}),
    ], debug=True, static_path='static')
    app.listen(8888)
    webbrowser.open('http://localhost:8888')
    tornado.ioloop.IOLoop.current().start() 