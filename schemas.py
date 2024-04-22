from marshmallow import Schema, fields

# User Schemas
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserCreateSchema(UserSchema):
    quote = fields.Str(required=True)

