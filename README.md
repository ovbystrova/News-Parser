# News-Parser
## Parser for life.ru; provladimir.ru; rbc.ru. For university project on News Headlines.

Запустить через консоль: **python  main.py _%Разметчик%_ _%Кол-во%_**

```python
$python main.py Быстрова 10
```

- Программа создает папку с датой запуска.

+ Парсер переходит на главную страницу из вышеперечисленных, собирает ссылки на новости.

- Далее парсер выкачивает каждую новость: заголовок и сама статья записываются в txt файлы, создается датафрейм с необходимой для разметки информации.

+ Вся полученная информация сохраняется в Exel. 

- length_count.py считает среднюю длину статей каждого источника в символах
