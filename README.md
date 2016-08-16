Pocket CLI
==========

Pocket-CLI is an application for reading / listing and managing your GetPocket.com articles from the terminal.

Note: This app is based on my [Pocket-API](https://github.com/rakanalh/pocket-api) package.

Features
--------

* Retrieves and indexes all of your articles and saves them into a CSV file in your home directory for quicker response.
* Enables you to specify your reading speed to calculate the amount of time each article requires. You can estimate your reading speed from online tests such as [Speed Reading Online Test](http://www.readingsoft.com/)
* Able to sort articles by reading time (default) and Article ID
* Enables you to search articles by keywords, tags and sort by [GetPocket's sorting params](https://getpocket.com/developer/docs/v3/retrieve). This will perform a request to Pocket.
* Automated app configuration through `pocket-cli configure` command.
* Uses LESS to list article for easy navigation.
* Multiple `fetch` command calls will retrieve articles since last fetch.


Note: This application has been tested on Python 2.7.10 and 3.5.0.

Installation
------------

    pip install pocket-cli

Configuration
-------------

 If you already have a Pocket API consumer key, skip to step 2.

 1. Generate a Pocket API consumer key at https://getpocket.com/developer/apps/new. Here's an example:

 ![](/docs/create_consumer_key.png?raw=true)

 2. Run `pocket-cli configure` and enter the consumer key generated in step 1 when prompted.
 3. Next, you will be prompted for a sort order and your estimated reading speed. You may visit http://www.readingsoft.com/ to estimate your reading speed.
 4. After you have finished selecting configurations for `pocket-cli`, a browser window will open requesting access to your Pocket account. Log in to Pocket (if you are not already logged in) and click **Authorize** to accept and complete the configuration of `pocket-cli`.


Usage
-----

    Usage: pocket-cli [OPTIONS] COMMAND [ARGS]...

    Options:
        --help  Show this message and exit.

    Commands:
        add
        archive
        configure
        fetch
        list
        random
        read
        search


Commands
--------

To configure the app (for first time use)

    pocket-cli configure

To add a new article URL with additional params.

    pocket-cli add --url <URL> --title <title> --tags <tag1> --tags <tag2>


Mark a specific article as read.

    pocket-cli archive <ID>


To fetch all articles / or articles added since last fetch

    pocket-cli fetch

To list your articles

    pocket-cli list --limit 10 --order [asc|desc]

To select a random article for you to read

    pocket-cli random --archive --browser

    --archive will mark this article as read
    --browser will open the article in your default browser

To read an article

    pocket-cli random --open-origin --archive

    --archive will mark this article as read
    --open-origin will open the article's original URL rather than Pocket's.

To search for specific articles

    pocket-cli --state [unread|archive|all] --sort [newest|oldest|title|site] --tag <search_by_tag> <Search Term>


Cronjob
-------

You can add `/path/to/pocket-cli fetch` to your crontab to let the app fetch new articles every once and a while. For example, to fetch every 3 hours, execute crontab -e and add the following line:

    * */3 * * * /usr/local/bin/pocket-cli fetch

Contribution
------------

Contributions are welcome! Fork the repository, create a branch, implement your changes and create a pull request and i'll be happy to review and merge your features / changes.

License
-------

The MIT License (MIT)

Copyright (c) 2016 Rakan Alhneiti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
