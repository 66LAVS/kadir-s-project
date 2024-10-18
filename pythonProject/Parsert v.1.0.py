import PyPDF2

def extract_text_from_pdf(pdf_file_path, output_file_path):
  """
  Извлекает текст из PDF-файла и сохраняет его в текстовый файл.

  Args:pip install PyPDF2
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
    parts = text.split("УДК ") # Разделение по "УДК "
    return parts

n = 2 # число файлов в папке Parsing units
i = 1
while i <= n: # создание файлов в папку Parsing units text через функцию

  pdf_file_path = fr'Parsing units/{i}.pdf'
  output_file_path = fr'parsing units text/{i}extracted_text.txt'  # Замените на имя желаемого выходного файла
  extract_text_from_pdf(pdf_file_path, output_file_path)

  file_path = fr'Parsing units text/{i}extracted_text.txt'
  parts = split_text_by_udk(file_path)

# Вывод результата

  print("^^^" * 20)#начало нового файла
  print(f'Файл номер {i}')

  for z, part in enumerate(parts):
    print(f"Часть {z+1}:")
    print(part)
    print("-" * 20)

    z += z;

  i += i
