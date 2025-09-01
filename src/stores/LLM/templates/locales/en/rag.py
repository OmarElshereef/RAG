from string import Template

### rag prompts ###

system_prompt = Template(
    "\n".join(
        [
            "you are an assistant to generate a response for the user",
            "you will be provided with a user's query and a list of documents related to the query",
            "you will have to generate a response based on the documents provided only",
            "Ignore the documents that are not relevant to the query",
            "You can aplogoize if you don't know the answer from the documents",
            "you have to generate the response in the same language as the query",
            "be polite and professional in your response",
            "be precise and concise in your response, avoid unnecessary information",
        ]
    )
)

### document prompts ###

document_prompt = Template(
    "\n".join(
        [
            "##Document No:$doc_num",
            "### Content:$content",
        ]
    )
)

footer_prompt = Template(
    "\n".join(
        [
            "Based only on the above documents, generate a response for the user",
            "##Answer:",
        ]
    )
)
