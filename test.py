import json
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

tavily_search = TavilySearch(max_results=3)
search_docs = tavily_search.invoke("What is the most searched item in the FAQ from Apple?")
print(type(search_docs))

json_string_formatado = json.dumps(search_docs, indent=2, ensure_ascii=False)
print(json_string_formatado)

print(search_docs["results"])

results = search_docs["results"]

for result in results:
    print(result["url"])

res = "\n".join([f"{r["content"]}" for r in search_docs["results"]])
print(res)