import os
import cohere
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
cohereAPIKey = os.environ["CO_API_KEY"]
co = cohere.Client(cohereAPIKey)

# seems like the connector can return the same url inside "documents" more than once
# i believe its bc one url has many "document snippets" that the connector thinks will be useful to feed the model
# this function tackles this by filtering out duplicate urls
def handleDocumentURLs(documents):
    documentURLs = []
    for document in documents:
        if document['url'] not in documentURLs:
            documentURLs.append(document['url'])

    return documentURLs

def handleChatAPIResponse(chatAPIResponse):
    text = chatAPIResponse.text
    documents = chatAPIResponse.documents

    return text, handleDocumentURLs(documents)

def handleWarning(prompt):
    if prompt == "":
        return gr.Warning("input empty: please enter an input.")
    
def makeChatPOSTRequest(model, prompt, temperature):
    chatAPIResponse = co.chat (
        model = model,
        message = prompt,
        temperature = temperature,
        connectors = [
            {"id": "web-search",
            #"options": {}
            }
        ],
    )

    return chatAPIResponse

def chatPOSTRequest(prompt):
    handleWarning(prompt)
    chatAPIResponse = makeChatPOSTRequest("command", prompt, 0.5)

    return handleChatAPIResponse(chatAPIResponse)


theme = gr.themes.Monochrome(
    text_size=gr.themes.sizes.text_lg, 
    spacing_size=gr.themes.sizes.spacing_lg, 
    radius_size=gr.themes.sizes.radius_md,
    font=[gr.themes.GoogleFont("Inconsolata"), gr.themes.GoogleFont("Source Sans Pro"), "Arial"]
    ).set(
         button_primary_background_fill="black"
    )

css = """
    #examples-list {color: gray}
    #markdown-title h1 {font-size: 35px}
    #markdown-title h1 {border-bottom: 1px solid black}
    #markdown-title h1  {display: inline-block}
    #markdown-title h1  {margin-top: 5px}
    #markdown-paragraph p  {margin-top: -38px}
    #resources-textbox textarea {font-style: italic}
    #search-button {width: 400px}
    #search-button {margin: 0 auto}
    #search-button {background-color: rgb(23, 23, 23)}
"""

with gr.Blocks(theme=theme, title = "AI Search", css=css) as demo:
    gr.Markdown(value="# AI powered search with Cohere API 🚀", elem_id="markdown-title") 
    gr.Markdown(value="AI Topics: Large Language Models(LLM), Retrieval Augmented Generation(RAG)", elem_id="markdown-paragraph") 
    inp = gr.Textbox(label="What do you want to ask?")
    gr.Examples([["What is Cohere API?"], ["Who won the 1999 NBA Finals?"]], inp, elem_id="examples-list")
    btn = gr.Button("Search 🔎", elem_id="search-button")
    out1 = gr.Textbox(label="Response")
    out2 = gr.Textbox(label="Resources", elem_id="resources-textbox")
    btn.click(fn = chatPOSTRequest, inputs = inp, outputs = [out1, out2])
    
demo.launch(favicon_path="https://cdn3.iconfinder.com/data/icons/feather-5/24/search-512.png")
