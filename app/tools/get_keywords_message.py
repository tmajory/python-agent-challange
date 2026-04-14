#Trata o texto da pergunta do usuário, para extrair palavras-chave relevantes, ignorando palavras comuns e conectivos, 
# para melhorar a busca na KB.
import string
from unidecode import unidecode

articles = ['o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas']
interrogatives = ['o que', 'como', 'por que', 'quando', 'onde','que','qual','quais']
prepositions = ['de', 'do', 'da', 'dos', 'das','em', 'no', 'na', 'nos', 'nas']
conective = ['e', 'ou']


def get_keywords(message:str):
    words_list = unidecode(message.lower().translate(str.maketrans('','',string.punctuation))).split()
    keywords = []
    for word in words_list:
        if word not in articles and word not in interrogatives and word not in prepositions and word not in conective:
            keywords.append(word)    
    return keywords
       
if __name__ == "__main__":
    message = "Qual a composição de um átomo?"
    keywords = get_keywords(message)
    print(keywords)
