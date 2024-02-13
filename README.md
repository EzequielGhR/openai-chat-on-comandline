# openai-chat-on-comandline

- Create a folder on your home directory called ".creds"
- Inside create a file called "credentials.sh" with `export OPENAI_KEY="your-openai-api-key"`
- run `source credentials.sh`
- Move project to a hidden folder on your home like ".custom-scripts" and move into that folder `cd ~/.custom-scripts`
- Create a virtual env with python `python -m venv .venv` and activate it `source .venv/bin/activate`
- Install required libraries onto the venv `pip install -r requirements.txt`
- deactivate the venv `deactivate`
- Add sourcing to .bashrc:
    - Open .bashrc for example with nano: `nano ~/.bashrc`
    - At the end add the line `source ~/.custom-scripts/gpt-utils.sh`
    - Save and close (Ctrl+S, Ctrl+X on nano)
- Now reload your terminal and you should be able to use the commands:
    - `gpt`: Use `gpt help` to see use cases
    - `gpt-latest`: Use `gpt-latest help` to see use cases
    - `gpt-from-file`: Use `gpt-from-file help` to see use cases