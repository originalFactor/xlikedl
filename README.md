# <center> Twitter-Like-Downloader </center>

Simply save X(Twitter) liked contents (include media and text).

## Usage

### Getting started

Here's an example for debian. Other systems are similar.

```sh
# make sure you have python3 and pip3 installed
sudo apt install python3 python3-pip -y
# then, install poetry
pip3 install poetry
# and, intall the project dependencies
poetry install
# activate the virtual environment
poetry shell
# run the project
python mainv2.py
```

Then you may be asked to fill your cookies in `cookies.txt`.

Follow these steps and restart the project:

### How to get cookies

First, open your web browser and log in x.com.

Second, open developer tools (On most browsers, right click and choose "Check") and navigate to the network page.

Third, refresh the web page to catch the XHR requests.

Forth, select a xhr request and navigate to its request header.

Fifth, copy its `cookies` header value and paste them in `cookies.txt`.

Reminder: Do not include `cookies: `.

### Result

You must keep it running until it automatic breaked since it's multiprocessing and async.

Finally there will be a `data` directory storaged your liked tweets.

For each tweet, a `data/<rest_id>` folder will storage its content.

First, publisher id and name, text content and hashtags will be storaged in `metadata.json`.

Then, for each media, it will be storaged as `<index>.<format>`.
`format` ususally be png and mp4.
(For video media, a mp4 and a preview png will be storaged both.)

