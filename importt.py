import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://ajigwrxxtsfjgh:eef2bb35cd85a37e7d10b5699794a552f7dd4736560b44c88126e9f1228f8f51@ec2-54-145-102-149.compute-1.amazonaws.com:5432/d8tvv4bh4q66pr")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn,:title,:author,:year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Books were opened from {isbn} to {title} writer {author} year {year}")
        db.commit()

if __name__ == "__main__":
    main()
