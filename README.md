# WEB CRAWLING

---


#### Libraries and Imports

- **`asyncio`**: This is a Python library used to write concurrent code using the `async`/`await` syntax. It allows the program to perform asynchronous operations, such as I/O-bound tasks like fetching data from websites.
  
- **`aiohttp`**: This is an asynchronous HTTP client/server framework. In this script, it is used to perform asynchronous HTTP requests, enabling the script to handle multiple requests simultaneously.
  
- **`re`**: This module provides regular expression matching operations, which are used for string searching and manipulation.

- **`BeautifulSoup`**: This is a Python library used for parsing HTML and XML documents. It creates a parse tree that is helpful for extracting data from HTML tags.
  
- **`pprint`**: This module provides a capability to "pretty-print" data structures, making it easier to read complex data structures.

- **`sqlalchemy`**: SQLAlchemy is a SQL toolkit and Object-Relational Mapping (ORM) library for Python. It allows the program to interact with the database in an object-oriented manner.

#### SQLAlchemy ORM Setup

The script begins by setting up SQLAlchemy's ORM (Object-Relational Mapping), which allows interaction with the database through Python classes.

```python
Base = declarative_base()
```

- **`Base`**: This is the base class for all the ORM models. It keeps track of all tables and mapped classes.

#### Car Model

```python
class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_type = Column(String(50))
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(100))
    details = Column(Text)
    image = Column(String(255))
    location = Column(String(100))
    post_time = Column(String(50))
    price = Column(String(50))

    def __repr__(self):
        return f"<Car(car_type='{self.car_type}', code='{self.code}', title='{self.title}', price='{self.price}')>"
```

- **`Car`**: This class defines the structure of the `cars` table in the SQLite database.
  - `id`: Primary key, auto-incremented.
  - `car_type`: Type of the car.
  - `code`: Unique code identifier for the car.
  - `title`: Title or name of the car.
  - `details`: Detailed description of the car.
  - `image`: URL to the car's image.
  - `location`: Location where the car is available.
  - `post_time`: The time when the car was posted.
  - `price`: Price of the car.

The `__repr__` method provides a readable string representation of the `Car` objects, useful for debugging.

#### Database ORM Class

```python
class DatabaseORM:
    def __init__(self, db_url='sqlite:///bama-cars.db'):
        self.engine = create_engine(db_url, echo=True)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine)
```

- **`DatabaseORM`**: This class encapsulates the database operations.
  - **`__init__`**: Initializes the database connection using SQLAlchemy's `create_engine`. It also sets up a scoped session, which ensures that sessions are thread-safe.
  - **`get_session`**: Returns a new session for database operations.
  - **`close_session`**: Closes the session, ensuring no memory leaks.
  - **`add_instance`**: Adds a new instance (record) to the database.
  - **`get_all`**: Retrieves all records of a given model class from the database.
  - **`get_by_filter`**: Retrieves a specific record based on filter criteria.
  - **`delete_instance`**: Deletes a given record from the database.
  - **`update_instance`**: Commits changes to an existing record.

#### Web Scraping Crawler

##### ClassName Class

```python
class ClassName:
    def __init__(self, main_class_name, class_name_prefix=None):
        self.main_class_name = main_class_name
        self.class_name_prefix = class_name_prefix

    def generate_class_name(self) -> str:
        if self.class_name_prefix is not None:
            return f"{self.main_class_name}__{self.class_name_prefix}"
        return f"{self.main_class_name}"
```

- **`ClassName`**: This utility class is used to generate CSS class names dynamically.
  - **`__init__`**: Initializes the class with the main class name and an optional prefix.
  - **`generate_class_name`**: Concatenates the main class name with the prefix (if provided) using double underscores (`__`).

##### Crawler Class

```python
class Crawler:
    code_dict = dict()
    valid_classes = list()

    def __init__(self, base_link):
        self.base_link = base_link
        self.session = None
        self.orm = DatabaseORM()
```

- **`Crawler`**: This class is responsible for fetching and processing data from the web.
  - **`code_dict`**: A dictionary to hold extracted data.
  - **`valid_classes`**: A list to hold valid CSS classes.
  - **`__init__`**: Initializes the crawler with a base URL and an instance of `DatabaseORM`.

##### Asynchronous Methods

- **`fetch`**: Performs an asynchronous HTTP GET request to fetch the HTML content of a given URL.
  
- **`get_links`**: Fetches the content of the base URL and extracts all links (`<a>` tags with `href` attributes) from it.

- **`filter_by_name`**: Filters links based on a given name pattern, returning only those that match the pattern.

- **`get_code_divs`**: Fetches the HTML content of a specific link and extracts all `div` elements with a given class name.

- **`extract`**: Extracts relevant information (title, image, price, location, post time, details) from the `div` elements and organizes it into a dictionary.

##### Process Method

```python
async def process(self):
    async with aiohttp.ClientSession() as session:
        self.session = session

        cars = await self.filter_by_name("car")
        res = []
        for car in list(cars):
            for c in car.split("/"):
                res.append(c)
        res_ = [r for r in res if r != "" and r != "car"]

        nested_code_dict = {}
        tasks = []
        for car_path in res_:
            link_s = f"https://bama.ir/car/{car_path}"
            tasks.append(self.get_code_divs(link_s, "bama-ad-holder"))

        all_code_divs = await asyncio.gather(*tasks)

        for car_path, divs in zip(res_, all_code_divs):
            code_dict = await self.extract(divs)
            nested_code_dict[car_path] = code_dict

            for code, car_data in code_dict.items():
                details_str = ", ".join(car_data['details'])
                car_entry = {
                    'car_type': car_path,
                    'code': code,
                    'title': car_data['title'],
                    'details': details_str,
                    'image': car_data['image'],
                    'location': car_data['location'],
                    'post_time': car_data['post_time'],
                    'price': car_data['price']
                }
                self.orm.add_instance(Car, car_entry)

        pprint(nested_code_dict)
```

- **`process`**: This is the core method that orchestrates the web scraping and data storage.
  - It initializes an asynchronous session.
  - Filters links related to cars.
  - Extracts `div` elements with specific class names from the filtered links.
  - Extracts relevant information from these `divs` and stores it in a nested dictionary.
  - Iterates through the extracted data and stores each car's data in the SQLite database.

#### Main Function

```python
async def main():
    instance_base_link = "https://bama.ir/price"
    crawler = Crawler(base_link=instance_base_link)
    await crawler.process()
```

- **`main`**: The entry point of the script, where an instance of `Crawler` is created and its `process` method is invoked.

#### Running the Script

```python
if __name__ == "__main__":
    asyncio.run(main())
```

- **`__main__`**: This block ensures that the script runs only when executed directly, not when imported as a module. It runs the `main` function using `asyncio.run`.
