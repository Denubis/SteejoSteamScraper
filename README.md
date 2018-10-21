# SteejoSteamScraper

```
Steejo: What I ideally would like
[3:23 AM] Steejo: is the ability to specify a date
[3:24 AM] Steejo: and download all the trailers of the new games from that date into a folder
[3:24 AM] Steejo: and in that folder also have a txt file that has [Gamename] : [Steam Store Link]
[3:25 AM] Steejo: the text file would have each game on a separate line
```

Main link: `https://store.steampowered.com/news/posts/?feed=steam_release&enddate=1534654564`


To invoke for releases 2 days ago:

~~~
scrapy crawl steamNewReleases -a targetdate="2 days ago"
~~~