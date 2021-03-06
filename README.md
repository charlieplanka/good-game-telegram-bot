# Telegram-бот для выдачи призов клиентам

[Открыть бот в Телеграме](http://t.me/GoodGamePrizesBot)

❕ Бот развернут на сервере Heroku. Если не пользоваться ботом в течение долгого времени, он «засыпает». Поэтому первый запрос может выполняться несколько секунд, пока бот «просыпается».

![](https://i.imgur.com/czE0F5w.png)  
Правила акции: если клиент пополнил игровой счёт в течение последних 24 часов на сумму более 250 рублей, он сможет получить один или несколько призов на выбор, в зависимости от размера внесённой суммы.
* Кнопка **Призы**: получить информацию о содеражании призов
* Кнопка **Как открыть коробку?**: инструкция по получению призов
* Кнопка **Открыть коробку**: получить приз

Вместо работы с реальным счётом клиента используется [готовый словарь](https://jsonbin.io/5f8daafdadfa7a7bbea58fad/2) с заданными суммами. Этот словарь бот получает через библиотеку **requests**. 
Каждый раз, когда клиент наживает кнопку **Открыть коробку**, из словаря случайным образом извлекается значение — сумма «пополнения» счёта. Значение используется для определения количества и типа призов.  
  
Если клиент получит приз и после этого нажмёт на кнопку **Открыть коробку** повторно, выведется сообщение о том, что приз уже получен. Если после этого *снова* нажать на кнопку, будет получена новая сумма из словаря, и клиент сможет опять получить приз.
