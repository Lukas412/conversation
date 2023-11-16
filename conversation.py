import string
from pathlib import Path


class Person:
    name: str
    _personality: list[str]

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
                name = line.removeprefix('> **').removesuffix('**')
                name_allowed = string.ascii_lowercase + '- _'
                if any((char not in name_allowed for char in name.lower())):
                    continue
                name = name.replace('_', ' ').replace('-', ' ').replace('  ', ' ').title()
                current = Person(name)
                continue
            if line.startswith('> '):
                line = line.removeprefix('> ')
                personality_allowed = string.ascii_lowercase + ' ,._-'
                if any((char not in personality_allowed for char in line.lower())):
                    continue
                current.add_personality(line)
                continue
    if current is not None:
        persons.append(current)
    return persons


def _project_dir() -> Path:
    return Path(__file__).parent


def main():
    persons = collect_persons()
    for person in persons:
        print(f'## {person.name}')
        print(person.personality)


if __name__ == '__main__':
    main()
