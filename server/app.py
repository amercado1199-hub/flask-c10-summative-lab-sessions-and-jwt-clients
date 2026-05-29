#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Note


class Signup(Resource):
    def post(self):
        data = request.get_json()

        try:
            user = User(username=data.get("username"))
            user.password_hash = data.get("password")

            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return user.to_dict(), 201

        except (ValueError, IntegrityError):
            db.session.rollback()
            return {"errors": ["validation errors"]}, 422


class Login(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.filter_by(username=data.get("username")).first()

        if user and user.authenticate(data.get("password")):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.get(user_id)

        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        session.clear()
        return {}, 204


class Notes(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        pagination = Note.query.filter_by(user_id=user_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
            "items": [note.to_dict() for note in pagination.items]
        }, 200

    def post(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        try:
            note = Note(
                title=data.get("title"),
                content=data.get("content"),
                user_id=user_id
            )

            db.session.add(note)
            db.session.commit()

            return note.to_dict(), 201

        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 422


class NoteByID(Resource):
    def patch(self, id):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        note = Note.query.filter_by(id=id, user_id=user_id).first()

        if not note:
            return {"error": "Note not found"}, 404

        data = request.get_json()

        try:
            if "title" in data:
                note.title = data.get("title")

            if "content" in data:
                note.content = data.get("content")

            db.session.commit()

            return note.to_dict(), 200

        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 422

    def delete(self, id):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized"}, 401

        note = Note.query.filter_by(id=id, user_id=user_id).first()

        if not note:
            return {"error": "Note not found"}, 404

        db.session.delete(note)
        db.session.commit()

        return {}, 204


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Logout, "/logout")
api.add_resource(Notes, "/notes")
api.add_resource(NoteByID, "/notes/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)