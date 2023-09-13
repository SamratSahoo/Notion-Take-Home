
<h1 align="center">Notion Take Home Assessment</h1>

Hello! Thank you for taking some time to go through my Notion Take Home assessment. I've gone ahead and delineated the different parts of my project along with some other information below. Hope you enjoy!

<p align="center">
  <a href="#project-structure">Project Structure</a> &#xa0; | &#xa0;
  <a href="#setup">Setup</a> &#xa0; | &#xa0;
  <a href="#libraries">Libraries</a> &#xa0; | &#xa0;
  <a href="#sources">Sources</a> &#xa0; | &#xa0;
  <a href="#reflection">Reflection</a> &#xa0; | &#xa0;
  <a href="https://github.com/SamratSahoo" target="_blank">Author</a>
</p>
 
 
## Project Structure ##

This project comes with two major modules and aims to keep the codebase as declarative as possible.

**Major Modules:**
* **CSVProcessor Module:** As its name might suggest, this module was built for the sole purpose of processing the `data/ratings.csv` file. It is module specifically designed to parse the CSV file and gather any necessary information for our use case (i.e. average ratings or number of favorites). If the CSV file were to differ or the information we want to obtain differed, then the processor module would have a custom implementation. 
* **DatabaseClient Module:** This module is a wrapper module around the Python `notion-client` SDK. It abstracts away basic notion database functionality (i.e. creating a column or adding a row). There is a sister `DatabaseColumn` module that this module is designed to interface with.

**Project Structure:**
* **Entrypoint:** The core of this project's functionality can be invoked through the `main.py` file which will initialize the database client, CSV processor, and add columns + rows to the database.
* **Testing:** This project comes with a basic suite of tests (found in `tests/`), testing both the database client and the CSV processor. These tests can be invoked via the `tests.py` file.
* **Data:** The data for this project is kept in the `data/` directory. This project has both the notion provided data (`data/ratings.csv`) as well as a smaller subset of that data (`data/sample.csv`) for testing purposes.
* **Config:** As an attempt to keep the codebase as elegant as possible, it follows a declarative coding style. The `notion_types.py` and `config.py` provide some of the classes & config variables we parse throughout the application.

## Setup ##

To setup this project, we first will want to [create a Notion database](https://www.notion.so/help/guides/creating-a-database) and [create a Notion integration](https://developers.notion.com/docs/create-a-notion-integration).

Then create a `.env` file in the root of this project and populate it with the following:
```
NOTION_TOKEN="<notion token for your integration>"
DATABASE_ID="<id of your created database>"
```

Next install the dependencies using pip - I reccommend creating a virtual environment first:

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Finally, you can run the entrypoint and see the database populate:
```
python3 main.py
```

You can also run the tests as well:
```
python3 tests.py
```

There is also the option to run via Docker:
```
docker build -t notion-take-home . && docker run notion-take-home
```

Or run the tests via Docker:
```
docker build -t notion-take-home-tests -f Dockerfile.tests . && docker run notion-take-home-tests
```

## Libraries ##
A couple of libraries were key to this project:
* **notion-client**: Used to interface with Notion API with some levels of abstraction
* **python-dotenv**: Used to load environment variables so integration tokens can be kept secret
* **pytest**: Used as a testing framework to ensure high quality and robust code.

## Sources ##
* [Notion Developer Docs](https://developers.notion.com/reference/): API Reference for Notion API
  * Note: I relied on many pages throughout the Notion API reference - for the sake of brevity, I've only included the overall developer docs but all pages I relied on can be found in subpages of the developer docs.
* [Python Notion Client Docs](https://ramnes.github.io/notion-sdk-py/): API Reference for the Unofficial Python SDK for Notion API
* [Source Code for Python Notion Client](https://github.com/ramnes/notion-sdk-py): Used as a reference to determine SDK usage
* [Notion Intern Take Home Exercise](https://www.notion.so/Intern-Take-Home-Exercise-ca75357f136d4557be6505632ed9bde0): Specifications for this exercise
* [PyTest Global Variable Stackoverflow Thread](https://stackoverflow.com/questions/44441929/how-to-share-global-variables-between-tests): Used to help me determine how to create a unified Database Client for my tests

## Reflection ##

This assignment was a really interesting assignment and I would say it really helped me both become a bit better with the way I right code while also enabling me to learn more about Notion!

### Challenges ###

Having not interacted too heavily with Notion API in Python before, working on this project had some challenges. One challenge I am really proud of overcoming was determining how the Unofficial Python client interfaced with Notion's API. 

When working with the client, I noticed I would get error messages that would be a bit cryptic (i.e. `properties.properties.Book Title.rich_text is undefined`). While the message in itself isn't too difficult to understand, it did not make sense in the context of the API request I was sending via the client.

In essence, the issue was that I was passing through a body like this to the client:
```
{
  properties: {
    Book Title {...}
  }
}
```
when in reality it should've been: 
```
{
    Book Title {...}
}
```

This reason I came across this issue is because of inconsistences in the documentation between the client documentation and Notion's documentation. The client documentation told me to refer to the Notion documentation when deciding what values to pass into the client - but this was not quite exactly what I needed to do. 

I was able to overcome this error by delving into the source code to determine how exactly the API request was being made within the client which is when I came across this line of code:
```
body=pick(kwargs, "archived", "properties", "icon", "cover")
```

The `pick` here is defined as is:
```
def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a dict composed of key value pairs for keys passed as args."""
    return {key: base[key] for key in keys if key in base and base[key] is not None}
```

After reading through some of the source code, I came to the conclusion that the pick method will automatically construct the outer properties based what property I choose when making the method call. Therefore, I did not need to manually specify `properties` when constructing the body because it was handled internally.

### Notion API Documentation Feedback ###

The Notion API documentation was quite thorough and well written! However I believe there are a couple areas of improvement:
* **Examples:** I am someone who learns best by reading examples of code - while there were some examples of requests in the API, I think I would have been able to work far faster if there were more examples in the docs. As it stands, the number of examples in the docs does cover the breadth of the capabilities of the API.
* **Organization:** The organization of the Notion API docs is intuitive but because of the nature of how the API is used, it can get quite messy from a developer's perspective. For instance, in order to make one API call, I might have open 3 or 4 tabs because there are so many types of objects and attributes I need to keep note of. Having some way to have multiple pages of the docs open on one screen might make the docs easier to navigate. 
* **Notion Glossary:** Going off the last point, because there are so many definitions in Notion, I think having a Glosssary of some sorts with all the object defitions, attribute definitions, etc. would be extremely useful. The centralization of these resources would ensure that developers can find the things they care about most a lot faster. 

