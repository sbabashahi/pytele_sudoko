This is telegram bot which can help you solve a sudoko. It can help solving puzzel completely or eaither as a hint just show part of solved puzzel like a row or column.
All you need is to pass an image of the sudoko you want to be solved.

You need to add `BOT_TOKEN` to the env, you can generate one for your self using [telegram botfather](https://core.telegram.org/bots/tutorial).

To extract the sudoko from the image this project is using [pytesseract](https://pypi.org/project/pytesseract/)

![Extracting the sudoko from image](https://github.com/sbabashahi/pytele_sudoko/blob/main/output-48dc.gif)

to reduce repatative solving the puzzel, the solution would be saved on redis.
