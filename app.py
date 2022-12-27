# Package imports
import os
import json
import openai
import random
import pprint
import requests
# import lob_python
# from lob_python.exceptions import ApiException
# from lob_python.model.postcard_editable import PostcardEditable
# from lob_python.model.address_editable import AddressEditable
# from lob_python.model.merge_variables import MergeVariables
# from lob_python.model.country_extended import CountryExtended
# from lob_python.api.postcards_api import PostcardsApi
from dotenv import load_dotenv
from flask import Flask, request, render_template

# Local imports
import scraper
from freq_add import freq_add_summarizer
from tf_idf import tf_idf_summarizer

load_dotenv()
username = os.getenv('LOB_API_KEY')
# configuration = lob_python.Configuration(
#     username = os.getenv('LOB_API_KEY')
# )

MAX_TOKEN_COUNTS = 4096

# Inspiration for the template website came from the following sources:
# https://python.plainenglish.io/sentiment-analysis-flask-web-app-using-python-and-nltkintroduction-a45f893fb724
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def index_post():
    url = request.form["url"]
    passage = scraper.parse_website(url, "dyn")
    freq_summary = freq_add_summarizer(passage)
    tf_summary = tf_idf_summarizer(passage)
    sentences = passage.split('.')
    values = {}
    num_openai_summ = 3
    # Split into groups of 100 sentences in order to fit model token constraints
    openai_prompts = [" ".join(sentences[i:i+100]) for i in range(0, len(sentences), 100)]
    for i, prompt in enumerate(openai_prompts):
        openai_prompt = prompt + "\n\nTl;dr"
        openai_summary = openai.Completion.create(
            model="text-davinci-002",
            prompt=openai_prompt,
            n=num_openai_summ,
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        values[f"openai_summ_group_{i}"] = [summ["text"] for summ in openai_summary["choices"]]
    openai_summaries = [value for key, value in values.items() if 'openai' in key.lower()]
    lob_front_summ = ""
    lob_back_summ = ""
    idx_3, idx_4 = random.sample(range(0, num_openai_summ), 2)
    if len(openai_summaries) > 1:
        idx_1, idx_2 = random.sample(range(0, len(openai_summaries)), 2)
        lob_front_summ = values[f"openai_summ_group_{idx_1}"][idx_3]
        lob_back_summ = values[f"openai_summ_group_{idx_2}"][idx_4]
    else:
        lob_front_summ = values[f"openai_summ_group_0"][idx_3]
        lob_back_summ = values[f"openai_summ_group_0"][idx_4]
    lob_front_html = "<html style='padding: 1in; font-size: 15;'>{{lob_front_summ}}</html>"
    lob_back_html = "<html style='padding: 1in; font-size: 8;'>{{lob_back_summ}}</html>"
    payload = {
        "description": "short_form_api postcard",
        "front": lob_front_html,
        "back": lob_back_html,
        "to": {
            "name": "Josh Nkoy",
            "address_line1": "210 King Street",
            "address_city": "San Francisco",
            "address_state": "CA",
            "address_zip": "94107",
            "address_country": "US"
        },
        "from": {
            "name": "Telecom Co.",
            "address_line1": "210 King Street",
            "address_city": "San Francisco",
            "address_state": "CA",
            "address_zip": "94107",
            "address_country": "US"
        },
        "merge_variables": {
            "lob_front_summ": lob_front_summ,
            "lob_back_summ": lob_back_summ
        }
    }
    '''
    POST call to Lob API to create postcard
    Originally tried to use Lob Python SDK v5, but failed compared to v4 SDK
    due to lack of JSON response return values
    '''
    headers = {
        'Authorization': 'Basic dGVzdF80MWZlZjZjMGVkNmRiYWU0NzhiZTBkZTEyNDdkNGNhNmZjMTo=',
        'Content-Type': 'application/json'
    }
    postcard = requests.post(
        url = "https://api.lob.com/v1/postcards",
        headers = headers,
        json = json.dumps(payload),
        auth = (username, '')
    ).json()
    postcard_link = postcard["url"]
    print(postcard_link)
    return render_template(
        'index.html',
        passage = passage,
        freq_summary = freq_summary,
        tf_summary = tf_summary,
        openai_summaries=openai_summaries,
        postcard_link = postcard_link
    )

@app.route("/test-parse", methods=["POST"])
def test_parse():
    url = request.form["url"]
    dyn = request.form["dyn"]
    return scraper.parse_website(url, dyn)

@app.route("/summarize", methods=["POST"])
def summarize():
    url = request.form["url"]
    dyn = request.form["dyn"]
    num_openai_summ = int(request.form["summaries"])
    text = scraper.parse_website(url, dyn)
    freq_summary = freq_add_summarizer(text)
    tf_summary = tf_idf_summarizer(text)
    values = {}
    values['passage'] = text
    values['freq_summ'] = freq_summary
    values['tf_idf_summ'] = tf_summary
    sentences = text.split('.')
    # Split into groups of 100 sentences in order to fit model token constraints
    openai_prompts = [" ".join(sentences[i:i+100]) for i in range(0, len(sentences), 100)]
    for i, prompt in enumerate(openai_prompts):
        openai_prompt = prompt + "\n\nTl;dr"
        openai_summary = openai.Completion.create(
            model="text-davinci-002",
            prompt=openai_prompt,
            n=num_openai_summ,
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        values[f"openai_summ_group_{i}"] = [summ["text"] for summ in openai_summary["choices"]]
    openai_summaries = [value for key, value in values.items() if 'openai' in key.lower()]
    lob_front_summ = ""
    lob_back_summ = ""
    idx_3, idx_4 = random.sample(range(0, num_openai_summ), 2)
    if len(openai_summaries) > 1:
        idx_1, idx_2 = random.sample(range(0, len(openai_summaries)), 2)
        lob_front_summ = values[f"openai_summ_group_{idx_1}"][idx_3]
        lob_back_summ = values[f"openai_summ_group_{idx_2}"][idx_4]
    else:
        lob_front_summ = values[f"openai_summ_group_0"][idx_3]
        lob_back_summ = values[f"openai_summ_group_0"][idx_4]
    lob_front_html = "<html style='padding: 1in; font-size: 15;'>{{lob_front_summ}}</html>"
    lob_back_html = "<html style='padding: 1in; font-size: 8;'>{{lob_back_summ}}</html>"
    payload = {
        "description": "short_form_api postcard",
        "front": lob_front_html,
        "back": lob_back_html,
        "to": {
            "name": "Josh Nkoy",
            "address_line1": "210 King Street",
            "address_city": "San Francisco",
            "address_state": "CA",
            "address_zip": "94107",
            "address_country": "US"
        },
        "from": {
            "name": "Telecom Co.",
            "address_line1": "210 King Street",
            "address_city": "San Francisco",
            "address_state": "CA",
            "address_zip": "94107",
            "address_country": "US"
        },
        "merge_variables": {
            "lob_front_summ": lob_front_summ,
            "lob_back_summ": lob_back_summ
        }
    }
    '''
    POST call to Lob API to create postcard
    Originally tried to use Lob Python SDK v5, but failed compared to v4 SDK
    due to lack of JSON response return values
    '''
    headers = {
        'Authorization': 'Basic dGVzdF80MWZlZjZjMGVkNmRiYWU0NzhiZTBkZTEyNDdkNGNhNmZjMTo=',
        'Content-Type': 'application/json'
    }
    values["postcard"] = requests.post(
        url = "https://api.lob.com/v1/postcards",
        headers = headers,
        json = json.dumps(payload),
        auth = (username, '')
    ).json()
    return values

    # postcard_config = PostcardEditable(
    #     description = "short_form_api postcard",
    #     front = lob_front_html,
    #     back = lob_back_html,
    #     to = AddressEditable(
    #         name = "Josh Nkoy",
    #         address_line1 = "210 King Street",
    #         address_city = "San Francisco",
    #         address_state = "CA",
    #         address_zip = "94107"
    #     ),
    #     _from = AddressEditable(
    #         name = "Telecom Co.",
    #         address_line1 = "210 King Street",
    #         address_city = "San Francisco",
    #         address_state = "CA",
    #         address_zip = "94107",
    #         address_country = CountryExtended("US")
    #     ),
    #     merge_variables = MergeVariables(
    #         lob_front_summ = lob_front_summ,
    #         lob_back_summ = lob_back_summ
    #     )
    # )
    # with lob_python.ApiClient(configuration) as api_client:
    #     api = PostcardsApi(api_client)
    # try:
    #     created_postcard = api.create(postcard_config)
    #     # For some reason the response is still a postcard object so I'll make it JSON
    #     values["postcard"] = make_postcard_json(created_postcard)
    #     # values["postcard"] = json.dumps(created_postcard)
    #     # json_values = json.dumps(values)
    #     deleted_postcard = api.cancel(created_postcard["id"])
    #     print(deleted_postcard)
    #     return values
    # except ApiException as e:
    #     print(e)

# def make_postcard_json(response):
#     postcard_data = response["_data_store"]
#     postcard_data["to"] = postcard_data["to"]["_data_store"]
#     postcard_data["_from"] = postcard_data["_from"]["_data_store"]
#     postcard_data["metadata"] = postcard_data["metadata"]["_data_store"]
#     postcard_data["to"]["metadata"] = postcard_data["to"]["metadata"]["_data_store"]
#     postcard_data["_from"]["metadata"] = postcard_data["_from"]["metadata"]["_data_store"]
#     postcard_data["merge_variables"] = postcard_data["merge_variables"]["_data_store"]
#     postcard_data["mail_type"] = postcard_data["mail_type"]["_data_store"]["value"]
#     postcard_data["size"] = postcard_data["size"]["_data_store"]["value"]
#     pprint.pprint(postcard_data)
#     print(type(postcard_data))
#     return postcard_data

if __name__ == "__main__":
    app.run(debug=True)