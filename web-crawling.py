import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
from pprint import pprint
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# SQLAlchemy ORM Setup
Base = declarative_base()


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


class DatabaseORM:
    def __init__(self, db_url='sqlite:///bama-cars.db'):
        self.engine = create_engine(db_url, echo=True)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close_session(self):
        self.Session.remove()

    def add_instance(self, model_class, data_dict):
        session = self.get_session()
        instance = model_class(**data_dict)
        session.add(instance)
        session.commit()

    def get_all(self, model_class):
        session = self.get_session()
        return session.query(model_class).all()

    def get_by_filter(self, model_class, **kwargs):
        session = self.get_session()
        return session.query(model_class).filter_by(**kwargs).first()

    def delete_instance(self, instance):
        session = self.get_session()
        session.delete(instance)
        session.commit()

    def update_instance(self):
        session = self.get_session()
        session.commit()


# Web Scraping Crawler
class ClassName:
    def __init__(self, main_class_name, class_name_prefix=None):
        self.main_class_name = main_class_name
        self.class_name_prefix = class_name_prefix

    def generate_class_name(self) -> str:
        if self.class_name_prefix is not None:
            return f"{self.main_class_name}__{self.class_name_prefix}"
        return f"{self.main_class_name}"


class Crawler:
    code_dict = dict()
    valid_classes = list()

    def __init__(self, base_link):
        self.base_link = base_link
        self.session = None
        self.orm = DatabaseORM()  # Initialize the DatabaseORM class

    async def fetch(self, url):
        async with self.session.get(url) as response:
            response.raise_for_status()
            html_content = await response.text()
            return html_content

    async def get_links(self):
        html_content = await self.fetch(self.base_link)
        soup = BeautifulSoup(html_content, 'html.parser')
        return [a.get('href') for a in soup.findAll('a', href=True)]

    async def filter_by_name(self, name):
        links = await self.get_links()
        return set([link for link in links if re.search(rf"^/{name}/", link)])

    async def get_code_divs(self, link, class_name):
        html_content = await self.fetch(link)
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.find_all("div", class_=class_name)

    @classmethod
    async def extract(cls, divs):
        image_box_class = ClassName(main_class_name="bama-ad", class_name_prefix="image-box")\
            .generate_class_name()
        title_class = ClassName(main_class_name="text").generate_class_name()
        price_class = ClassName(main_class_name="bama-ad", class_name_prefix="price").\
            generate_class_name()
        address_class = ClassName(main_class_name="bama-ad", class_name_prefix="address")\
            .generate_class_name()
        time_class = ClassName(main_class_name="bama-ad", class_name_prefix="time")\
            .generate_class_name()

        code_dict = {}
        for div in divs:
            code = div.get("code")
            if code:
                title = div.find(class_=title_class).text.strip() if div.find(class_=title_class) \
                    else "No Title"
                image = div.find(class_=image_box_class).find("img")['src'] if div.find(
                    class_=image_box_class) and div.find("img") else "No Image"
                price = div.find(class_=price_class).text.strip() if div.find(class_=price_class)\
                    else "No Price"
                location = div.find(class_=address_class).text.strip() if div.find(class_=address_class)\
                    else "No Location"
                post_time = div.find(class_=time_class).text.strip() if div.find(class_=time_class)\
                    else "No Post Time"

                details_div = div.find(class_="bama-ad__detail-row")
                details_list = [span.text.strip() for span in details_div.find_all("span")] if details_div else []

                code_dict[code] = {
                    "title": title,
                    "image": image,
                    "price": price,
                    "location": location,
                    "post_time": post_time,
                    "details": details_list
                }

        return code_dict

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

                # Store each car's data in the database
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


async def main():
    instance_base_link = "https://bama.ir/price"
    crawler = Crawler(base_link=instance_base_link)
    await crawler.process()


if __name__ == "__main__":
    asyncio.run(main())
