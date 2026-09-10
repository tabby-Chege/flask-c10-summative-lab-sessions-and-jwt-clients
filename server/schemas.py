from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validates_schema,
    validate,
)


def validate_not_blank(value):
    if not value.strip():
        raise ValidationError("Field cannot be blank.")


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80),
            validate_not_blank,
        ],
    )


class SignupSchema(Schema):
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80),
            validate_not_blank,
        ],
    )
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8),
    )
    password_confirmation = fields.Str(
        required=True,
        load_only=True,
    )

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data["password"] != data["password_confirmation"]:
            raise ValidationError(
                {"password_confirmation": ["Passwords do not match."]}
            )


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=200),
            validate_not_blank,
        ],
    )
    content = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1),
            validate_not_blank,
        ],
    )
    category = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=50),
            validate_not_blank,
        ],
    )
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    user = fields.Nested(UserSchema, dump_only=True)
