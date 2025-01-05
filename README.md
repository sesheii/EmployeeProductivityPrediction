## Встановлення
1.	Завантажити та встановити версію Python за [посиланням](https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe)
2.	Мати встановлений git на комп’ютері, в довільній директорії відкрити термінал чи командний рядок та написати команду
```
git clone https://github.com/sesheii/EmployeeProductivityPrediction.git
```
## Запуск
Перейти всередину отриманої папки, відкрити в ній термінал чи командний рядок, виконати наступні команди по порядку:

### Linux

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd epp
python manage.py runserver
```

### Windows

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cd epp
python manage.py runserver
```

В результаті виконання команд застосунок запущено, залишається останній крок, щоб побачити його графічний інтерфейс - в адресному полі браузера ввести адресу localhost:8000 . Після цього буде видно інтерфейс застосунку та можна одразу ж з ним взаємодіяти.
