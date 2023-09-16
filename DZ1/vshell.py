import argparse
import tarfile
import os

class VShell:
    def __init__(self, fs):
        self.cwd = "/"  # Текущая рабочая директория
        self.fs = fs    # текущий путь офайловой системы

    def _get_file_list(self):
        # Получение списка файлов и папок в текущей директории из архива

        #открываем архив для чтения , результат сохраняем в tar
        with tarfile.open(self.fs, 'r') as tar:
                    #возвращаем каждое имя файла из полного пути в списке всех файлов в архиве
            return [os.path.basename(member) for member in tar.getnames() 
                    # если название директории, в которой находится файл = рабочей директории 
                    if os.path.dirname(member) == self.cwd[1:]]

    def _extract_file(self, file_name):
        # Извлечение содержимого файла из архива
        with tarfile.open(self.fs, 'r') as tar:
            #получаем содержимое, объеденяю текущую раб. дерикторию и имя файла, читаем содержимое и декодируем в UTF-8(в строку из бинарной)
            return tar.extractfile(os.path.join(self.cwd[1:], file_name)).read().decode('utf-8')

    def pwd(self):
        # Вывод текущего рабочего каталога
        return self.cwd

    def ls(self):
        # Вывод списка файлов и папок в текущей директории
        return "\n".join(self._get_file_list())

    def _directory_exists(self, directory):
        # Проверка существования указанной директории в архиве
        with tarfile.open(self.fs, 'r') as tar:
            #     если путь директории member = с той которую передали, пребирая все файлы в архиве,
            return any(os.path.dirname(member) == directory for member in tar.getnames() 
                       # проверяем только файлы у которых есть родительская директория
                       if os.path.dirname(member) != '')

    def cd(self, directory):
        # Изменение текущей директории
        if directory == "..":
            if self.cwd == "/":
                return f"cd: ..: No such directory"
            else:
                # Убираем последний сегмент пути (переходим на уровень выше)
                self.cwd = os.path.dirname(self.cwd)
        else:
            #новая директория = текущий путь + путь файла
            new_dir = os.path.join(self.cwd[1:], directory)
            #если существует то устанавливае новую директорию
            if self._directory_exists(new_dir):
                self.cwd = '/' + new_dir
            else:
                return f"cd: {directory}: No such directory"

    def cat(self, file_name):
        # Вывод содержимого файла
        with tarfile.open(self.fs, 'r') as tar:
            try:
                #полное имя = текущий путь без / + имя файла
                full_path = os.path.join(self.cwd[1:], file_name).replace("\\", "/")
                #читаем файл
                file_data = tar.extractfile(full_path).read().decode('utf-8')
                return file_data
            #файл не найден или неправильный тип
            except (KeyError, TypeError):
                return f"cat: {file_name}: No such file. Full Path: {full_path}"

def main():
    #создаю объект который будет обрабатывать аргументы
    parser = argparse.ArgumentParser()
    parser.add_argument("fs", help="Path to the file system(tar).")
    parser.add_argument("--script", help="Path to the script file containing commands to execute.")

    args = parser.parse_args()

    #создаю объект vshell
    vshell = VShell(args.fs)

    if args.script:
        # Если указан скрипт, выполняем команды из скрипта
        with open(args.script, 'r') as script_file:
            commands = script_file.readlines()
            for command in commands:
                output = execute_command(vshell, command.strip())
                if output:
                    print(f"    command: {command}{output}")
    else:
        # В противном случае запускаем интерактивный режим
        while True:
            #текущая_директория$ 
            command = input(f"{vshell.pwd()}$ ")
            if command == "exit":
                break
            output = execute_command(vshell, command)
            if output:
                print(output)

def execute_command(vshell, command):
    parts = command.split()
    if len(parts) == 0:
        return None

    cmd = parts[0]

    if cmd == "pwd":
        return vshell.pwd()
    elif cmd == "ls":
        return vshell.ls()
    elif cmd == "cd" and len(parts) > 1:
        return vshell.cd(parts[1])
    elif cmd == "cat" and len(parts) > 1:
        return vshell.cat(parts[1])
    else:
        return f"Command not found: {command}"

if __name__ == "__main__":
    main()

# cd DZ1
# python vshell.py tarfile.tar --script commands.txt

#   Структура tar
#
#   tarfile.tar
#   ├── file1.txt
#   ├── file2.txt
#   └── subfolder/
#    ├── file3.txt
#    └── file4.txt

# Комманды в commands.txt
# ls
# cat file1.txt
# cd subfolder
# ls
# cat file4.txt
# cd ..
# ls
# cat subfolder/file3.txt
# cat file2.txt