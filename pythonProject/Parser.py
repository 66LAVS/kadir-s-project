import PyPDF2
import sqlite3

def extract_text_from_pdf(pdf_file_path, output_file_path):
    """
  Извлекает текст из PDF-файла и сохраняет его в текстовый файл.

  Args:
    pdf_file_path: Путь к PDF-файлу.
    output_file_path: Путь к выходному текстовому файлу.
  """

    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        extracted_text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
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


def create_database(db_name):
    """
  Создает базу данных SQLite.

  Args:
    db_name: Имя базы данных.
  """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Создание таблицы
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      file_number INTEGER,
      udk TEXT,
      content TEXT
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

        # Удаление лишних пробелов и символов в начале текста после УДК
        content = part[len(udk):].strip().lstrip('0123456789').strip()  # Остальной текст - это содержание

        cursor.execute("INSERT INTO documents (file_number, udk, content) VALUES (?, ?, ?)",
                       (file_number, udk, content))

    conn.commit()
    conn.close()


n = 2  # число файлов в папке Parsing units
i = 1
while i <= n:  # создание файлов в папку Parsing units text через функцию

    pdf_file_path = fr'Parsing units/{i}.pdf'
    output_file_path = fr'parsing units text/{i}extracted_text.txt'  # Замените на имя желаемого выходного файла
    extract_text_from_pdf(pdf_file_path, output_file_path)

    file_path = fr'Parsing units text/{i}extracted_text.txt'



    # Создание базы данных
    create_database('documents.db')

    # Заполнение базы данных
    populate_database('documents.db', file_path)

    i += 1
