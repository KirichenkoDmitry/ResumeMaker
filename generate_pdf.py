from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Регистрация шрифтов
pdfmetrics.registerFont(TTFont("DejaVuSerif-Bold", "DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSerif", "DejaVuSerif.ttf"))

def create_pdf_with_photo(user_data):
    pdf_path = f"user_pdfs/{user_data['fio']}_resume.pdf"
    os.makedirs("user_pdfs", exist_ok=True)  # Создаём папку, если её нет

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Добавляем фото, если оно есть
    photo_height = 150
    photo_width = 110
    if "photo_path" in user_data:
        img = ImageReader(user_data["photo_path"])
        c.drawImage(img, 40, height - 42 - photo_height, photo_width, photo_height)  # Фото слева сверху

    # Добавляем текст
    text_x = 160  # Отступ от фото
    text_y = height - 50  # Начальная позиция текста
    line_spacing = 20

    # Блок с основными данными
    def draw_key_value(key, value, y_position):
        # Жирный ключ
        c.setFont("DejaVuSerif-Bold", 12)
        c.drawString(text_x, y_position, key)
        # Обычное значение
        c.setFont("DejaVuSerif", 12)
        c.drawString(text_x + c.stringWidth(key, "DejaVuSerif-Bold", 12) + 5, y_position, value)

    draw_key_value("ФИО:", user_data['fio'], text_y)
    draw_key_value("Дата рождения:", user_data['birth_date'], text_y - line_spacing)
    draw_key_value("Профессия:", user_data['profession'], text_y - 2 * line_spacing)
    draw_key_value("Опыт работы:", f"{user_data['experience']} лет", text_y - 3 * line_spacing)

    # Определяем начальную позицию для раздела "О себе" ниже всех данных и фото
    about_section_y = height - 80 - photo_height   # Отступ ниже фото
    if about_section_y < 100:
        about_section_y = 100  # Минимальная позиция, чтобы текст не выходил за границы

    # Заголовок "О себе"
    c.setFont("DejaVuSerif-Bold", 12)
    c.drawString(40, about_section_y, "О себе:")

    # Текст "О себе" - меняем шрифт
    c.setFont("DejaVuSerif", 12)
    about_text = (
        "Являюсь профессионалом в своей сфере с высоким уровнем ответственности и "
        "способностью быстро адаптироваться к новым условиям. Обладаю навыками "
        "эффективной коммуникации, решения сложных задач и работы в команде. "
        "Стремлюсь к профессиональному росту и готов к освоению новых знаний и технологий."
    )

    # Разделяем текст "О себе" на строки вручную для текущего шрифта
    max_line_width = width - 80
    words = about_text.split()
    lines = []
    current_line = ""

    for word in words:
        if c.stringWidth(f"{current_line} {word}", "DejaVuSerif", 12) < max_line_width:
            current_line = f"{current_line} {word}".strip()
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Рисуем строки текста "О себе"
    for i, line in enumerate(lines):
        c.drawString(40, about_section_y - (i + 1) * line_spacing, line)

    c.save()
    return pdf_path
