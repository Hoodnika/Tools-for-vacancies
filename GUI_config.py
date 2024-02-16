from tkinter import *
from config import HH, JSONSaver, DBManager

temporary_labels = []


def combine_funcs(*funcs):
    """
    функция для комбинирования функций
    :param funcs:
    :return:
    """

    def inner_combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)

    return inner_combined_func()


def clicked_choose_company(company):
    """
    добавление в файл компании по клику кнопки в функции clicked_auto_search
    :param company:
    :return:
    """
    JSONSaver.add_company(company)


def clicked_next_page_search():
    """
    перейти по клику кнопки next_button на следующую страницу в get запросе поиска работадателей
    Изначально стоит 10 страница
    :return:
    """
    HH.employer_page += 1
    clicked_auto_search()


def clicked_auto_search():
    """
    по клику стартовой кнопки btn_auto_search выполняет get запрос по API для получения списка работадалей
    циклом создает фреймы и кнопки для выбора компании (добавления в файл COMPANIES.json)
    каждый элемент интерфеса добавлет в список temporary_labels, для последующей очитски с экрана
    :return:
    """
    buttons_auto_search = []
    button_count = 0
    column = 1
    row = 2
    companies = HH.employers_to_lstdir()
    for company in companies:
        frame_auto_search = LabelFrame(window, text=f'{company["Company_name"][0:20]}\n'
                                                    f'Открытых вакансий - {company["Open_vacancies"]}',
                                       font=('Arial Bold', 10))
        temporary_labels.append(frame_auto_search)
        frame_auto_search.grid(column=column, row=row)
        new_button = Button(frame_auto_search, text='Выбрать',
                            command=lambda company_l=company: [clicked_choose_company(company_l)])
        buttons_auto_search.append(new_button)
        temporary_labels.append(new_button)
        buttons_auto_search[button_count].grid(column=column, row=row + 1)
        button_count += 1

        column += 1
        if column > 4:
            column = 1
            row += 1

    next_button = Button(window, text='Следующая страница', command=clicked_next_page_search)
    next_button.grid(column=4, row=row)
    temporary_labels.append(next_button)


def clicked_confirm_searching(user_search):
    """
    По клику кнопки button_user_search из функции clicked_btn_user_search  добавляет компанию, которую ввел пользователь
    ,в зависимости от положительного или отрицательного результата поиска
    выводит label в соответствующим текстом
    :param user_search:
    :return:
    """
    company = HH.search_company(user_search)
    result_label = Label(window, font=('Arial Bold', 15))
    result_label.grid(column=1, row=4)
    temporary_labels.append(result_label)

    if company is None:
        result_label.config(text=' Такой компании нет на HH.ru ')
        result_label.update()
        pass
    elif company != 'Такой компании нет на HH.ru':
        if int(company['Open_vacancies']) < 1:
            result_label.config(text='У компании закрыты вакансии')
            result_label.update()
        else:
            JSONSaver.add_company(company)
            result_label.config(text='Компания успешно добавлено')
            result_label.update()
    elif company == 'Такой компании нет на HH.ru':
        result_label.config(text=' Такой компании нет на HH.ru ')
        result_label.update()


def clicked_btn_user_search():
    """
    По клику стратовой кнопки btn_user_search выводит поле для ввода,
    в котором пользователь ищет интересующую его компанию
    :return:
    """
    user_search = Entry(window, font=('Arial Bold', 20))
    user_search.grid(column=1, row=2)

    button_user_search = Button(window, text='Найти', command=lambda: [clicked_confirm_searching(user_search.get())])
    button_user_search.grid(column=1, row=3)

    temporary_labels.append(user_search)
    temporary_labels.append(button_user_search)


def clear_frame():
    """
    чистка всех временных, не стартовых фреймов
    :return:
    """
    for label in temporary_labels:
        label.destroy()


def destroy_label(labels, i):
    """
    функция для коррекной работы функции clicked_show_chosen_companies,
    когда пользователь удаляет компанию из выбранного списка компании
    :param labels:
    :param i:
    :return:
    """
    labels[i - 1].destroy()
    labels[i].destroy()


def clicked_show_chosen_companies():
    """
    По клику стартовой кнопки btn_favorite_companies, выводит список выбранных пользователем компаний из
    файлка COMPANIES.json
    циклом создает фреймы и кнопки для удаления компании (удаление из файла COMPANIES.json)
    каждый элемент интерфеса добавлет в список temporary_labels, для последующей очитски с экрана
    :return:
    """
    chosen_labels = []
    buttons_auto_search = []
    button_count = 0
    column = 1
    row = 2
    companies = JSONSaver.load_file()
    for company in companies:
        frame_auto_search = LabelFrame(window, text=f'{company["Company_name"][0:20]}\n'
                                                    f'Открытых вакансий - {company["Open_vacancies"]}',
                                       font=('Arial Bold', 10))
        temporary_labels.append(frame_auto_search)
        chosen_labels.append(frame_auto_search)
        frame_auto_search.grid(column=column, row=row)

        new_button = Button(frame_auto_search, text='Удалить',
                            command=lambda company_l=company, new_button_l=len(chosen_labels):
                            [destroy_label(chosen_labels, new_button_l), JSONSaver.remove_company(company_l)])
        buttons_auto_search.append(new_button)
        temporary_labels.append(new_button)
        chosen_labels.append(new_button)
        buttons_auto_search[button_count].grid(column=column, row=row + 1)
        button_count += 1
        column += 1

        if column > 4:
            column = 1
            row += 1


def clicked_tools_for_sql():
    """
    Создает базу данных, если такая существует, идет дальше
    Создает таблицы и зависимости, если таковые имеются, идет дальше
    Загружает вакансии из компаний файла COMPANIES.json в базу данных
    для дальнейшей работы с этой базой данных

    :return: Результаты работы с базой данных будут выводится в консоль
    """
    DBManager.create_database()
    DBManager.create_tables()
    DBManager.load_vacancies_to_database()

    btn_sql_get_companies_count = Button(window, text='Получить список компаний и их количество',
                                         command=DBManager.get_companies_and_vacancies_count)
    btn_sql_get_companies_count.grid(column=1, row=2)
    temporary_labels.append(btn_sql_get_companies_count)

    btn_sql_get_all_vacancies = Button(window, text='Получить все вакансии',
                                       command=DBManager.get_all_vacancies)
    btn_sql_get_all_vacancies.grid(column=2, row=2)
    temporary_labels.append(btn_sql_get_all_vacancies)

    btn_sql_get_avg_salary = Button(window, text='Узнать среднюю зарплату по вакансиям',
                                    command=DBManager.get_avg_salary)
    btn_sql_get_avg_salary.grid(column=3, row=2)
    temporary_labels.append(btn_sql_get_avg_salary)

    btn_sql_higher_salary = Button(window, text='Лучшие предложения по зарплате',
                                   command=DBManager.get_vacancies_with_higher_salary)
    btn_sql_higher_salary.grid(column=4, row=2)
    temporary_labels.append(btn_sql_higher_salary)

    frame_keyword = LabelFrame(window,
                               text=f'Получить список всех вакансий,\n в названии которых содержатся \nпереданные в метод слова',
                               font=('Arial Bold', 10))
    frame_keyword.grid(column=1, row=3)
    temporary_labels.append(frame_keyword)
    search_keyword = Entry(frame_keyword, font=('Arial Bold', 10))
    search_keyword.grid(column=1, row=4)
    temporary_labels.append(search_keyword)
    btn_sql_keyword = Button(window, text='Найти',
                             command=lambda: [DBManager.get_vacancies_with_keyword(search_keyword.get())])
    btn_sql_keyword.grid(column=1, row=5)
    temporary_labels.append(btn_sql_keyword)


JSONSaver.clear_file()
window = Tk()

# STAR WINDOW

window['bg'] = '#fafafa'
window.title('Tools for vacancies')
window.wm_attributes('-alpha', 0.7)
window.geometry('1500x500')
window.resizable(width=False, height=False)

# START BUTTONS

btn_auto_search = Button(window, text='Выбрать компании из списка',
                         command=lambda: [clear_frame(), clicked_auto_search()], bg='deep sky blue')
btn_auto_search.grid(column=1, row=1)

btn_user_search = Button(window, text='Найти компанию по ее названию',
                         command=lambda: [clear_frame(), clicked_btn_user_search()],
                         bg='deep sky blue')
btn_user_search.grid(column=2, row=1)

btn_favorite_companies = Button(window, text='Посмотреть выбранные вами компании',
                                command=lambda: [clear_frame(), clicked_show_chosen_companies()], bg='deep sky blue')
btn_favorite_companies.grid(column=3, row=1)

btn_sql_loader = Button(window, text='Загрузить вакансии в базу данных',
                        command=lambda: [clear_frame(), clicked_tools_for_sql()], bg='deep sky blue')
btn_sql_loader.grid(column=4, row=1)

btn_sql_delete_data = Button(window, text='Удалить данные из базы данных',
                             command=DBManager.delete_tables, bg='red')
btn_sql_delete_data.grid(column=5, row=1)
