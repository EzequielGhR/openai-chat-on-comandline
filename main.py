import os
import json
import openai
import logging

from argparse import ArgumentParser
from datetime import datetime as dt


logging.getLogger().setLevel(logging.WARNING)
openai.api_key = os.getenv("OPENAI_KEY")

#Set VERBOSE to True for debugging logs
VERBOSE = False
MODEL = "gpt-3.5-turbo-1106"
with open("pricing/matcher.json", "r") as f:
    price_matcher = json.loads(f.read())[MODEL]
    INPUT_PER_TOKEN = price_matcher["input"]
    OUTPUT_PER_TOKEN = price_matcher["output"]


if VERBOSE:
    logging.getLogger().setLevel(logging.INFO)


def _get_latest_filename() -> str:
    return max(
        [dt.strptime(file_.rsplit(".json")[0], fmt:="%Y%m%dT%H%M%S%f")
            for file_ in os.listdir() if file_.endswith(".json")]
    ).strftime(fmt)+".json"


class OpenaiChat():
    def __init__(self, start_message:str="", purpose:str="") -> None:
        purpose = purpose or "general purpose"
        self._price = 0
        self._messages = [{"role": "assistant", "content": purpose}]
        if start_message:
            self._messages.append({"role": "user", "content": start_message})
    
    @property
    def messages(self):
        return self._messages
    
    @property
    def price(self):
        return self._price
    
    def chat(self, loaded_filename:str="") -> None:
        for message in self.messages:
            print(f"{message['role']}_: {message['content']}")

        while True:
            logging.info("Sending GPT request")
            response = openai.chat.completions.create(
                model=MODEL,
                messages = self.messages
            )

            #add price for this interaction
            self._price += response.usage.prompt_tokens * INPUT_PER_TOKEN
            self._price += response.usage.completion_tokens * OUTPUT_PER_TOKEN
            logging.info("Current chat price: %s" % self.price)

            #append first context message to messages
            chat_message = response.choices[0].message.content
            self._messages.append({"role": "assistant", "content": chat_message})
            print(f"assistant_: {chat_message}")

            #Ask and parse user input
            message = input("user_: ")
            if message.lower() in ("quit", "exit"):
                logging.info("quitting ephimeral chat")
                break

            if message.lower() == "save":
                #update latest chat if oppened and saved from an older one
                delete_old_json = False
                if loaded_filename == _get_latest_filename():
                    filename = loaded_filename
                else:
                    filename = dt.utcnow().strftime('%Y%m%dT%H%M%S%f')+".json"
                    delete_old_json = True

                logging.info("saving chat as %s" % filename)
                with open(filename, "w") as f:
                    f.write(json.dumps(self.messages, indent=4))
                    
                if delete_old_json and loaded_filename:
                    logging.info("deleting old json: %s" % loaded_filename)
                    os.remove(loaded_filename)
                break

            self._messages.append({"role": "user", "content": message})
        
    def load(self, message:str, **kwargs) -> None:
        latest = kwargs.get("latest") or False

        #check for keyword arguments
        try:
            if kwargs.get("filename"):
                logging.info("filename provided, ignoring all other keyword arguments.")
                with open(filename:=kwargs["filename"], "r") as f:
                    self._messages = json.loads(f.read())

            elif latest:
                filename = _get_latest_filename()
                logging.info("loading latest chat file \"%s\"" % filename)
                with open(filename, "r") as f:
                    self._messages = json.loads(f.read())
            
            self._messages.append({"role": "user", "content": message})
            self.chat(loaded_filename=filename)

        except FileNotFoundError as e:
            logging.warning("File \"%s\" not found. Are you sure the name is correct?" % filename)
            raise e
        
        except ValueError as e:
            logging.warning("No conversations found")
            raise e
        
        except Exception as e:
            logging.warning("Exception raised %s" % str(e))
            raise e

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
    
    print(f"Total interaction price: {gpt.price}")
