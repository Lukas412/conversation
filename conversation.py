import string
import subprocess
import sys
from pathlib import Path
from typing import Set, List


def remove_prefix(text: str, prefix: str):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_suffix(text: str, suffix: str):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text


class Person:
    name: str
    _personality: List[str]

    def __init__(self, name: str):
        self.name = name
        self._personality = []

    @property
    def personality(self) -> str:
        return ' '.join(map(str.strip, self._personality))

    def add_personality(self, personality: str):
        self._personality.append(personality)


def collect_persons():
    persons = []
    current = None
    with open(_project_dir() / 'Persons.md') as file:
        for line in file.readlines():
            line = line.rstrip()
            if not line.startswith('>'):
                if current is not None:
                    persons.append(current)
                    current = None
                continue
            if line.startswith('> **') and line.endswith('**'):
                if current is not None:
                    continue
                name = remove_suffix(remove_prefix(line, '> **'), '**')
                name_allowed = string.ascii_lowercase + '- _'
                if any((char not in name_allowed for char in name.lower())):
                    continue
                name = string.capwords(name.replace('_', ' ').replace('-', ' '))
                current = Person(name)
                continue
            if line.startswith('> '):
                line = remove_prefix(line, '> ')
                personality_allowed = string.ascii_lowercase + ' ,._-'
                if any((char not in personality_allowed for char in line.lower())):
                    continue
                current.add_personality(line)
                continue
    if current is not None:
        persons.append(current)
    return persons


def get_persons_in_conversation() -> Set[Person]:
    persons = collect_persons()
    filter_names_lower = list(map(str.lower, sys.argv[1:]))
    return set(person for person in persons if person.name.lower() in filter_names_lower)


def run_llm(model: str, prompt: str) -> str:
    process = subprocess.Popen(['ollama', 'run', model, prompt], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return ''.join(char.decode('utf8') for char in iter(lambda: process.stdout.read(1), b''))


def _project_dir() -> Path:
    return Path(__file__).parent


def main():
    persons = get_persons_in_conversation()
    for person in persons:
        print(f'## {person.name}')
        print(person.personality)


if __name__ == '__main__':
    r = run_llm('llama2', 'In one small sentence: What is a bird?')
    print(r)
