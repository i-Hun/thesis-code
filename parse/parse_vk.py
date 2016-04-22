# python3
import os
import csv
import pickle
# from pymongo import MongoClient
from mongoengine import *
from dateutil.parser import parse as parse_date

# db = MongoClient().thesis
# vk_users_db = db.vk_users
# vk_posts_db = db.vk_posts
connect("thesis")


class Vk_users(Document):
    user_id = IntField(primary_key=True, required=True, unique=True)
    first_name = StringField()
    last_name = StringField()
    screen_name = StringField()
    sex = IntField(required=True)
    birth_day = IntField()
    birth_month = IntField()
    birth_year = IntField()
    city = StringField()
    region = StringField()
    country = StringField()
    posts_count = IntField(required=True)
    comments_count = IntField(required=True)
    likes_count = IntField(required=True)
    rec_comments = IntField(required=True)
    rec_posts_likes = IntField(required=True)
    rec_comments_likes = IntField(required=True)
    phone = StringField()
    site = StringField()
    univ = StringField()
    faculty = StringField()
    edu = StringField()
    edu_status = StringField()
    friends_count = IntField(required=True)
    groups_count = IntField(required=True)
    followers_count = IntField(required=True)
    photo = StringField()
    posts = ListField(ReferenceField("Vk_posts"), default=[])  # посты, которые написал пользователь
    wall_posts = ListField(ReferenceField("Vk_posts"), default=[])  # посты, которые написаны на степне пользователя. Это надо?

    def getFullName(self):
        return "{} {}".format(self.first_name, self.last_name)


class Vk_posts(Document):
    post_id = StringField(primary_key=True, required=True, unique=True)
    wall_owner = ReferenceField("Vk_users", required=True,)
    author_id = ReferenceField("Vk_users", required=True,)
    date = DateTimeField(required=True)
    text = StringField()
    comments_count = IntField(required=True,)
    likes_count = IntField(required=True,)
    reposts_count = IntField(required=True,)
    repost_owner_id = ReferenceField("Vk_users")
    repost_added_text = StringField()
    link_url = StringField()
    likers_ids = ListField(ReferenceField("Vk_users"))
    comments = ListField(ReferenceField("Vk_comments"))


class Vk_comments(Document):
    comment_id = StringField(primary_key=True, required=True, unique=True)
    author_id = ReferenceField("Vk_users", required=True)
    date = DateTimeField(required=True)
    text = StringField()
    likers_ids = ListField(ReferenceField("Vk_users"))





users_csv_fields = ["id", "First Name", "Last Name", "Screen Name", "Sex", "BDate", "City", "Region", "Country",
               "Posts", "Comments", "Likes", "Recieved Comments", "Recieved Posts Likes", "Recieved Comments Likes",
               "Mobile phone", "Home site", "University", "Faculty", "Education", "Education Status", "Friends", "Groups",
               "Followers", "Timezone", "Photo"]

wallposts_csv_fields = ["id", "from_id", "date", "text", "comments", "likes", "reposts", "link_url", "link_title",
                        "link_description", "link_image_src", "copy_owner_id", "copy_text"]

wallpostslikes_csv_fields = ["id", "user_id", "like_id"]

comments_csv_fields = ["id", "authid", "from_id", "Author_post", "date", "text", "likes"]
"""
id = id комментария, идёт в ?reply=id
authid = id автора комментария
from_id = часть id поста, к которому сделан комментарий
Author_post = id автора поста
"""

commentslikes_csv_field = ["id", "user_id", "comm_id", "comm_user_id", "like_id"]

def users_to_db():
    for dirpath, dirs, files in os.walk("../../vk/"):
        for num, userdir in enumerate(dirs):
            # print(num, userdir, dirpath)
            for csvfilename in os.listdir(os.path.join(dirpath, userdir)):
                if csvfilename == "wall_persuinfo.csv":
                    path_to_csv = os.path.join(dirpath, userdir, csvfilename)
                    with open(path_to_csv, newline="", encoding="CP1251") as csvfile:
                        csvfile.seek(0)
                        next(csvfile)
                        csvreader = csv.DictReader(csvfile, fieldnames=users_csv_fields, delimiter=";")
                        for row in csvreader:
                            if row["Sex"] != (1 or 2): # пол может быть "", 0 и "(Error on loading)"
                                sexvar = 0
                            else:
                                sexvar = int(row["Sex"])

                            if row["BDate"] == "":
                                bdatey = None
                                bdatem = None
                                bdated = None
                            elif row["BDate"] == "(Error on loading)":
                                bdatey = None
                                bdatem = None
                                bdated = None
                            else:
                                bdatelist = row["BDate"].split(".")
                                if len(bdatelist) == 2:
                                    bdatey = None
                                    bdatem = int(bdatelist[1])
                                    bdated = int(bdatelist[0])
                                elif len(bdatelist) == 3:
                                    bdatey = int(bdatelist[2])
                                    bdatem = int(bdatelist[1])
                                    bdated = int(bdatelist[0])
                                else:
                                    raise Exception("Проблемы с датой рождения юзеров", row["BDate"])


                            dic = {
                                "user_id": int(row["id"]),
                                "first_name": row["First Name"],
                                "last_name": row["Last Name"],
                                "screen_name": row["Screen Name"],
                                "sex": sexvar,
                                "birth_day": bdated,
                                "birth_month": bdatem,
                                "birth_year": bdatey,
                                "city": row["City"],
                                "region": row["Region"],
                                "country": row["Country"],
                                "posts_count": int(row["Posts"]),
                                "comments_count": int(row["Comments"]),
                                "likes_count": int(row["Likes"]),
                                "rec_comments": int(row["Recieved Comments"]),
                                "rec_posts_likes": int(row["Recieved Posts Likes"]),
                                "rec_comments_likes": int(row["Recieved Comments Likes"]),
                                "phone": row["Mobile phone"],
                                "site": row["Home site"],
                                "univ": row["University"],
                                "faculty": row["Faculty"],
                                "edu": row["Education"],
                                "edu_status": row["Education Status"],
                                "friends_count": int(row["Friends"]),
                                "groups_count": int(row["Groups"]),
                                "followers_count": int(row["Followers"]),
                                "photo": row["Photo"]

                            }
                            user = Vk_users(**dic)
                            try:
                                user.save()
                            except NotUniqueError as err:
                                print(err)


def get_postslikes():
    if os.path.isfile("postslikes.pickle"):
        with open("postslikes.pickle", "rb") as f:
            return pickle.load(f)
    else:
        postslikes = {}
        for dirpath, dirs, files in os.walk("../../vk/"):
                for num, userdir in enumerate(dirs):
                    if "wall_postslikes.csv" in os.listdir(os.path.join(dirpath, userdir)):
                        path_to_postslikes = os.path.join(dirpath, userdir, "wall_postslikes.csv")
                        with open(path_to_postslikes, newline="", encoding="CP1251") as csv_postslikes:
                            csv_postslikes.seek(0)
                            next(csv_postslikes)
                            csvreader_postslikes = csv.DictReader(csv_postslikes, fieldnames=wallpostslikes_csv_fields, delimiter=";")
                            for row in csvreader_postslikes:
                                post_uniq_id = "{0}_{1}".format(userdir, row["id"])
                                if post_uniq_id not in postslikes:
                                    postslikes[post_uniq_id] = {}
                                    postslikes[post_uniq_id]["author"] = int(row["user_id"])
                                    postslikes[post_uniq_id]["wall_owner"] = int(userdir)
                                if "likers" not in postslikes[post_uniq_id]:
                                    postslikes[post_uniq_id]["likers"] = set()
                                    postslikes[post_uniq_id]["likers"].add(int(row["like_id"]))
                                else:
                                    postslikes[post_uniq_id]["likers"].add(int(row["like_id"]))

        print("postslikes ready")

        with open("postslikes.pickle", "wb") as f:
            pickle.dump(postslikes, f)
        return postslikes

def get_commlikes():
    if os.path.isfile("commlikes.pickle"):
        with open("commlikes.pickle", "rb") as f:
            return pickle.load(f)
    else:
        commlikes = {}
        for dirpath, dirs, files in os.walk("../../vk/"):
                for num, userdir in enumerate(dirs):
                    if "wall_commlikes.csv" in os.listdir(os.path.join(dirpath, userdir)):
                        path_to_postslikes = os.path.join(dirpath, userdir, "wall_commlikes.csv")
                        with open(path_to_postslikes, newline="", encoding="CP1251") as csv_commlikes:
                            csv_commlikes.seek(0)
                            next(csv_commlikes)
                            csvreader_commlikes = csv.DictReader(csv_commlikes, fieldnames=commentslikes_csv_field, delimiter=";")
                            for row in csvreader_commlikes:
                                comm_uniq_id = "{0}_{1}_{2}".format(userdir, row["id"], row["comm_id"])
                                if comm_uniq_id not in commlikes:
                                    commlikes[comm_uniq_id] = {}
                                    commlikes[comm_uniq_id]["comment_author"] = int(row["comm_user_id"])
                                    commlikes[comm_uniq_id]["parent_post"] = userdir + "_" + row["id"]
                                if "likers" not in commlikes[comm_uniq_id]:
                                    commlikes[comm_uniq_id]["likers"] = set()
                                    commlikes[comm_uniq_id]["likers"].add(int(row["like_id"]))
                                else:
                                    commlikes[comm_uniq_id]["likers"].add(int(row["like_id"]))
        with open("commlikes.pickle", "wb") as f:
            pickle.dump(commlikes, f)

        return commlikes



def posts_to_db():
    err_counter = 0
    postslikes = get_postslikes()
    for dirpath, dirs, files in os.walk("../../vk/"):
            for num, userdir in enumerate(dirs):
                print(userdir)
                if "wall_posts.csv" in os.listdir(os.path.join(dirpath, userdir)):
                    path_to_csv = os.path.join(dirpath, userdir, "wall_posts.csv")
                    with open(path_to_csv, newline="", encoding="CP1251") as csvfile:
                        csvfile.seek(0)
                        try:
                            next(csvfile)
                        except Exception:
                            err_counter += 1
                        csvreader = csv.DictReader(csvfile, fieldnames=wallposts_csv_fields, delimiter=";")
                        try:
                            for row in csvreader:
                                post_uniq_id = "{0}_{1}".format(userdir, row["id"])

                                if not post_uniq_id in postslikes:
                                    likers_ids = []
                                else:
                                    likers_ids = postslikes[post_uniq_id]["likers"]
                                if row["reposts"] == "":
                                    continue
                                author_id = int(row["from_id"])
                                wall_owner = int(userdir)
                                dic = {
                                    "post_id": post_uniq_id,
                                    "wall_owner": wall_owner,
                                    "author_id": author_id,
                                    "date": parse_date(row["date"]),
                                    "text": row["text"],
                                    "comments_count": int(row["comments"]),
                                    "likes_count": int(row["likes"]),
                                    "reposts_count": int(row["reposts"]),
                                    "repost_owner_id": None if row["copy_owner_id"] == "" else int(row["copy_owner_id"]),
                                    "repost_added_text": row["copy_text"],
                                    "link_url": row["link_url"],
                                    "likers_ids": likers_ids,
                                }
                                post = Vk_posts(**dic)
                                post.save()

                                author = Vk_users.objects.get(user_id=author_id)
                                author.posts.append(post)
                                author.save()

                                wall_owner_user = Vk_users.objects.get(user_id=wall_owner)
                                wall_owner_user.wall_posts.append(post)
                                wall_owner_user.save()
                        except UnicodeDecodeError as err:
                            err_counter += 1
                            print(err_counter, err)
                        except ValueError as err:
                            err_counter += 1
                            print(err_counter, err)


def get_commlikes():
    if os.path.isfile("commlikes.pickle"):
        with open("commlikes.pickle", "rb") as f:
            return pickle.load(f)
    else:
        commlikes = {}
        for dirpath, dirs, files in os.walk("../../vk/"):
                for num, userdir in enumerate(dirs):
                    if "wall_commlikes.csv" in os.listdir(os.path.join(dirpath, userdir)):
                        path_to_postslikes = os.path.join(dirpath, userdir, "wall_commlikes.csv")
                        with open(path_to_postslikes, newline="", encoding="CP1251") as csv_commlikes:
                            csv_commlikes.seek(0)
                            next(csv_commlikes)
                            csvreader_commlikes = csv.DictReader(csv_commlikes, fieldnames=commentslikes_csv_field, delimiter=";")
                            for row in csvreader_commlikes:
                                comm_uniq_id = "{0}_{1}_{2}".format(userdir, row["id"], row["comm_id"])
                                if comm_uniq_id not in commlikes:
                                    commlikes[comm_uniq_id] = {}
                                    commlikes[comm_uniq_id]["comment_author"] = int(row["comm_user_id"])
                                    commlikes[comm_uniq_id]["parent_post"] = userdir + "_" + row["id"]
                                if "likers" not in commlikes[comm_uniq_id]:
                                    commlikes[comm_uniq_id]["likers"] = set()
                                    commlikes[comm_uniq_id]["likers"].add(int(row["like_id"]))
                                else:
                                    commlikes[comm_uniq_id]["likers"].add(int(row["like_id"]))
        with open("commlikes.pickle", "wb") as f:
            pickle.dump(commlikes, f)

        return commlikes

def comments_to_db():
    err_counter = 0
    miss_counter = 0
    commlikes = get_commlikes()
    for dirpath, dirs, files in os.walk("../../vk/"):
            for num, userdir in enumerate(dirs):
                # print(userdir)
                if "wall_comments.csv" in os.listdir(os.path.join(dirpath, userdir)):
                    path_to_csv = os.path.join(dirpath, userdir, "wall_comments.csv")
                    with open(path_to_csv, newline="", encoding="CP1251") as csvfile:
                        csvfile.seek(0)
                        next(csvfile)
                        csvreader = csv.DictReader(csvfile, fieldnames=comments_csv_fields, delimiter=";")
                        for row in csvreader:
                            comm_uniq_id = "{0}_{1}_{2}".format(userdir, row["from_id"], row["id"])
                            parent_post = "{0}_{1}".format(userdir, row["from_id"])
                            if not comm_uniq_id in commlikes:
                                likers_ids = []
                            else:
                                likers_ids = commlikes[comm_uniq_id]["likers"]
                            dic = {
                                "comment_id": comm_uniq_id,
                                "author_id": int(row["authid"]),
                                "date": parse_date(row["date"]),
                                "text": row["text"],
                                "likers_ids": likers_ids
                            }

                            comment = Vk_comments(**dic)
                            comment.save()

                            post = Vk_posts(post_id=parent_post)
                            print(post.author_id)
                            post.comments.append(comment)
                            # post.save()


    print(err_counter, miss_counter)

# 10002082
def check_users():
    empty_counter = 0
    for dirpath, dirs, files in os.walk("../../vk/"):
        for num, userdir in enumerate(dirs):
            # print(num, userdir, dirpath)
            count = Vk_users.objects(user_id=int(userdir)).count()
            print(count)
            if count == 0:
                empty_counter += 1
                print(empty_counter, userdir)

check_users()
print(Vk_users.objects(user_id=int("1401560")).count())