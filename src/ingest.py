from pathlib import Path #path of file ke liye
from pypdf import PdfReader #to open pdf and pulling text from each page
import json #to save the chunks to a file
# import re #regular expression cleaing white spaces


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
#these are constants are path of data raw and data path 


# def clean_text(text):
#         text = re.sub(r"\s+", " ", text)# (pattern , replace,text) r means a raw string, +means one or more in a row
#         #\s+ means any anount of spaces newline or tabs converting it to single space (pattern,what to change it with,on what)
#         return text.strip() #removes spaces at start and end spaces in mid stay
#         # "  Marma \n\n is   a\tpoint \n"
#         # " Marma is a point "
#         # "Marma is a point"

def clean_text(text):
    return " ".join(text.split()) #split turns text into a list # ["Marma", "is", "a", "point"] removees whitespaces form start and end too and any long white spaces
#join will take 2 things first string and a list of strings
#it will make one string and join it unsing any operator or sting we choose at the front

def chunk_text(text, chunk_size=500, overlap=50):#default hai but we can change chunksize and overlapp when calling
    words = text.split() #cleand text to lekar will make arry of indivisual words
    list_of_chunks = [] #chunks ka ek empty array 
    start = 0 #say if we have a chunk the start will be position of the first word 
    # this comes handy if we want to implement overlapp but changing start = chunksize - overlap ir 500-50=450 so now the start of another chunk is 450 not 500 this ensures overlapp
    while start < len(words): #len of words can be very high say 1000 jab tak start is 1000 ke limit me rhega tab tak this loop will continvue 
        #the moment start becoms more than 1000 means the text has ended it will stop 
        #this also helps in say if we have 200 words remaining after deviding every 500 chunks we will get a chunk size of 200 instead of an error or miscalculatin
        end = start + chunk_size #at whihch position do we want to end the chunk ofc its start+500
        chunk = " ".join(words[start:end])
        #wordsstartend will give an array of words from start to end-1 
        #and join will join it using " " as seperator
        if chunk: #if there is atlest something in chunk 
            list_of_chunks.append(chunk) #then add that chunk in the list of chunks 

        start += chunk_size - overlap
    return list_of_chunks



def process_pdfs():
    documents = [] #holds chunks
    pdf_files = list(RAW_DIR.glob("*.pdf"))#find every pdf in the location convert it into a list of pdfs so that len function works on it
    #*means any charecter
    print(f"Found {len(pdf_files)} PDFs") #just a check wether all the pdf are receved or not
    for i in pdf_files:
        #loop go pdf by pdf one pdf at a time
        print(f"Processing: {i.name}")
        reader = PdfReader(i) #only reads structure but dont pull any text yet
        for page_number, page in enumerate(reader.pages, start=1):
            #go page by page one page at a time
            #reader.pages is just list of pages
            #enumerate generates pairs of number and page pagenumber(used when creating a dictionary) me number starting with 1 hoga
            #and page me that actual item ie a page
            text = page.extract_text() or "" #this is the text pulling phase
            
            text = clean_text(text)
            #this is where we clean text
            if not text:
                continue #in case the cleand page turns out to be enpty
            #if the page contain cleaned text then
            chunks = chunk_text(text)

            for chunk_number, chunk in enumerate(chunks): #assigne a number to each chunk while we can use items 
                # this way we can use chunk number for some resaon
                documents.append({
                    "source": i.name, 
                    "page": page_number,
                    "chunk": chunk_number, #this is where we use chunk number 
                    "text": chunk
                }) #what document contains is a dictionary of 4 items  souce page chunk text

    return documents


if __name__ == "__main__":

    documents = process_pdfs() #the list of dictionsy ie document is stored in documents
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True) #makes a processes directory defined by a global variable 
    #in case if its not present parents =true will also create data forlder in which process dir exits 
    #if that folder exists then we wont make any this is handles by existok=true
    output_file = PROCESSED_DIR / "chunks.json" #just a path on where results will be saved


    
    with open(output_file, "w", encoding="utf-8") as f: #unicode encoding 2B
        json.dump(documents, f, ensure_ascii=False, indent=2)
        #with will open the file and auto close 
        # it will open the output file path file with write insturctions and we can use it using a file handler f
        # we want the chunks to be read by bm25 which opens the file with same encodeing 
        # we need to define it as diffent encoding may have probles reading the file 
        # utf will also help later for hindi sanskrit texts
        #now json is just a text format file for storing structure data similar notations as pytthon list and dicts
        #dump takes 2 input object and file simply convers ovj to json text\
        #example data = [{
        #       "source": "File No 2960.pdf",
        #       "page": 1,
        #       "chunk": 0,
        #       "text": "Marma point: Kshipra ā"}]

        # to  [{"source": "File No 2960.pdf", 
        #       "page": 1,
        #       "chunk": 0,
        #       "text": "Marma point: Kshipra \u0101"}]

        # ensureascii will ensure if there are any special charecter we want them to be sore as is and by not converting it 
        # if we used a true valude ā will be stored as as \u0101
        # indent is only for better visual experience 2 means adds 2 space indentation .. it also adds line break
    print()

    print(f"Created {len(documents)} chunks")