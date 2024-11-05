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


def populate_database(db_name, file_path):
    """
    Заполняет базу данных данными из текстового файла.

    Args:
      db_name: Имя базы данных.
      file_path: Путь к текстовому файлу.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    parts = split_text_by_udk(file_path)
    file_number = int(file_path.split('/')[-1].split('extracted_text')[0])  # Получение номера файла

    for z, part in enumerate(parts):
        udk = part.split('\n')[0].strip()  # Получение УДК из первой строки

        # Извлечение ключевых слов из текста
        keywords = extract_keywords(part)

        # Удаление лишних пробелов и символов в начале текста после УДК
        content = part[len(udk):].strip().lstrip('0123456789').strip()  # Остальной текст - это содержание

        # Удаляем часть текста после "Литература"
        content = remove_literature_and_after(content)

        cursor.execute("INSERT INTO documents (file_number, udk, content, keywords) VALUES (?, ?, ?, ?)",
                       (file_number, udk, content, keywords))

    conn.commit()
    conn.close()


n = 2  # Число файлов в папке Parsing units
i = 1
while i <= n:  # Создание файлов в папку Parsing units text через функцию

    pdf_file_path = fr'Parsing units/{i}.pdf'
    output_file_path = fr'parsing units text/{i}extracted_text.txt'  # Замените на имя желаемого выходного файла
    extract_text_from_pdf(pdf_file_path, output_file_path)

    file_path = fr'parsing units text/{i}extracted_text.txt'

    # Проверим, что текст был извлечен
    if os.path.exists(file_path):
        print(f"Текст из файла {pdf_file_path} успешно извлечен в {output_file_path}")
    else:
        print(f"Ошибка при извлечении текста из {pdf_file_path}")

    # Создание базы данных
    create_database('documents.db')

    # Заполнение базы данных
    populate_database('documents.db', file_path)

    i += 1
