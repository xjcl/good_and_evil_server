
# good_and_evil_server

Python Django webapp for generating images in the style of Tally Halls's "Good & Evil" album cover!

Usage is `/<hex_color>,<str1>,<str2>,<font_size>` with font_size being optional (default 70). Examples:

| `/000000,TALLY,HALL`            | `/ff0000,GOOD,EVIL`            | `/4B8BBE,PYTHON,DOCKER,54`            |
| ------------------------------- | ------------------------------ | ------------------------------------- |
| ![](demo_000000,TALLY,HALL.png) | ![](demo_ff0000,GOOD,EVIL.png) | ![](demo_4B8BBE,PYTHON,DOCKER,54.png) |

Running live instance currently available [here](http://167.172.140.13:8000/000000,GOOD,EVIL) (link might die soon).

The ususal `sudo docker-compose up` is enough to run it.
