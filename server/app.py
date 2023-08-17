#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

#Added
ma = Marshmallow(app)

class NewsletterSchema(ma.SQLAclhemySchema):
    class Meta: 
        model = Newsletter
        load_instance = True
    
    title = ma.auto_field()
    published_at = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "newsletterbyid",
                values=dict(id="<id>")),
                "collection": ma.URLFor("newsletters"),
        }
    )
newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

class Index(Resource):

    def get(self):
        
        response_dict = {
            "index": "Welcome to the Newsletter RESTful API",
        }
        
        response = make_response(
            response_dict,
            200,
        )

        return response

api.add_resource(Index, '/')

class Newsletters(Resource):

    def get(self):
        #New Marshmallow code 
        newsletters = Newsletter.query.all()

        response = make_response(
            newsletters_schema.dump(newsletters),
            200
        )
        return response
    
        #Old code
        # response_dict_list = [n.to_dict() for n in Newsletter.query.all()]

        # response = make_response(
        #     response_dict_list,
        #     200,
        # )

        # return response

    def post(self):
        
        new_record = Newsletter(
            title=request.form['title'],
            body=request.form['body'],
        )

        db.session.add(new_record)
        db.session.commit()

        # response_dict = new_record.to_dict()

        # response = make_response(
        #     response_dict,
        #     201,
        # )
        response = make_response(
            newsletter_schema.dump(new_record),
            201
        )
        return response

api.add_resource(Newsletters, '/newsletters')

class NewsletterByID(Resource):

    def get(self, id):
        response_ma = Newsletter.query.filter_by(id=id).first()

        response = make_response(
            newsletter_schema.dump(response_ma),
            200
        )
        return response

        # response_dict = Newsletter.query.filter_by(id=id).first().to_dict()

        # response = make_response(
        #     response_dict,
        #     200,
        # )

        # return response

    def patch(self, id):

        record = Newsletter.query.filter_by(id=id).first()
        for attr in request.form:
            setattr(record, attr, request.form[attr])

        db.session.add(record)
        db.session.commit()

        response = make_response(
            newsletter_schema.dump(record),
            200
        )

        return response

    def delete(self, id):

        record = Newsletter.query.filter_by(id=id).first()
        
        db.session.delete(record)
        db.session.commit()

        response_dict = {"message": "record successfully deleted"}

        response = make_response(
            response_dict,
            200
        )

        return response

api.add_resource(NewsletterByID, '/newsletters/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)