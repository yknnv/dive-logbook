# Задание на элементы схем

Не иллюстрации на страницу, а **детали конструктора**: отдельные фигуры,
из которых вёрстка сама собирает схемы. Шкалы глубин, стрелки, подписи
и сетку рисует код — от вас нужны только сами объекты.

Отсюда главное требование, которого нет в обычных заданиях.

---

## 1. Каноническая ориентация — жёсткое требование

**Каждый элемент рисуется в указанном ракурсе строго, без наклона
и без перспективы.** Повороты и расстановку делает вёрстка.

Если фигура приедет нарисованной «под углом», код не сможет поставить
её точно: он не знает, сколько градусов уже заложено в картинку.

---

## 2. Стиль

Тот же, что у принятой серии `d-01` … `d-12`. Префикс к каждому промпту:

```
Editorial line illustration for a printed pocket field manual. Clean confident
ink linework, flat grey fills, minimal detail. Pure white background. Strictly
monochrome: black ink and neutral greys only, absolutely no colour of any kind.
No gradients, no photorealism, no 3D render, no dramatic shadows. Even flat
lighting. Absolutely no text, letters, numbers, labels, watermark or signature
anywhere in the image.
```

Дополнительно для элементов:

```
Single isolated object centred in the frame, nothing else in the picture. Plain
white background with no ground plane, no shadow, no horizon, no water texture,
no bubbles, no reef, no border. Flat orthographic view, no perspective, no tilt.
```

---

## 3. Технические требования

- PNG, от **1200 px по длинной стороне**
- фон строго белый и сплошной, без подложки и виньетки
- объект не касается краёв кадра, поле вокруг 5–10 % ширины
- строго монохром, никакого текста
- **одинаковая толщина обводки во всех трёх файлах** — см. раздел 6

Прозрачность делать не нужно: белый фон выбивается автоматически
командой `python3 tools/prepare_illustrations.py --elements`.

---

## 4. Список

### e-diver-top · дайвер сверху — 1:1

```
Top-down orthographic view of a scuba diver seen from directly above, looking
straight down onto the back of the cylinder and the top of the head. Body
horizontal and level, arms slightly out to the sides, legs straight with fins
spread apart. Head towards the top of the frame. Clean ink outline, flat grey
fills on wetsuit and cylinder, no perspective, no tilt.
```

Приёмка: строго вид сверху, а не сбоку и не в три четверти; голова к
верху кадра; силуэт симметричен относительно вертикали.

Ставится в центр схемы осмотра на 360°, вместо нынешней точки.

---

### e-diver-ascending · дайвер на всплытии — 2:3

```
Side elevation of a scuba diver ascending, seen from directly abeam. Body
upright and vertical, one arm raised straight above the head, the other holding
the inflator hose at chest level, head tilted to look upward, fins together and
pointing down. Facing to the right. Clean ink outline, flat grey fills on
wetsuit and cylinder, no perspective, no bubbles, no background.
```

Приёмка: корпус строго вертикальный; рука вытянута прямо вверх, а не
в сторону; взгляд вверх.

---

### e-smb · буй — 1:4

```
An inflated surface marker buoy standing upright, seen from directly abeam.
A tall slim sausage shape with a rounded closed top and an open flat bottom,
noticeably taller than wide. A short thin line hangs from the bottom. Clean ink
outline, flat light grey fill, strictly vertical, no perspective, no water,
no diver, no background.
```

Приёмка: строго вертикальный, верх скруглён, низ открыт; пропорция
вытянутая, не бочонок.

---

## 5. Именование и сдача

Имя файла — ровно ID из задания, префикс `e-`. Архив
`elements/<ID>.png`. Каждый элемент отдельным файлом, не склеивать
в общий лист.

---

## 6. Главный риск партии

**Толщина обводки гуляет между отрисовками.** Каждый файл — отдельный
запуск генератора, и линия приходит то тоньше, то жирнее. Дайверы стоят
на соседних панелях одной схемы, разнобой виден сразу.

Сгенерируйте по три-четыре кандидата на элемент и отберите
**согласованный комплект**, а не лучший файл по отдельности. Починить
это после вставки в вёрстку нельзя.

Второе по частоте — разное снаряжение: оба дайвера должны быть одним
и тем же человеком в одном комплекте, а не двумя разными.

---

## 7. Как элементы попадают в книгу

```bash
python3 tools/prepare_illustrations.py --elements elements/ mapping.txt
./build.sh
```

`--elements` обрезает поля и выбивает белый фон в прозрачность заливкой
от края кадра — белое внутри силуэта остаётся белым, и разметка схемы
не просвечивает сквозь фигуру.

`e-diver-top` схема потери напарника подхватит сама. Остальные два
элемента пока не подключены: скажите, когда файлы будут готовы, —
`fig_ascent` и третья панель переводятся на них одной правкой.

Пока файлов нет, схемы рисуются как сейчас: сборка не ломается
на полпути.
