Программа с GUI интерфейсом(пока очень простым)(tkinter библиотека) 
Программа имеет инструментарий для работы с API от HH.ru 

Программа обрабатывает компании, добавляет все вакансии выбранной компании в отдельный файл
Имеется поле для самостоятельного поиска компании, и также можно выбрать из предоставленных компаний. Вся информация подтягивается по API
У вабранных компаний, вакансии добавляются в базу данных 𝘷𝘢𝘤𝘢𝘯𝘤𝘪𝘦𝘴𝘣𝘢𝘴𝘦. База данных и таблицы с зависимостями к ней создаеются сами, если таковые существуют то пропускает эти шаги
По данным из баззы данных существует 5 функций, для их обработки:

-Получает список всех компаний и количество вакансий у каждой компании
-Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию
-Получает среднюю зарплату по всем вакансиям
-Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
-Получает список всех вакансий, в названии которых содержатся переданные в метод слова
