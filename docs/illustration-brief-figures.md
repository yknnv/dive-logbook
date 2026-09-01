# Задание на иллюстрации: замена векторных схем

Задание на перерисовку схем из `src/figures.py` растровыми иллюстрациями.
Самодостаточно: внешних файлов открывать не нужно. Приложите к заданию
два-три принятых PNG из `assets/images` как визуальный референс.

**Прочтите раздел «Что стоит и чего не стоит заменять» до того, как
запускать генерацию.** Часть схем несёт измеримую геометрию, и картинка
вместо них ухудшит справочник, а не улучшит.

---

## 1. Стиль

Редакционная штриховая иллюстрация, как в полевом руководстве. Уверенная
чёрная линия, плоские серые заливки, минимум деталей. Не фотореализм,
не 3D-рендер, без градиентов и драматических теней.

Префикс подставляется к каждому промпту ниже:

```
Editorial line illustration for a printed pocket field manual. Clean confident
ink linework, flat grey fills, minimal detail. Pure white background. Strictly
monochrome: black ink and neutral greys only, absolutely no colour of any kind.
No gradients, no photorealism, no 3D render, no dramatic shadows. Even flat
lighting. Centred composition with generous white margin. Absolutely no text,
letters, numbers, labels, watermark or signature anywhere in the image.
```

## 2. Технические требования

- PNG, sRGB, от 2048 px по длинной стороне
- фон строго белый, не серая плашка
- никакого текста в кадре: подписи наносятся в вёрстке
- строго монохром: книга печатается одной краской
- соотношение сторон ровно указанное
- без логотипов брендов и узнаваемых реальных людей

## 3. Именование и сдача

Имя файла — ровно ID из задания. Архив со структурой
`illustrations/<ID>.png`. ID начинаются с `d-f`, чтобы не пересекаться
с принятыми сериями `d-01` … `d-12` и `d-s1` … `d-s8`.

---

## 4. Что стоит и чего не стоит заменять

Схемы делятся на три группы. Группа указана у каждой позиции.

**«Можно»** — сюжет и пропорции не несут измеримой информации. Картинка
заменяет схему целиком.

**«Фон»** — картинка даёт обстановку и читаемость, но числа, оси, глубины
и подписи остаются вектором поверх неё. Порядок: `img()` рисует фон,
следом функция `fig_*` дорисовывает измеримый слой.

**«Не рекомендую»** — вся информация схемы и есть график. Генератор
ошибётся в пропорциях убедительно и незаметно: картинка будет выглядеть
аккуратной и врать. Промпт написан, решение за вами.

---

## 5. Список

### d-f01 · Всплытие: схема — 16:9 — фон

```
Side elevation underwater scene. A horizontal line near the top of the frame is
the water surface, with a small boat hull sitting on it at the upper left, seen
from the side. Below the surface, a scuba diver in full kit ascends on the right
side of the frame, body vertical and upright, one arm raised straight above the
head, face tilted up, fins together. A long straight vertical arrow on the left
half of the frame points upward towards the surface. Three faint horizontal
guide lines cross the frame at even intervals between the diver and the bottom
of the image. Clean ink linework, flat grey fills, no perspective distortion,
no fish, no reef, no bubbles clutter.
```

Приёмка: рука вытянута строго вверх, взгляд вверх; корпус вертикальный;
стрелка подъёма прямая, без изгиба.

Остаётся вектором: шкала глубин 5 / 10 / 15 / 20 м, отметка остановки
на пяти метрах, скорость 9 м/мин. **Числа и есть содержание схемы**, они
рисуются кодом поверх картинки.

---

### d-f02 · Потеря напарника: осмотр 360° — 1:1 — можно

```
Top-down bird's eye view of a single scuba diver seen from directly above,
centred in the frame, arms slightly out, fins spread. A dashed circle is drawn
around the diver. Eight short straight arrows point outward from the circle in
eight evenly spaced directions, like compass rays. Flat plan view, clean ink
linework, light grey fills, no perspective, no background, no water texture.
```

Приёмка: дайвер по центру, лучи расходятся равномерно во все стороны —
читается осмотр на месте, а не заплыв по сторонам.

---

### d-f03 · Потеря напарника: всплытие — 3:4 — можно

```
Side elevation. A horizontal line across the upper part of the frame is the
water surface. A single scuba diver ascends towards it from below, body upright
and vertical, one arm raised above the head. A long straight vertical arrow runs
from the lower part of the frame up to the surface line beside the diver. Nothing
else in the frame. Clean ink linework, flat grey fills, no perspective, no reef.
```

Приёмка: движение однозначно вверх, к линии поверхности; фигура одна.

---

### d-f04 · Потеря напарника: буй и ожидание — 3:4 — можно

```
Side elevation. A horizontal line across the lower third of the frame is the
water surface. An inflated surface marker buoy, a tall slim vertical sausage
shape with a rounded top, floats upright on that line, its lower part below the
surface. A thin line runs from the base of the buoy down out of frame. Nothing
else. Clean ink outline, flat light grey fill, no perspective, no waves, no
diver.
```

Приёмка: буй вертикальный, заметно выступает над линией воды.

---

### d-f05 · Давление наглядно — 16:9 — не рекомендую

```
Five circles in a horizontal row on a common centreline, evenly spaced,
decreasing in size from left to right. The leftmost is the largest; each
following circle is visibly smaller than the one before it, with the gaps between
sizes shrinking towards the right so the last two are close in size. Thin ink
outlines, flat light grey fill. Thin vertical separator lines between adjacent
circles. Nothing else in the frame. Flat front view, no perspective, no shading.
```

Приёмка: диаметры относятся как 1 : 1/2 : 1/3 : 1/4 : 1/5.

Остаётся вектором: **это отношение и есть вся схема.** Круги «на глаз»
превращают наглядную демонстрацию закона Бойля в декоративный ряд
кружков. Читатель по картинке оценивает, во сколько раз сожмётся воздух,
и ошибка здесь дороже отсутствия картинки.

---

### d-f06 · Расход газа: пример — 16:9 — не рекомендую

```
A simple line chart on a light grid. A single continuous line starts at the top
left corner, drops steeply down to a low level, runs perfectly flat and
horizontal across most of the width, then rises in two steps back towards the top
right, with a short flat landing between the steps. Thin ink line on a faint
grey grid of horizontal and vertical rules. No axes labels, no ticks, no numbers,
no markers. Flat front view.
```

Приёмка: ровный участок строго горизонтальный и занимает большую часть
ширины.

Остаётся вектором: оси, сетка, числа глубины и времени. По этому графику
читатель считает SAC: 50 бар за 20 минут на 20 метрах. Сдвинутая на глаз
полка ломает пример, ради которого страница и сделана.

---

### d-f07 · Как читать профиль — 16:9 — не рекомендую

```
A simple line chart on a light grid. A single continuous line starts at the top
left, drops steeply to the lowest level in the frame, runs flat and horizontal
for about half the width, then climbs back towards the top in two straight
segments of decreasing steepness, with a short flat landing near the top right
before reaching the top edge. A small solid dot marks that final landing. Thin
ink line on a faint grey grid. No axis labels, no ticks, no numbers. Flat front
view.
```

Приёмка: подъём ступенями с замедлением к поверхности; точка стоит
на последней полке.

Остаётся вектором: сетка, глубины, время, отметка остановки безопасности.
Страница учит читать профиль по числам — без точной сетки учить нечему.

---

## 6. Чего избегать

Ошибки, которые повторялись:

- имена файлов не совпадали с содержимым
- в кадр попадали английские или русские подписи
- фон приходил цветным или серым вместо белого
- несколько файлов дублировали один сюжет, которого не было в задании
- разрешение около 250 dpi вместо запрошенного

## 7. Приёмка партии

1. Прогнать через `tools/prepare_illustrations.py` — он обрежет поля
   и переведёт в серое.
2. Вставить блоком `("img", ("имя", высота_мм, "подпись"))`.
3. `./build.sh` и просмотр изменённых страниц глазами.
4. Для позиций «фон» — проверить, что векторный слой лёг поверх картинки
   и не разъехался с ней.
