import json
import logging
import requests

from bs4 import BeautifulSoup


def clean_td(td:BeautifulSoup) -> str|float:
    """
    Clean a table td text, returns a float of the prices per token, or just the text on other cases
    """
    td = td.text.rsplit("\xc2", 1)[0]
    if "$" not in td:
        return td
    return float(td.replace("$", ""))/1000

def main() -> None:
    """
    Scrapes openai/pricing page and saves a json with pricing data per model
    """
    response = requests.get("https://openai.com/pricing")
    soup = BeautifulSoup(response.text, "html.parser")

    model_ids = ["gpt-3-5-turbo", "gpt-4", "gpt-4-turbo", "older-models"]
    records = []
    for id_ in model_ids:
        #get array of pricing table rows
        table_array = [list(map(clean_td, row.findAll("td")))
            for row in soup.select("#%s table:nth-child(1) tr" % id_)]
        headers = table_array[0]
        records += [dict(zip(headers, row)) for row in table_array[1:]]

    with open("pricing/matcher.json", "w") as f:
        f.write(json.dumps({
            rec["Model"]: {
                u"input": rec["Input"],
                u"output": rec["Output"]
            } for rec in records
        }, indent=4))

if __name__ == "__main__":
    main()