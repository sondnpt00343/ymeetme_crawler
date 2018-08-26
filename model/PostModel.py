# -*- coding: utf-8 -*-
import time
import json
import mysql.connector

from helper.Database import Database
from datetime import datetime
from collections import namedtuple

class PostModel():

    # Find a post with condition
    # Example
    #   post.find('id', id)
    @staticmethod
    def find_by_origin_id(value):
        params = (value,)
        try:
            # Get database connection
            database    = Database()
            connector   = database.connect()
            cursor      = database.cursor()

            cursor.execute("SELECT * FROM posts WHERE id=%s", params)
            result = cursor.fetchone()
            if result is not None:
                return namedtuple("Post", result.keys())(*result.values())
            else:
                return result
        except mysql.connector.Error as error:
            print(error)

    # Save data to database
    @staticmethod
    def save(params):
        # Get database connection
        database    = Database()
        connector   = database.connect()
        cursor      = database.cursor()

        # Build query to insert data
        query = ("INSERT INTO posts "
            "(origin_id, origin_url, title, description ,image, crawl_status, created_at, updated_at) "
            "VALUES (%(origin_id)s, %(origin_url)s, %(title)s, %(description)s, %(image)s, %(crawl_status)s, %(created_at)s, %(updated_at)s)")

        # Total queries
        count = 0;

        # Insert new posts
        try:
            result = cursor.execute(query, params)
            connector.commit()

            # Increase total queries
            count += cursor.rowcount
        except mysql.connector.IntegrityError as err:
            print("PostModel.save: {}".format(err))
            return False

        return count

    @staticmethod
    def findAll():
        try:
            # Get database connection
            database    = Database()
            connector   = database.connect()
            cursor      = database.cursor()

            cursor.execute("SELECT * FROM posts")
            posts = []
            for (post) in cursor:
                posts.append(post)
            return posts
        except mysql.connector.Error as error:
            print(error)

    @staticmethod
    def findPostNoContent():
        try:
            # Get database connection
            database    = Database()
            connector   = database.connect()
            cursor      = database.cursor()

            cursor.execute("SELECT * FROM posts where crawl_status = 0")
            posts = []
            for (post) in cursor:
                posts.append(post)
            return posts
        except mysql.connector.Error as error:
            print(error)

    @staticmethod
    def updatePost(post_id, params):
        # prepare query and data
        query = """ UPDATE posts
                    SET description = %(description)s, crawl_status = %(crawl_status)s, updated_at = %(updated_at)s
                    WHERE id = %(id)s
                    LIMIT 1 """

        try:
            # Get database connection
            database    = Database()
            connector   = database.connect()
            cursor      = database.cursor()

            # update pair time
            params['id'] = post_id
            rows_update = cursor.execute(query, params)

            # accept the changes
            connector.commit()

            return True
        except mysql.connector.Error as error:
            print(error)
            return False
