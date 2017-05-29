### overview
*feed_list.json* contains a list of RSS and Atom feeds which the script parses and downloads the found images in the tags and some relevant metadata. The metadata, list of feeds and the path to the images are then stored in MongoDB.
*scheduler.py* schedules an automatic run of the script in the background

### packages
  - [feedparser](https://github.com/kurtmckee/feedparser)
  - [pymongo](https://api.mongodb.com/python/current/)
  - [urllib3](https://urllib3.readthedocs.io/en/latest/)
  - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
  - [schedule](https://schedule.readthedocs.io/en/stable/)

### usage
  run the script in every *k* minutes

  `python3 scheduler.py k`

  or

  `nohup /usr/bin/python3 scheduler.py k &`
