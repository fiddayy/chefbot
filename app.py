{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "ac162258-c063-44c5-8f73-dac4538c0952",
   "metadata": {},
   "outputs": [],
   "source": [
    "# ✅ Step 1: Install Required Packages (only run once)\n",
    "#!pip install ddgs beautifulsoup4 requests\n",
    "\n",
    "# ✅ Step 2: Imports\n",
    "from ddgs import DDGS\n",
    "import requests\n",
    "from bs4 import BeautifulSoup\n",
    "import re\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "d5988f1f-1404-4ab2-8049-6cb5322919e5",
   "metadata": {},
   "outputs": [],
   "source": [
    "# app.py\n",
    "import streamlit as st\n",
    "import requests\n",
    "from bs4 import BeautifulSoup\n",
    "#from duckduckgo_search import DDGS\n",
    "import openai\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "25684405-54c8-4c57-9930-ee520cb09bab",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "af7f99ba-8f0f-45fe-b0e9-c877835efdad",
   "metadata": {},
   "outputs": [],
   "source": [
    "openrouter_api_key = \"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\"  # paste your key here securely\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "7a717e04-9248-42a8-9aed-88747d0de138",
   "metadata": {},
   "outputs": [],
   "source": [
    "def search_recipe_url(query):\n",
    "    with DDGS() as ddgs:\n",
    "        results = [r for r in ddgs.text(query, max_results=5)]\n",
    "    for r in results:\n",
    "        if \"recipe\" in r['title'].lower():\n",
    "            return r['href']\n",
    "    return None\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "acdc1a78-544f-4d35-8afa-2652510eedf4",
   "metadata": {},
   "outputs": [],
   "source": [
    "def basic_scrape_recipe(url):\n",
    "    try:\n",
    "        res = requests.get(url, headers={\"User-Agent\": \"Mozilla/5.0\"})\n",
    "        soup = BeautifulSoup(res.text, 'html.parser')\n",
    "\n",
    "        title = soup.find(\"title\").text.strip()\n",
    "\n",
    "        # Try to extract ingredients/instructions (very basic, site-dependent)\n",
    "        ingredients = [li.get_text().strip() for li in soup.select('li') if \"ingredient\" in li.get(\"class\", [])]\n",
    "        instructions = [p.get_text().strip() for p in soup.select('p') if len(p.get_text()) > 40]\n",
    "\n",
    "        return {\n",
    "            \"title\": title,\n",
    "            \"ingredients\": ingredients[:10],\n",
    "            \"instructions\": instructions[:10],\n",
    "            \"source\": url\n",
    "        }\n",
    "\n",
    "    except Exception as e:\n",
    "        return {\"error\": str(e)}\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "72b74141-8170-48a0-be35-c52ba0b52c19",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "\n",
    "def generate_recipe_with_llm(query, api_key):\n",
    "    url = \"https://openrouter.ai/api/v1/chat/completions\"\n",
    "\n",
    "    headers = {\n",
    "        \"Authorization\": f\"Bearer {api_key}\",\n",
    "        \"Content-Type\": \"application/json\"\n",
    "    }\n",
    "\n",
    "    payload = {\n",
    "        \"model\": \"mistralai/mistral-7b-instruct\",\n",
    "        \"messages\": [\n",
    "            {\"role\": \"system\", \"content\": \"You are a helpful cooking assistant.\"},\n",
    "            {\"role\": \"user\", \"content\": f\"Generate a full recipe for: {query}. Include: Title, Ingredients, and Step-by-step Instructions.\"}\n",
    "        ]\n",
    "    }\n",
    "\n",
    "    response = requests.post(url, headers=headers, json=payload)\n",
    "    \n",
    "    if response.status_code == 200:\n",
    "        return response.json()['choices'][0]['message']['content']\n",
    "    else:\n",
    "        return f\"❌ API error {response.status_code}: {response.text}\"\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "298cfa9f-c27a-47f7-865b-9e6d9f8a03ca",
   "metadata": {},
   "outputs": [],
   "source": [
    "def chefbot(query, api_key):\n",
    "    print(f\"🍳 Looking for recipe: {query}\\n\")\n",
    "\n",
    "    url = search_recipe_url(f\"{query} site:allrecipes.com\")\n",
    "    if url:\n",
    "        print(f\"🔗 Found URL: {url}\")\n",
    "        data = basic_scrape_recipe(url)\n",
    "        if data.get(\"ingredients\") and data.get(\"instructions\"):\n",
    "            return f\"🍽️ **{data['title']}**\\n\\n🥄 **Ingredients:**\\n\" + \\\n",
    "                   \"\\n\".join(f\"- {i}\" for i in data['ingredients']) + \\\n",
    "                   \"\\n\\n🔥 **Instructions:**\\n\" + \\\n",
    "                   \"\\n\".join(f\"{idx+1}. {step}\" for idx, step in enumerate(data['instructions'])) + \\\n",
    "                   f\"\\n\\n🔗 Source: {data['source']}\"\n",
    "        else:\n",
    "            print(\"⚠️ Scrape failed. Using LLM instead.\")\n",
    "    \n",
    "    # If no URL or scrape fails\n",
    "    return generate_recipe_with_llm(query, api_key)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "e91e044b-3fa9-4568-8642-b733c05e7772",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "🍳 Looking for recipe: how to make biryani\n",
      "\n",
      "🔗 Found URL: https://www.allrecipes.com/recipe/246558/hyderabad-dum-biryani/\n",
      "⚠️ Scrape failed. Using LLM instead.\n",
      " Title: Chicken Biryani Recipe\n",
      "\n",
      "Ingredients:\n",
      "- 1 kg boneless, skinless chicken legs, cut into large pieces\n",
      "- 2 cups basmati rice\n",
      "- 2 large onions, thinly sliced\n",
      "- 6 cloves garlic, minced\n",
      "- 2-inch piece ginger, minced\n",
      "- 2 tablespoons oil\n",
      "- 2 cups yogurt\n",
      "- 2 teaspoons chili powder\n",
      "- 1 teaspoon turmeric powder\n",
      "- 1 tablespoon dried mint leaves\n",
      "- 2 teaspoons garam masala\n",
      "- 2 teaspoons ground cumin\n",
      "- 2 teaspoons ground coriander\n",
      "- Salt, to taste\n",
      "- 6 green chilies, slit lengthwise\n",
      "- 3 potatoes, peeled and quartered\n",
      "- 2 carrots, peeled and cut into rounds\n",
      "- 1 cup of water\n",
      "- 2 cups eggless raita (optional, for serving)\n",
      "- Chopped fresh cilantro, for garnish\n",
      "- Sliced almonds, for garnish\n",
      "\n",
      "Step-by-step Instructions:\n",
      "\n",
      "1. Wash and soak the basmati rice in water for 30 minutes. Drain and set aside.\n",
      "\n",
      "2. In a large bowl, combine chicken pieces with yogurt, chili powder, turmeric, dried mint leaves, garam masala, cumin, coriander, and salt. Mix well, cover, and marinate for at least 2 hours (or overnight for a more developed flavor).\n",
      "\n",
      "3. Heat oil in a large, deep pot or pressure cooker over medium heat. Add sliced onions, garlic, and ginger, and sauté until golden brown. Remove the sautéed onions and set aside.\n",
      "\n",
      "4. Add the marinated chicken pieces to the same pot, and cook until lightly browned on all sides. Remove the chicken from the pot and set aside.\n",
      "\n",
      "5. In the same pot, add potatoes, carrots, and green chilies. Cook for about 5 minutes until the vegetables start to soften.\n",
      "\n",
      "6. Add soaked rice on top of the cooked vegetables, followed by the cooked chicken, and the sautéed onions.\n",
      "\n",
      "7. Pour water into the pot, just enough to cover the rice and chicken (about 2 cups) and season with salt.\n",
      "\n",
      "8. Cover the pot and cook on low heat (or as appropriate for your cooking method - stovetop or pressure cooker) for 20-30 minutes, or until the rice is fully cooked and the grains are separate. Fluff the rice gently with a fork before serving.\n",
      "\n",
      "9. Garnish the biryani with chopped fresh cilantro and sliced almonds. Serve it hot with raita on the side for a cooling accompaniment. Enjoy!\n",
      "\n",
      "Enjoy your homemade Chicken Biryani!\n"
     ]
    }
   ],
   "source": [
    "openrouter_api_key = \"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\"  # paste your key here securely\n",
    "query = \"how to make biryani\"   \n",
    "\n",
    "#fattoush salad\n",
    "#mutabal\n",
    "#three beans salad\n",
    "# ceaser salad\n",
    "# baba ganoush\n",
    "# etc etc.\n",
    "\n",
    "output = chefbot(query, openrouter_api_key)\n",
    "print(output)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6101e178-5d07-4e0d-baaf-6f048c079171",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "49e6299f-8277-4dd7-85e6-e8c767ac3476",
   "metadata": {},
   "outputs": [],
   "source": [
    "#openrouter_api_key = \"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\"  # paste your key here securely\n",
    "#query = \"how to make baba ganoush\"\n",
    "\n",
    "#output = chefbot(query, openrouter_api_key)\n",
    "#print(output)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "2901f2fa-5147-4a36-8f7e-9235e7b250e4",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2025-07-30 09:45:37.419 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:37.419 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.359 \n",
      "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
      "  command:\n",
      "\n",
      "    streamlit run C:\\Users\\Fiddayy\\.conda\\envs\\llm\\lib\\site-packages\\ipykernel_launcher.py [ARGUMENTS]\n",
      "2025-07-30 09:45:38.359 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.375 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Session state does not function when running a script without `streamlit run`\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.391 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-07-30 09:45:38.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n"
     ]
    }
   ],
   "source": [
    "# 🎯 Streamlit App UI\n",
    "# ---------------------------\n",
    "st.set_page_config(page_title=\"ChefBot 🍽️\", layout=\"centered\")\n",
    "st.title(\"👨‍🍳 ChefBot\")\n",
    "st.write(\"Ask me for any recipe, and I’ll fetch or generate it!\")\n",
    "\n",
    "api_key = st.text_input(\"🔑 Enter your OpenRouter API key\", type=\"password\")\n",
    "query = st.text_input(\"📝 Enter a dish or recipe name\", placeholder=\"e.g., Chicken Biryani\")\n",
    "\n",
    "if st.button(\"🍽️ Get Recipe\") and query and api_key:\n",
    "    with st.spinner(\"Cooking up your recipe... 🍳\"):\n",
    "        try:\n",
    "            result = chefbot(query, api_key)\n",
    "            st.markdown(result)\n",
    "        except Exception as e:\n",
    "            st.error(f\"Error: {e}\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2c357d81-b5ac-436b-9a1f-e29cc97c9636",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "00297da4-3b4d-4063-9f82-8ffdd69ae2b0",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "56013056-64ed-4f5d-bd02-e9a03b04e4cc",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f712b58e-0d6e-4531-8aa1-f148ee5d11ff",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5e7f087b-0cb9-426b-862e-bdc7e2fb9754",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4b22b139-5c6f-4506-9a9c-a3fcb6ead896",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "93da0e84-cbf8-40c2-890f-971d93b5571a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6d6dfc71-75ab-4651-8b94-5f44debc743a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a5bbc3b2-bae4-4ec7-8e83-df3dd5b44b60",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d58a57b3-dbc9-472b-92f7-1eec9d922fbb",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "47ab0efc-4960-4049-8ef3-a8e5c0c7dee1",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dd0e066a-f975-4a5b-aab8-7b40f7312580",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f4a53895-02ca-424d-90bf-df64a64bdf59",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "48ba8fd3-bd1c-43fb-85d3-9040964041ea",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3ad775ae-2c40-43fe-89e7-aa139d017639",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d2c0935b-e055-46dc-9e87-99fa34671b33",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a2d32824-442a-40cd-98cb-18bd6cffb2ad",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6896ebd5-3e7e-414c-a4d8-152b10f03a97",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d7a1a840-4497-4951-bada-d0f78e8ac86e",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dc698398-3376-4992-9671-62886e468633",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e7c101a1-0467-4383-8973-aa446fbbcd75",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "239a5bc6-83b5-41b9-9904-2eb7a0b393ce",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "30c22c02-ee50-4372-b1d4-de8be0248418",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c69b6621-0362-4016-babd-c493846997b6",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d59ac3a6-6069-4107-b0c8-b16ca2e66d4a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "56cabbe9-bc1c-4f3d-a451-0cbf832d1759",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6908fe6a-57d0-46bc-b7c7-28aadfaba680",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9f310392-a504-46a4-ae16-6a830ce73bbe",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f22d4bfd-5815-438a-ac66-60c844c68a01",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0d283746-e3f2-43d1-8702-7293188f5ed1",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "36ff6938-c3ed-42fd-845c-8e3192bf6d3e",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "14c042b0-4644-4f91-9744-50175da6587a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4de83def-c155-4eb1-90ac-06c2a4eeea02",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "23cc7bab-c47f-495d-988d-079637c2f079",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "93247c35-74e0-4502-a808-c7fcf78eaad7",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "123a957b-e074-4da0-a531-7bddd7285cc1",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "55e34be3-e3ba-4a9c-95f4-6ce73a7c524b",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3c3fcf17-fa71-4ca5-bdec-604809a1a791",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2d49732c-bf61-4b60-8426-5b28e6b18856",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "66f9a4b9-bbdc-45ef-ba7a-48ca0e8b5304",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5b05eb1c-5684-469b-8370-4cf6774951e7",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "60749083-09b4-49e1-9134-7d675d82b14b",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a6d9cfdd-e44e-4a86-9cce-ef2134e3a3ee",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4bc7bba1-a90f-4eed-a8df-7783b7b9da51",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c7c91c01-4771-4403-9edd-08155a900297",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "410d67fb-f45c-4e22-9b69-8a0cb667a397",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6d972499-537d-4c3a-87ff-3631dc98ad72",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b024cea9-6507-4a6a-983c-a3a2b4361341",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "67fc3f0c-07e3-4c9d-a6ce-d7a45c708412",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8e9d8d6d-1f0f-4587-8a75-ee3a3ae218bc",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4e416296-8c5c-40db-a6dd-09f18da850f5",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bc7caf51-610a-4a3c-8e2c-0572afe05ccc",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "03dc81ea-b906-452b-8654-2aaa0965acba",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "82843e5c-1fab-4888-bada-2d87620d0cfb",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "792fb88b-196a-4365-a66a-aa838fe16697",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e8c2b154-bc95-43c7-864c-bb6516be7be3",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bdbe5a81-a2b6-41d4-b553-472643f16b05",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a4b96477-e83e-4f48-b1e7-222552eacae5",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2042649d-24d5-4ebc-87ad-fb6ea6751349",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "23e6b856-3a6e-4d0f-a242-a3349b584105",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d1b192f2-09a7-4bae-9ccd-252bce988c73",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1caffa1d-fed8-48bb-adbb-aef351f25eeb",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c62495d4-92ee-4db5-bac9-fde092b17ba5",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5a05ef31-ca79-493a-8e3d-556441a825af",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "03730fd8-49ae-427f-b9ee-6f84b0250ed5",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e89b502f-5a45-4c1f-9e4c-01772348b63a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6a5f8648-71c0-4fcb-90c9-05d9d807fd2b",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b26ec5d1-a6be-4af2-8f1d-094104021da7",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "54c8eab7-5ca2-42a5-89f2-e36abb07c731",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a9189b41-ea67-4e28-952e-d148d5e80dfa",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2eb10508-f3a6-4c3a-83e2-f64bed726e3b",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "012e8b15-5f73-432d-b78b-0249781eb0ea",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bf501e1a-264b-45ac-9720-1dcdc6663d7d",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ae739572-62e6-4eef-bffc-b837a3267c3f",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9a85a120-3bec-4a24-b277-ab14d4fe63e7",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "43070015-391b-4c97-83ae-e82ea1cec544",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4a8d381f-4508-4689-96a2-edd7eeb773ba",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9fe9c650-0865-4afd-b5b4-3bb620d679c6",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "126fdb14-c892-4ba8-bcf3-f5fa5a8dd8fe",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "06f0b1d9-9ea9-4271-b34e-c46d3609c1ec",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1cfa5964-6bb3-4ece-910a-d161555dfdde",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2ab2b90e-d356-498a-a717-9479f903a047",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b0408cc8-d541-457c-b2f2-bc28212b1454",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d80da1d9-e9d6-42a8-99fc-891476460b44",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "04f270ef-efbc-4afe-a370-9b640a8e8758",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "daef7d9e-d53c-4ed7-aa39-0a4e21bb179a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "17c7e7ad-a1f0-4420-ad96-4965466b797d",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cb8e6558-0f2b-453e-97e7-3323046ad0cf",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "20d8e937-aeb6-4c01-8f1e-bd46f8582f12",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "98bc9b24-e211-4d0e-99bd-d7c6454f7603",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3f5b2664-effa-44db-9d9a-008fedc714ac",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dbad4a26-d83d-40c8-b1f8-705fdc71f9aa",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "835c4a44-c072-4aca-b53e-af946d900e53",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "df48c7c8-bd1e-41d2-921e-07f08bd97b2d",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "407f1175-001a-4a22-b6a5-d324511f8269",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1cb5a433-8173-40d6-8223-7869e0301ad9",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f8229f92-f651-4e0a-8037-cb16c061ccdd",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8dbce481-060b-46ad-9b85-76fb560f06e9",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "251831af-69f7-4dbb-9ee0-e626849af9ed",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9606711d-3cda-43a6-9090-39dba803a9d3",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d84dbda0-ea77-4534-b949-b2b6f00b96ac",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e0a13c0e-bcbf-4127-b20e-7f92d1cca423",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "71597129-574d-4e18-94f7-c852a2b69cc3",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "451b8ef7-6217-44aa-8d51-7b57f2366fcf",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "82faad11-5f3f-46f6-a61c-14461bb2c8d3",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b8bf5367-c6f4-455c-aa47-a6d00483b1ba",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4fe6665d-f504-44b2-80fd-6b82d6a93bba",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e954a3a7-4647-4cbb-b14b-981e21397c1c",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e633e713-7a9d-4ece-8a53-03f0c8b3ff3e",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9c2a894c-ff14-4447-9f98-4eb1c13bc8ce",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9285a4f0-ef03-49b4-afe4-13e6218fe69c",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0c070f8d-bdec-492a-bf29-4b0e02e4beaa",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "acb7f3bd-186a-49f9-9a1d-ddcc5f86f4b1",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "67fca1bb-8ad6-4996-8bdd-43f2e4318d02",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ee0f5eb2-fdae-47f8-a099-943df3ec2b21",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ab4f8454-cb96-4131-b8c9-28ee6645ad06",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6bd192f2-7477-48ec-b578-909f76a3d3d1",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4bcba358-e7ee-45a7-b739-01150253a1c7",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "730b0d81-2c86-4af4-95cb-19485de7ff54",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a7b0aae4-4946-4f38-8698-224c39901c2b",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "08e0710f-3d96-4537-aab6-083600c4ced7",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c04846d3-997a-44f3-b5d6-a753cef138a8",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fc061e52-d84b-4360-9581-d5987a60d3ac",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ab1b67ef-a603-48b2-b5bf-7a9663376542",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ca521ea6-a05f-4202-8779-ccda75e1f424",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c2f9b7a7-9b58-4576-91f4-1a57be2407ab",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "16acf646-b896-42af-b4ca-171175a93849",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2c2abc75-4e5c-446a-b007-4a16769ba1c0",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c6177cfd-1c10-4db1-881d-eaca12a67490",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d7a5a766-9b61-4b69-b433-2e0fc204b997",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b2d1cb21-f7fa-4667-8527-35d6ce0519f4",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8f85c1be-66b5-4019-82be-4a2f89c03423",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f8d5a8df-10d0-42f5-ac37-6b9c8bd414e2",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "374cd4c7-7afc-4743-a09c-9fc45956dbe6",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "87a3c798-6d14-4d77-9195-3ce148a4c23c",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "99b41c46-5b6e-4d3c-b53d-5488f58af491",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f122c71d-29ef-4549-a6ad-c4688df3e4a8",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f2a62013-b76e-4a66-b5b5-c1f30804e908",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5156184a-6f85-4125-8c84-46968852579e",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dfb19717-9e07-4c80-ab12-d3c26ff03379",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f3731043-8923-4a31-9a82-6e16c76dd803",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ac63f08b-2a1b-422d-84b7-e7404fc7feb9",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "60114572-ada5-47db-a2f1-2761eaab031e",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c61cd415-8b88-4240-8d9d-2ffc0c8297d5",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6f4321aa-97ae-4eb2-8e38-469f17467b88",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e46f2f37-5e90-418d-b1e0-348a37009177",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "361649a3-ac44-47b4-a43d-19d40c26a374",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b220ef3c-0365-46c4-ac68-22082aad5c5e",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f19e173a-ce77-4096-a2d5-2f02dc9e5238",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "52e311ac-20b5-47b6-8944-6156d8992b62",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bbf4aaa2-05c8-4392-ae59-ac3f13cae48d",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2d38c7cb-dfc2-45fd-826a-85088cee3109",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "15c98f99-8f07-4716-bc2c-22ddbcfde59a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e60618a6-aaa0-4bf3-ab9a-91b438087c77",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "aed406d2-4a58-4f55-a433-dd7b3daeb102",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6116ef42-395c-47bb-bf9d-267e8743cee0",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4e486649-090b-42e0-8360-55f42aab161c",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4809925d-934d-407a-8466-49199fec560d",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d88a00b5-0ab4-4166-b59c-212694dcdbe5",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "81f65eaa-d672-47ff-b526-c921e9150f1e",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b11e910e-f3b9-4f5b-b9b7-be5fc013e785",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cb94d163-6175-4926-80ac-f1c25758c014",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b1bd7189-4d78-4601-b2cf-41fc7f0e8240",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "50877719-49ba-4a2d-89ff-00f3d0d7f61c",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1a8b9a3c-23bc-4f94-b3e3-1588a74513c7",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7267c9a9-da12-4639-a4c7-f81b80c41cf8",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "928bbe7a-9331-499f-98b5-e1d395d217ca",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f6827c9c-7198-4b55-be44-169497dee171",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "30cdb747-9b84-4d51-93d4-d79571991873",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "89759c4f-9aed-49bf-83d1-e36a7209f9d8",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b52b054d-b876-4ef9-b566-ae240fcc5bf6",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "79bfa929-23c0-4cd5-b760-4fecc0030f4a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "77e8a1dc-7bfe-4cef-b46e-454322fe1cf2",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c0d643b4-e0ac-42ec-b944-5cd26a3fc29a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b9853a85-ea76-4082-a394-c1b4f657c2a2",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b08f677f-8a0d-4614-a98a-a8a3099e0edc",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "56cecbaf-ade9-4447-8fea-cf3e4af08898",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "80edf86a-d9fe-4091-9874-e63ce181fcd5",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d41d924a-1c5c-4c3e-9e6b-5765f20c1333",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5db62613-215e-4347-a586-f66dd077b7b6",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c8513af4-94f4-4d2c-9486-295387e58d20",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9da4371a-b331-463a-84a1-f4520aad0a27",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "87a26858-0cdc-42a5-8815-ab71a4009697",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "960ae2a7-a146-45ff-b4cc-0fd8bc333a22",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7bfa8eb0-ddfa-4869-b14d-1878fdfabd4a",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "135eb6d2-7276-4fbb-9aa0-308d718f08e1",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cb4c18f4-cf3f-4a05-9305-9ef2d081131b",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "34a03b83-9c76-493d-bef3-fc934e35b618",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9d49875d-56e6-484a-aafb-42d5912e0a35",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d356b575-2053-475d-a211-5b08742cab4e",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.18"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
