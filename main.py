# main.py for debug

# in terminal, use "scrapy crawl <crawlName(here is jobbole)>" to start crawler proj.
# here we can use "execute(["scrapy", "crawl", "<crawlName>"])" to call the terminal to run the same command.

from scrapy.cmdline import execute
import sys
import os

# add current folder into sysPath. so that project can be called from terminal.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole"])