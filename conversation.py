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

    @property
    def filename(self) -> str:
        return self.name.lower().replace(' ', '')

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


def create_person_llm(person: Person):
    with open(_project_dir() / 'template.mk', mode='r') as file:
        template = file.read()
    template.format(personality=person.personality)
    filepath = (_models_dir() / person.filename).with_suffix('.mk')
    with open(filepath, mode='w', encoding='utf8') as file:
        file.write(template)
    process = subprocess.Popen(['ollama', 'create', person.filename, '-f', str(filepath.absolute())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process.wait()


# ollama create mario -f ./Modelfile


def _project_dir() -> Path:
    return Path(__file__).parent


def _models_dir() -> Path:
    directory = _project_dir() / 'models'
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def main():
    persons = get_persons_in_conversation()
    for person in persons:
        print(f'creating {person.name} ...')
        create_person_llm(person)
        print('done!')
    print()
    conversation = 'This is a conversation:\n'
    print('Conversation:')
    while True:
        for person in persons:
            conversation = f'{conversation}\n{person.name}: '
            print(f'{person.name}: ', end='', flush=True)
            answer = run_llm(model=person.filename, prompt=conversation)
            print(answer.rstrip())
            conversation += answer


if __name__ == '__main__':
    main()
