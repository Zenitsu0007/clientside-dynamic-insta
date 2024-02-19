"""Insta485 REST API."""
from insta485.api.index import get_index
from insta485.api.index import check_authentication
from insta485.api.posts import get_some_posts
from insta485.api.posts import get_post_detail
from insta485.api.comments import create_comment
from insta485.api.comments import delete_comment
from insta485.api.likes import create_like
from insta485.api.likes import delete_like
