import nltk
from bs4 import BeautifulSoup
import requests
import pandas as pd
from nltk import word_tokenize,sent_tokenize
from statistics import mean
import string
import re
import math


def w_c(doc):
    """Function to calculate number of words in a document

    Args:
        doc (list): any document eg: mined pdf/youtube transcript

    Returns:
        integer: count of number of words in the document

    """           
    w=cleaner(doc)
    return(len(w))



def new_s_c(doc):
    """sentence counter

    Args:
        doc (string): document like transcript, pdf etc

    Returns:
        integer: count of number of sentences
    """
    s=doc.split(".")
    return len(s)



from nltk.corpus import cmudict
#global varaible d for storing cmudict key,value pairs
d = cmudict.dict()



def sy_c(word):
    """Function to count number of syllables in a given word

    Args:
        word (string): any word eg: Hello

    Returns:
        integer: return number of syllables
    """
    try:
        l=[]
        m=[]
        w=d[word.lower()]
        for x in d[word.lower()]:
            l=[]
            for y in x:
                #match with last char of the phoneme eg: AE1 AH0
                if y[-1].isdigit():
                    l.append(y)
        m.append(len(l))
        return m[0]
    except KeyError:
        return syllables(word)



def syllables(word):
    """Function to count no of a syllables in a word which is a Proper Noun

    Args:
        word (string): Any word or proper noun

    Returns:
        integer: No of syllables in the word based on phonetics
    """
    count = 0
    vowels = 'aeiouy'
    word = word.lower()
    if word[0] in vowels:
        count +=1
    for index in range(1,len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count +=1
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count+=1
    if count == 0:
        count +=1
    return count



def t_sy_c(doc):
    """Function to calculate total number of syllables in a document by iterating through each word.


    Args:
        doc (string): full document eg: mined pdf/youtube transcript

    Returns:
        integer: total count of syllables in a document
    """     
    c=0
    for w in cleaner(doc):
        c=c+float(sy_c(w))
    return c




def cleaner(doc):
    """Function to clean any fetched data i.e. to remove non alpha items eg: /1'/*^&@!

    Args:
        doc (string): full document eg: mined pdf/youtube transcript/fetched data from a url

    Returns:
        list: cleaned document with non alpha items removed
    """
    w=word_tokenize(doc)
    cln=[]
    cla=[]
    for i in w:
        if i.isalpha():
            cln.append(i.lower())
    for i in cln:
        if len(i)>1:
            cla.append(i)
    return cla





def rtcal(doc):
    """function to calculate reading time of a document i.e. total words/200 wpm

    Args:
        doc (string): item whose reading time is to be calculated

    Returns:
        float: reading time in wpm
    """
    x=float(w_c(doc))
    return x/200






def fl_rs(doc):
    """function to calculate flesch reading score of any document

    Args:
        doc (string): item whose reading score is to be calculated

    Returns:
        float: flesch reading score of the document be it transcript,pdf etc
    """
    try:    
        cnt=float(206.835-(1.015*(w_c(doc)/new_s_c(doc)))-(84.6*((t_sy_c(doc)/w_c(doc)))))
    except:
        print("divide by 0 error")
        cnt=-1
    return cnt



def generator(l,func):
    """function use to return a list of tuples of items whose data has been fetched properly,
    function used here is fcal(), any other similar function can be created and used.

    Args:
        l (list): list of the transcripts/pdfs etc
        func (function): function to determine what tuple you need

    Returns:
        list: list of tuples of values returned from func 
    """
    t=[]
    substr="DATA COULD NOT BE FETCHED"
    cnt=1
    for i in l:
        print("working on item no.",cnt)
        if substr in i:
            t.append(-1)
        else:   
            w=func(i)
            t.append(w)
        cnt+=1
    return t




def fcal(doc):
    """function to generate a tuple of flesch score, word count and read time for a single entity

    Args:
        doc (string): entity for which the above mentioned are to be calculated

    Returns:
        tuple: tuple of flesch score,word count and read time for a single entity
    """
    x=fl_rs(doc)
    y=float(w_c(doc))
    z=rtcal(doc)
    return (x,y,z)


#example:  path='c:/users/misra/Documents/Edwisely/readability 0.1/pdfs/'
def dwn_pdf(l,path,c=-1):
    """function to download pdfs and store at desired path

    Args:
        l (list): list of urls from which pdfs need to be downloaded 
        path (string): desired path where you want to save the pdfs
        c (int, optional): Sets the names of the pdfs as index value, start_index=c+1. Defaults to -1.
    """
    import requests
    import wget
    for i in l:
        c=c+1
        url=i
        try:
            myfile=requests.get(url,allow_redirects=True)
            open(path+str(c)+'.pdf','wb').write(myfile.content)
        except:
            print("error in url",i)
            continue





def ex_txt_pdf(l,path,c=-1):
    """function used to mine text from a given pdf

    Args:
        l (list): list of links of pdfs
        path (string): path where pdfs are saved
        c (int, optional): starting index -1 of where to start the extraction from. Defaults to -1.

    Returns:
        dictionary: links are keys and values store the string that hold data of each corresponding link.
    """
    import pdfminer
    from pdfminer.high_level import extract_text
    t={}
    for i in l:
        c=c+1
        print("READING "+str(c)+'.pdf')
        try:
            s=pdfminer.high_level.extract_text(path+str(c)+'.pdf')
            s=s.replace("\n"," ")
            t.update({i:s})
            s=""
        except:
            t.update({i:"DATA COULD NOT BE FETCHED FROM THIS DAMAGED PDF"})
            print("DAMAGED PDF")
    return t







from urllib.parse import urlparse,parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

def video_id(value):
    """function to obtain video id from url

    Args:
        value (string): url

    Returns:
        string: video id

    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    
    """

    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


def gettrans(url):
    """function to obtain transcripts from youtube URL as a string

    Args:
        url (string): url

    Returns:
        string: Youtube transcript fetched from the given URL
    """


    err="DATA COULD NOT BE FETCHED FROM THIS URL: "+url
    try:
        vid=video_id(url)
        l=YouTubeTranscriptApi.get_transcript(vid)
    
        t=""
        for i in l:
            t=t+"."+i['text']
        return t
    except:
        return err


def getlist(li):
    """fucntion to generate a list of transcripts from given list of URLs

    Args:
        li (list): list of urls

    Returns:
        list: list of transcripts
    """
    cnt=1
    w=[]
    for url in li:
        print("working on link no.",cnt)
        w.append(gettrans(url))
        cnt+=1
    return w



def bucket_vids(l):
    """function to create a list of bucket values for given list of flesch score for videos

    Args:
        l (list): list of flesch scores of videos

    Returns:
        list: list of appropriate corresponding bucket values for videos
    """
    vidl=[]
    for i in l:
        try:
            if i >=87:
                vidl.append("EASY")
            elif i>=75:
                vidl.append("MEDIUM")
            elif i>=0:
                vidl.append("HARD")
        except:
            vidl.append("NA")
    return vidl




def bucket_docs(l):
    """function to create a list of bucket values for given list of flesch scores for documents

    Args:
        l (list): list of flesch scores of documents

    Returns:
        list: list of appropriate corresponding bucket values for documents
    """
    docl=[]
    for i in l:
        try:
            if i>=50:
                docl.append("EASY")
            elif i>=35:
                docl.append("MEDIUM")
            elif i>=0:
                docl.append("HARD")
        except:
            docl.append("NA")
    return docl






       