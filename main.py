import hashlib
from pathlib import Path
from typing import Dict, Set, Generator

import htmlmin
from bs4 import BeautifulSoup

QUESTION_TAG_CLASS = 'qtext'
RIGHT_ANSWER_TAG_CLASS = 'rightanswer'
USED_PARSER = 'html.parser'


def get_files_content(file_list: Generator[Path]) -> Dict[str, str]:
    return {str(file): file.read_text(encoding='utf-8') for file in file_list}


def load_soup(file_content: str) -> BeautifulSoup:
    minified_html = htmlmin.minify(file_content, remove_empty_space=True)
    return BeautifulSoup(minified_html, features=USED_PARSER)


def normalize_answer_language(answer_tag: BeautifulSoup) -> BeautifulSoup:
    return BeautifulSoup(str(answer_tag).replace('The correct answer is:', 'Odpowiedź:')
                         .replace('Poprawna odpowiedź to:', 'Odpowiedź:'), features='html.parser'
                         )


def load_tags_map(soup: BeautifulSoup) -> Dict[bytes, Dict[str, BeautifulSoup]]:
    question_tags = soup.findAll('div', {'class': QUESTION_TAG_CLASS})
    right_answer_tags = soup.findAll('div', {'class': RIGHT_ANSWER_TAG_CLASS})
    return {
        hashlib.md5(str(question_tag).encode('utf-8')).digest(): {
            'question_tag': question_tag,
            'answer_tag': normalize_answer_language(answer_tag)
        } for question_tag, answer_tag in zip(question_tags, right_answer_tags)
    }


def show_already_hashed(file_path: str, already_hashed: Set[bytes], currently_hashed: Set[bytes]):
    number_of_already_hashed = len(already_hashed.intersection(currently_hashed))
    print(f"Number of already hashed questions from file: {file_path} is: {number_of_already_hashed}")


def save_answers(whole_map: Dict[bytes, Dict[str, BeautifulSoup]]):
    output_soup = BeautifulSoup('', features=USED_PARSER)
    for key, tags in whole_map.items():
        output_soup.append(tags['question_tag'])
        output_soup.append(tags['answer_tag'])
    output_soup = BeautifulSoup(output_soup.prettify(encoding='utf-8'), features='html.parser')
    Path('answers.html').write_text(str(output_soup), encoding='utf-8')


def main():
    whole_map = {}
    files_to_analyze = Path('files_to_analyze').glob('*')
    files_content = get_files_content(files_to_analyze)
    for file_path, file_content in files_content.items():
        soup = load_soup(file_content)
        tags_map = load_tags_map(soup)
        show_already_hashed(file_path, set(whole_map.keys()), set(tags_map.keys()))
        whole_map.update(tags_map)
    save_answers(whole_map)


if __name__ == '__main__':
    main()
