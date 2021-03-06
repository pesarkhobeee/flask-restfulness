from flask_restful import Resource, reqparse
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

from src.DbHandler import DbHandler
import json

# Load config file
with open('config.json', mode='r') as config_file:
    MAX_LINKS_PER_PAGE = json.load(config_file).get('pagination', {}).\
        get('maximum_links_per_page')

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('page', type=int, location='args')
parser.add_argument('page_size', type=int, location='args')


class LinksGetterBySearch(Resource):
    @jwt_required
    @swag_from('../../yml/links_get_search.yml')
    def get(self, pattern):
        """ Return links that contains special keyword paginated. """
        current_user_username = get_jwt_identity()
        args = parser.parse_args()
        page = args['page']
        page_size = args['page_size']

        if page and page_size:
            if page_size > MAX_LINKS_PER_PAGE:
                return make_response(
                    jsonify(msg="Requested page size " +
                            "is larger than our max limit!"),
                    400
                )
            links_list = DbHandler.get_links_by_pattern(current_user_username,
                                                        pattern, page,
                                                        page_size)
        else:
            links_list = DbHandler.get_links_by_pattern(current_user_username,
                                                        pattern)

        if links_list == 'PATTERN_NOT_FOUND':
            return make_response(
                jsonify(msg="Pattern not found!"),
                404
            )
        else:
            return make_response(
                jsonify(links_list),
                200
            )
