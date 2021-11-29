from chalice import (
    Blueprint,
    Response,
    NotFoundError,
    BadRequestError,
)
from aws_lambda_powertools.utilities.parser import parse, BaseModel
from chalicelib.managers.articles.articlemanager import ArticleManager
from chalicelib.models.payloads.articles import (
    PostArticleModel,
    GetArticlesModel,
    GetFullArticleModel,
)
from chalicelib.helpers.utils import sanitize_url, get_query_params

articles = Blueprint(__name__)


class ArticlesGetQueryParams(BaseModel):
    min_words: int = 0
    max_words: int = 100000


@articles.route("/articles/{channel}", methods=["GET"])
def enumerate_articles_by_channel(channel) -> GetArticlesModel:
    """
    summary: Return all articles registered to a channel
    parameters:
        - in: query
          name: min_words
          schema:
              type: integer
        - in: query
          name: max_words
          schema:
              type: integer
    responses:
        200:
            description: GetArticlesModel
            schema:
                $ref: '#/definitions/GetArticlesModel'
    """
    query_params = get_query_params(articles, ArticlesGetQueryParams)
    return Response(
        status_code=200,
        body=ArticleManager()
        .get_articles_by_channel(
            channel, query_params.min_words, query_params.max_words
        )
        .json(),
    )


@articles.route("/articles/{channel}/{article_id}", methods=["GET"])
def get_article_by_id(channel, article_id) -> GetFullArticleModel:
    """
    summary: Fetch an individual article by its uuid
    responses:
        200:
            description: GetFullArticleModel
            schema:
                $ref: '#/definitions/GetFullArticleModel'
        404:
            description: ArticleNotFoundmsg
            schema:
                $ref: '#/definitions/StatusMsgFail'

    """
    return Response(
        status_code=200,
        body=ArticleManager().get_single_article_by_id(channel, article_id).json(),
    )


@articles.route("/articles/{channel}", methods=["POST"])
def create_new_article_on_channel(channel):
    """
    summary: Request the creation of a new article, returns a work promise ticket.
    responses:
        200:
            description: CreateArticleResponse
            schema:
                $ref: '#/definitions/CreateArticleResponse'
        404:
            description: ChannelNotFoundmsg
            schema:
                $ref: '#/definitions/StatusMsgFail'
    """
    payload = parse(articles.current_request.json_body, model=PostArticleModel)
    payload.url = sanitize_url(payload.url)
    return Response(
        status_code=202,
        body=ArticleManager().create_article_work_item(channel, payload).json(),
    )
