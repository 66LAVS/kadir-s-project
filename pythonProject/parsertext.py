import pdfplumber
import sqlite3
import os


def extract_text_from_pdf(pdf_file_path, output_file_path):
    """
    Извлекает текст из PDF-файла и сохраняет его в текстовый файл.

    Args:
      pdf_file_path: Путь к PDF-файлу.
      output_file_path: Путь к выходному текстовому файлу.
    """
    with pdfplumber.open(pdf_file_path) as pdf:
        extracted_text = ""
        for page in pdf.pages:
            extracted_text += page.extract_text()

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(extracted_text)


def split_text_by_udk(file_path):
    """
    Делит текстовый файл на массив, разделяя по строке "УДК ".

    Args:
      file_path: Путь к текстовому файлу.

    Returns:
      Список строк, разделенных по "УДК ".
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
        parts = text.split("УДК ")  # Разделение по "УДК "
    return parts


def extract_keywords(text):
    """
    Извлекает ключевые слова из текста. Ключевые слова идут после строки "Ключевые слова:", до точки.

    Args:
      text: Весь текст, из которого нужно извлечь ключевые слова.

    Returns:
      Строка с ключевыми словами или None, если ключевых слов нет.
    """
    start_index = text.find("Ключевые слова:")
    if start_index != -1:
        # Извлекаем текст после "Ключевые слова:" до точки
        keywords_text = text[start_index + len("Ключевые слова:"):].split('.')[0].strip()
        return keywords_text
    return None


def remove_literature_and_after(text):
    """
    Удаляет все, что идет после слова "Литература" (включая само слово).

    Args:
      text: Текст, из которого нужно удалить литературу.

    Returns:
      Обрезанный текст без части, начинающейся с "Литература".
    """
    literature_index = text.lower().find("литература")  # Ищем слово "литература" (нечувствительный к регистру)
    if literature_index != -1:
        return text[:literature_index].strip()  # Возвращаем текст до "Литература"
    return text


def remove_keywords_and_before(text):
    """
    Удаляет все, что идет до строки с ключевыми словами и сами ключевые слова.

    Args:
      text: Текст, из которого нужно удалить все до ключевых слов.

    Returns:
      Обрезанный текст, начиная с ключевых слов.
    """
    keywords = extract_keywords(text)  # Извлекаем ключевые слова
    if keywords:
        # Находим ключевые слова в тексте и обрезаем всё до них и сами ключевые слова
        start_index = text.find(keywords)
        if start_index != -1:
            return text[start_index + len(keywords):].strip()  # Возвращаем текст после ключевых слов
    return text


def create_database(db_name):
    """
    Создает базу данных SQLite.

    Args:
      db_name: Имя базы данных.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Создание таблицы с дополнительной колонкой для ключевых слов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      file_number INTEGER,
      udk TEXT,
      content TEXT,
      keywords TEXT
    )
    """)

    conn.commit()
    conn.close()


def populate_database(db_name, file_path, file_number):
    """
    Заполняет базу данных данными из текстового файла.

    Args:
      db_name: Имя базы данных.
      file_path: Путь к текстовому файлу.
      file_number: Уникальный номер для файла.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    parts = split_text_by_udk(file_path)

    for z, part in enumerate(parts):
        udk = part.split('\n')[0].strip()  # Получение УДК из первой строки

        # Извлечение ключевых слов из текста
        keywords = extract_keywords(part)

        # Удаление лишних пробелов и символов в начале текста после УДК
        content = part[len(udk):].strip().lstrip('0123456789').strip()  # Остальной текст - это содержание

        # Удаляем часть текста после "Литература" и до ключевых слов (если они есть)
        content = remove_literature_and_after(content)  # Убираем литературу
        content = remove_keywords_and_before(content)  # Убираем все до ключевых слов

        cursor.execute("INSERT INTO documents (file_number, udk, content, keywords) VALUES (?, ?, ?, ?)",
                       (file_number, udk, content, keywords))

    conn.commit()
    conn.close()


def process_pdfs_in_folder(pdf_folder, output_folder):
    """
    Обрабатывает все PDF-файлы в указанной папке, извлекает текст и заполняет базу данных.

    Args:
      pdf_folder: Папка, содержащая PDF-файлы.
      output_folder: Папка для сохранения извлеченных текстовых файлов.
    """
    # Получаем список всех файлов с расширением .pdf в указанной папке
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]

    for i, pdf_file in enumerate(pdf_files, start=1):  # Используем enumerate для получения индекса
        pdf_file_path = os.path.join(pdf_folder, pdf_file)

        # Формируем путь для текстового файла с тем же именем, что и у PDF, но с расширением .txt
        output_file_path = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}_extracted_text.txt")

        # Извлекаем текст из PDF
        extract_text_from_pdf(pdf_file_path, output_file_path)

        # Проверяем, что текст был извлечен
        if os.path.exists(output_file_path):
            print(f"Текст из файла {pdf_file_path} успешно извлечен в {output_file_path}")
        else:
            print(f"Ошибка при извлечении текста из {pdf_file_path}")

        # Заполняем базу данных, передавая уникальный file_number
        populate_database('documents.db', output_file_path, i)  # i - уникальный номер для каждого файла


# Укажите путь к папке с PDF-файлами
pdf_folder = '/workspaces/kadir-s-project/pythonProject/Parsing units'
output_folder = '/workspaces/kadir-s-project/pythonProject/Parsing units text'

# Создание базы данных
create_database('documents.db')

# Обработка всех PDF-файлов в папке
process_pdfs_in_folder(pdf_folder, output_folder)