from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Creating_Channel import *

engine = create_engine('sqlite:///channel.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


session.query(LanguageName).delete()

session.query(ChannelName).delete()

session.query(User).delete()

User1 = User(name="Sri Vyshnavi",
             email="nsvs1999@gmail.com",
             picture='image1.jpg')

session.add(User1)
session.commit()
print ("Successfully Add First User")

Language1 = LanguageName(name=" TELUGU", user_id=1)
session.add(Language1)
session.commit()

Language2 = LanguageName(name=" HINDI", user_id=1)
session.add(Language2)
session.commit()

Language3 = LanguageName(name=" ENGLISH", user_id=1)
session.add(Language3)
session.commit()


Language4 = LanguageName(name=" CARTOON", user_id=1)
session.add(Language4)
session.commit()

Language5 = LanguageName(name=" SPORTS", user_id=1)
session.add(Language5)
session.commit()

Language6 = LanguageName(name=" NEWS", user_id=1)
session.add(Language6)
session.commit()

Language7 = LanguageName(name=" COOKING", user_id=1)
session.add(Language7)
session.commit()

Language8 = LanguageName(name=" NATURE", user_id=1)
session.add(Language8)
session.commit()


Channel1 = ChannelName(name="STAR MAA TV",
                       owner="Uday Shankar",
                       price="Rs 49",
                       rating=" 7.4",
                       date=datetime.datetime.now(),
                       languagenameid=1,
                       user_id=1)
session.add(Channel1)
session.commit()

Channel9 = ChannelName(name="ZEE TELUGU",
                       owner="Subhash Chandra Goel",
                       price="Rs 20",
                       rating=" 8.5",
                       date=datetime.datetime.now(),
                       languagenameid=1,
                       user_id=1)
session.add(Channel9)
session.commit()


Channel2 = ChannelName(name="STAR PLUS",
                       owner=" Uday Shankar",
                       price=" Rs 49 ",
                       rating=" 8.9",
                       date=datetime.datetime.now(),
                       languagenameid=2,
                       user_id=1)
session.add(Channel2)
session.commit()


Channel3 = ChannelName(name=" STAR WORLD ",
                       owner="Uday Shankar ",
                       price="Rs 49",
                       rating="8.2",
                       date=datetime.datetime.now(),
                       languagenameid=3,
                       user_id=1)
session.add(Channel3)
session.commit()
Channel4 = ChannelName(name="DISNEY XD",
                       owner=" Alan Wagner. ",
                       price="Rs 4",
                       rating="7.9",
                       date=datetime.datetime.now(),
                       languagenameid=4,
                       user_id=1)
session.add(Channel4)
session.commit()
Channel5 = ChannelName(name=" STAR SPORTS ",
                       owner="Uday Shankar",
                       price="Rs 19",
                       rating="6.6",
                       date=datetime.datetime.now(),
                       languagenameid=5,
                       user_id=1)
session.add(Channel5)
session.commit()

Channel6 = ChannelName(name=" TV9",
                       owner=" Ravi Prakash ",
                       price="Rs 8 ",
                       rating="9.0",
                       date=datetime.datetime.now(),
                       languagenameid=6,
                       user_id=1)
session.add(Channel6)
session.commit()


Channel7 = ChannelName(name=" TLC ",
                       owner="John Hendricks ",
                       price=" Free",
                       rating="6.4,",
                       date=datetime.datetime.now(),
                       languagenameid=7,
                       user_id=1)
session.add(Channel7)
session.commit()


Channel8 = ChannelName(name=" DISCOVERY",
                       owner="John Hendricks",
                       price=" Rs 4",
                       rating="7.9",
                       date=datetime.datetime.now(),
                       languagenameid=8,
                       user_id=1)
session.add(Channel8)
session.commit()


print("Your channels in database has been inserted!")
