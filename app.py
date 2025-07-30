#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ✅ Step 2: Imports
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import re
import streamlit as st
import openai


# In[ ]:


openrouter_api_key = "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"  # paste your key here securely


# In[ ]:


def search_recipe_url(query):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=5)]
    for r in results:
        if "recipe" in r['title'].lower():
            return r['href']
    return None


def basic_scrape_recipe(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find("title").text.strip()

        # Try to extract ingredients/instructions (very basic, site-dependent)
        ingredients = [li.get_text().strip() for li in soup.select('li') if "ingredient" in li.get("class", [])]
        instructions = [p.get_text().strip() for p in soup.select('p') if len(p.get_text()) > 40]

        return {
            "title": title,
            "ingredients": ingredients[:10],
            "instructions": instructions[:10],
            "source": url
        }

    except Exception as e:
        return {"error": str(e)}


import requests

def generate_recipe_with_llm(query, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful cooking assistant."},
            {"role": "user", "content": f"Generate a full recipe for: {query}. Include: Title, Ingredients, and Step-by-step Instructions."}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"❌ API error {response.status_code}: {response.text}"


def chefbot(query, api_key):
    print(f"🍳 Looking for recipe: {query}\n")

    url = search_recipe_url(f"{query} site:allrecipes.com")
    if url:
        print(f"🔗 Found URL: {url}")
        data = basic_scrape_recipe(url)
        if data.get("ingredients") and data.get("instructions"):
            return f"🍽️ **{data['title']}**\n\n🥄 **Ingredients:**\n" +                    "\n".join(f"- {i}" for i in data['ingredients']) +                    "\n\n🔥 **Instructions:**\n" +                    "\n".join(f"{idx+1}. {step}" for idx, step in enumerate(data['instructions'])) +                    f"\n\n🔗 Source: {data['source']}"
        else:
            print("⚠️ Scrape failed. Using LLM instead.")
    
    # If no URL or scrape fails
    return generate_recipe_with_llm(query, api_key)


# 🎯 Streamlit App UI
# ---------------------------
st.set_page_config(page_title="ChefBot 🍽️", layout="centered")
st.title("👨‍🍳 ChefBot")
st.write("Ask me for any recipe, and I’ll fetch or generate it!")

#api_key = st.text_input("🔑 Enter your OpenRouter API key", type="password")
api_key = openrouter_api_key
query = st.text_input("📝 Enter a dish or recipe name", placeholder="e.g., Chicken Biryani")

if st.button("🍽️ Get Recipe") and query and api_key:
    with st.spinner("Cooking up your recipe... 🍳"):
        try:
            result = chefbot(query, api_key)
            st.markdown(result)
        except Exception as e:
            st.error(f"Error: {e}")


# In[ ]:





# In[ ]:



#openrouter_api_key = "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"  # paste your key here securely
#query = "how to make biryani"   

#fattoush salad
#mutabal
#three beans salad
# ceaser salad
# baba ganoush
# etc etc.

#output = chefbot(query, openrouter_api_key)
#print(output)




#openrouter_api_key = "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"  # paste your key here securely
#query = "how to make baba ganoush"

#output = chefbot(query, openrouter_api_key)
#print(output)


# In[ ]:





# In[ ]:




