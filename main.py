import os
import json
import openai
import logging

from argparse import ArgumentParser
from datetime import datetime as dt


logging.getLogger().setLevel(logging.WARNING)
openai.api_key = os.getenv("OPENAI_KEY")

class OpenaiChat():
    def __init__(self, start_message:str="", purpose:str="") -> None:
        purpose = purpose or "general purpose"
        self._messages = [{"role": "assistant", "content": purpose}]
        if start_message:
            self._messages.append({"role": "user", "content": start_message})
    
    @property
    def messages(self):
        return self._messages
    
    def chat(self, loaded_filename:str="") -> None:
        for message in self.messages:
            print(f"{message['role']}_: {message['content']}")

        while True:
            logging.info("Sending GPT request")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages = self.messages
            )

            chat_message = response.choices[0].message.content
            self._messages.append({"role": "assistant", "content": chat_message})
            print(f"assistant_: {chat_message}")

            message = input("user_: ")
            if message.lower() in ("quit", "exit"):
                logging.info("quitting ephimeral chat")
                break

            if message.lower() == "save":
                filename = loaded_filename or dt.utcnow().strftime("%Y%m%dT%H%M%S%f") + ".json"
                logging.info("saving chat as %s" % filename)
                with open(filename, "w") as f:
                    f.write(json.dumps(self.messages, indent=4))
                break

            self._messages.append({"role": "user", "content": message})
        
    def load(self, message:str, **kwargs) -> None:
        latest = kwargs.get("latest") or False

        if kwargs.get("filename"):
            logging.info("filename provided, ignoring all other keyword arguments.")
            with open(filename:=kwargs["filename"], "r") as f:
                self._messages = json.loads(f.read())
        
        elif latest:
            filename = max(
                [dt.strptime(file_.rsplit(".json", 1)[0], fmt:="%Y%m%dT%H%M%S%f")
                    for file_ in os.listdir() if file_.endswith(".json")]
            ).strftime(fmt) + ".json"
            logging.info("loading latest chat file \"%s\"" % filename)
            with open(filename, "r") as f:
                self._messages = json.loads(f.read())
        
        self._messages.append({"role": "user", "content": message})
        self.chat(loaded_filename=filename)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--start-message", type=str)
    parser.add_argument("--purpose", type=str)
    parser.add_argument("--load-latest", type=str)
    parser.add_argument("--load-from-file", type=str)

    args = parser.parse_args()

    gpt = OpenaiChat(args.start_message, args.purpose)

    if args.load_latest or args.load_from_file:
        gpt.load(args.start_message, filename=args.load_from_file, latest=args.load_latest)
    else:
        gpt.chat()
