import json
import re
from pathlib import Path
from rank_bm25 import BM25Okapi
import shutil
CHUNKS_FILE = Path("data/processed/chunks.json")

def tokenize(text): #lowecase and split
    lower_text=text.lower() # why lower case - bm25 is case ensitive MARMA and marma would be differnt words but they actually are the same
    return re.findall(r"\b\w+\b", lower_text)
    #didnt use split becus it only splits at white spaces 
    #we wanted tokes to contain splits at every thing that is not a letter of digit
    #so findall just takes 2 things pattern and text and returns a list of things kept 
    #it scans text and creates a list of everty part that matches the patter 
    #patter here is r"\b\w+\b" meaning \w means one word charecter(letter digit _ also letter like ā)
    # w+ means charects what are one or more in a row .. basically words if 
    # \b means boundary includes start end of text .. space comma hipher etc
    #ex   "Pain (knee) - 3.5 kg/day!"
    # this will keep pain knee 3 5 kg day 
    # and remove spaces () - . / ! ie anything that isn't a letter, digit or underscore. 
    #this function at final returns a list of words of the text part of chunk in document
# CHECK INTO IT
def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        #this opens the chunk file as read accees using same encodeing as we save erlier
        # files is opend with with which auto closes and file handler is f
        return json.load(f) 
        #load does what dunp does but in revers ie json file to python object 
        #so load chunks will return list of dictionary that we talked about with source page chunk and text

def build_bm25(documents): #input is list of dics
    tokenized_corpus = []# a corpurs is coleection of texts part of the chunk in the doc
    for doc in documents:  #this will doc will contain one chunk at a time 
        #documents conatina list of dictionary  so each dictionsy is a chunk               
        words = tokenize(doc["text"])      #takes one chunk ka text part and call tokenize on it 
        #tokenize retuns a list of words of the text part of chunk

        tokenized_corpus.append(words)     # this will simply add that list in the tokenized coruups list
        #so tokenized corupus is a list of list of words returns by tokenize 
    
    bm25 = BM25Okapi(tokenized_corpus)
    # this computes some number no search happens here nor we get any scores
    # it computes 
    # no of chunks = corpus size = n for idf
    # len of each chunks = doc_len for lenght normalisaton
    # average chunk len avgcl for a reference of long or short 
    # words count per chunk = frequency = f ie how ofter words appers in one chunk
    # idf = how rare is each word in the whole corpus ir all chunks

    # it returns an object that holds these number which are useful to api and searching
     
#example
# corpus = [["marma","points","are","vital"],
#           ["knee","pain","and","marma","therapy"],
#           ["knee","osteoarthritis","marma","marma"]]

# bm25.corpus_size=3
# bm25.doc_len=[4, 5, 4] list of number of words per list
# bm25.avgdl=4.333
# bm25.doc_freqs[2]	{'knee': 1, 'osteoarthritis': 1, 'marma': 2} dict with item=frequency
# bm25.idf	marma: 0.031 (in all 3 chunks, so almost worthless), knee: 0.031, osteoarthritis: 0.511 (in 1 chunk, so it counts more)

# at last bm25.get_scores(query_words) will get use our scores later

    return bm25
# this returns an object with all the numbers needed to compute store 

# def search(bm25, documents, query, top_k=5):
#     """
#     Search the BM25 index.
#     """
#     tokenized_query = tokenize(query)

#     results = bm25.get_top_n(
#         tokenized_query,
#         documents,
#         n=top_k
#     )

#     return results
def search(bm25, documents, query, top_k=5):#keep top 5
    tokenized_query = tokenize(query) #will simple give a list of words of the query 
    #which will be used later


    scores = bm25.get_scores(tokenized_query) 
    #what it gives score to every chunk based on our query looping one word at a time fron query word
    #it returns a list of score of each chunk - so we have a list of corpus size lenght
    #scores are in one to one corresponcene with the document cunks
    #detailed explaination::
    #takes input as list of words of query
    #creats an np array of same size as corpus size initaiating all with 0 
    #picks one words of the query

    #calulates how many times the word appeard in each chunk 0 1 2 3 4 using frequency of bm25
    # doc frequncy is a list of dict of key value pair with item and frequcy of each chunk
    # so for each word in query all we need to do is compare word with frequency 

    #now idf is calcualted using idf of corpus



    # ranked_indices = scores.argsort()[::-1][:top_k]




    where_would_it_be = scores.argsort() 
    # [1.8, 0.2, 3.5, 0.9].argsort() → [0.2, 0.9, 1.8, 3.5] → [1, 3, 0, 2].
    # numpy lsit sort karne ke baad wo element kaha hua karta tha uska list
    #this gives position from smallest to larget scores
    # how - simply replace position with score store there
    # but wee need big to small socre to fetch first  k
    # so we simple reverse this list    
    
    order_high_to_low = where_would_it_be[::-1] 
    #now this will reverse the list now big sores are front and small are back 
    ranked_indices    = order_high_to_low[:top_k]      
    #now we simply take the first k terms and put it in ranked indexes


    results = []
    #so now we need to show the results 
    #so that we took an anrray results empty

    for index in ranked_indices: #now index contain one item of ranked indexes 
        results.append({
            "score": float(scores[index]), #adding scores ka index postion to score
            "document": documents[index] #adding dodument ka index postion to score 
            #this will be used to print all other necessacites like text chunk page source
            #enumerating will be needed later
        })
    return results


if __name__ == "__main__":

    documents = load_chunks() #this will call load chunks function and the list of dictionaries are stored in documents

    print(f"Loaded {len(documents)} chunks") #just a check 

    bm25 = build_bm25(documents) #build is called and returns one object contain 5 things
        # bm25.corpus_size   
        # bm25.avgdl          
        # bm25.doc_len       
        # bm25.doc_freqs      
        # bm25.idf



#check using a query tesitng
    query = "marma therapy knee osteoarthritis"

    results = search( 
        bm25, #bm25 ie object of computed numbers of all the chunks 
        #will be used to calculate scores 
        documents, #documents - the list of dics ie all the original chunks 
        #bm 25 will give only score .. but what is in that chunk will be fetched from documents
        query, #query - what we search for
        #  this will be used to score the chunks
        top_k=5 #how many results you want back 
    )
    #result will return list of dict containg 2 things scre  and document of index field

    print()
    print(f"Query: {query}")
    print("=" * 80)

    for i, result in enumerate(results, start=1): #i is number and result is the item so it picks one dictionary or results list
        #i is here to just number results also start is 1 so i starts from 1
        doc = result["document"] # need to separte documet part in oder to print document dictionary stuff
        print(f"\nRESULT NUMBER {i}")
    #score of result chunk
        print(f"Score  : {result['score']:.4f}") #after decimal use 4 digit only
    #content of doucment chunk
        print(f"Source : {doc['source'][:50]}")
        print(f"Page   : {doc['page']}")
        print(f"Chunk  : {doc['chunk']}")
        print(f"Text   : {doc['text'][:500]}") # only prints first 500 charecters of 500 word chunk

        width = shutil.get_terminal_size().columns
        print("-" * width)  