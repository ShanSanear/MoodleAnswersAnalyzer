import hashlib
import re
from pathlib import Path

import htmlmin
from bs4 import BeautifulSoup

files_to_analyze = Path('files_to_analyze').glob('*')
mapping = {}
temp_soup = BeautifulSoup('', features='html.parser')
for file in files_to_analyze:
    already_hashed = []
    print(f"Getting data from file: {file}")
    html_raw = file.read_text(encoding='utf-8')
    minified = htmlmin.minify(html_raw, remove_empty_space=True)
    soup = BeautifulSoup(minified, features='html.parser')
    questions = soup.findAll('div', id=re.compile('^q[\d]+$'))
    for qid, question in enumerate(questions):
        question_qtext_tag = question.find('div', {'class': 'qtext'})
        correct = question.find('div', {'class': 'rightanswer'})
        h = hashlib.md5(str(question_qtext_tag).encode('utf-8')).digest()
        if h in mapping:
            continue
        mapping[h] = {'question_tag': question_qtext_tag, 'anwser': correct}
        temp_soup.append(question_qtext_tag)
        temp_soup.append(correct)
        already_hashed.append(qid)
    print(f"Number of already hashed for file: {file} is: {len(already_hashed)}")
with Path('answers.html').open('w', encoding='utf-8') as f:
    f.write(str(temp_soup))
