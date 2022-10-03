#!/usr/bin/env python
# coding: utf-8

# In[14]:


#!pip install -U pip setuptools wheel
#!pip install -U 'spacy[apple]'
#!python -m spacy download en_core_web_sm


# In[17]:


get_ipython().system('pip install nltk')


# In[18]:


import nltk
nltk.download('punkt') #recognizes punctuation.
nltk.download('averaged_perceptron_tagger') #default part of speech tagger for NLTK.
nltk.download('maxent_ne_chunker') #Named Entity Chunker for NLTK. 
nltk.download('words') #NLTK corpus of words.


# In[19]:



text ="Mining and resources companies were given an extraordinary level of access to the highest rungs of the New South Wales government in the past four years, securing roughly 188 meetings with ministers in 235 weeks. An analysis of four and a half years of the state’s ministerial diaries shows the NSW Minerals Council has obtained regular access to resources, planning and finance ministers, and the offices of premiers and deputy premiers. The council was given 61 meetings with NSW ministers, more than anyone except the NSW Farmers Association, the City of Sydney council and Penrith city council. Further meetings were granted to multinational resource and energy companies such as Shenhua, Whitehaven, Glencore, AGL, Rio Tinto, BHP, Origin Energy, Santos, Anglo American and Centennial Coal."

tokenized = nltk.word_tokenize(text)
pos_tagged = nltk.pos_tag(tokenized)
chunks = nltk.ne_chunk(pos_tagged)
for chunk in chunks:
   if hasattr(chunk, 'label'):
       print(chunk)


# In[ ]:




