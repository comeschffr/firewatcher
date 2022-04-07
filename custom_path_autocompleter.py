import readline
import os


def completer(text: str, state: int) -> str:
    last_path = os.path.dirname(
        readline.get_line_buffer().split(' ')[-1]
    )
    direntry = os.scandir('./'+last_path)
    volcab = []
    for item in direntry:
        if item.is_dir():
            volcab.append(item.name+"/")
        else:
            volcab.append(item.name+" ")
    results = [x for x in volcab if x.lower().startswith(text.lower())] + [None]
    return results[state]


readline.parse_and_bind('tab: complete')
readline.set_completer(completer)


input('>>> ')
