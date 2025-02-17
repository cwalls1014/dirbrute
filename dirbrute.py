import queue
import requests
import threading
import sys
import argparse

AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
TARGET = ''
THREADS = 0
WORDLIST = ''
OUTPUT_FLIE = ''

def get_words(resume=None):
    def extend_words(word):
        if "." in word:
            words.put(f'/{word}')
        else:
            words.put(f'/{word}/')
        
        for extension in EXTENSIONS:
            words.put(f'/{word}{extension}')

    with open(WORDLIST) as f:
        raw_words = f.read()

    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f'Resuming wordlist from: {resume}')
        else:
            print(word)
            extend_words(word)
    return words

def dirbrute(words):
    headers = {'User-Agent': AGENT, 'X-HackerOne-Research': 'flawedspoon'}
    while not words.empty():
        url = f'{TARGET}{words.get()}'
        try:
            r = requests.get(url, headers=headers)
        except:
            sys.stderr.write('x');sys.stderr.flush()
            continue

        if r.status_code == 200:
            with open(f'{OUTPUT_FILE}', 'w') as output:
                output.write(f'\nSuccess ({r.status_code}: {url})')
                print(f'\nSuccess ({r.status_code}: {url})')
        elif r.status_code  == 404:
            sys.stderr.write('.');sys.stderr.flush()
        else:
            print(f'{r.status_code} => {url}')


if __name__ == '__main__':
    # ArgParse Setup
    parser = argparse.ArgumentParser(description='Brute-Forces website directories.')
    parser.add_argument('-t', help='Target URL')
    parser.add_argument('-w', help='Path to wordlist')
    parser.add_argument('-r', help='Number of threads to use')
    parser.add_argument('-o', help='File in which to save output')
    args = parser.parse_args()

    if args.t == None:
        print('Target URL required.')
        sys.exit()
    elif args.w == None:
        print('Wordlist required.')
        sys.exit()
    elif args.r == None:
        print('Threads required')
        sys.exit()
    elif args.o == None:
        print('Output file required')
        sys.exit()
    
    TARGET = args.t
    WORDLIST = args.w
    THREADS = int(args.r)
    OUTPUT_FILE = args.o

    words = get_words()
    print('Press return to continue.')
    sys.stdin.readline()
    for _ in range(THREADS):
        t = threading.Thread(target=dirbrute, args=(words,))
        t.start()