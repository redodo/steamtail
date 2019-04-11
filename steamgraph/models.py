from neomodel import (
    StructuredNode, StructuredRel, StringProperty, DateProperty,
    UniqueIdProperty, Relationship, RelationshipTo, FloatProperty,
    IntegerProperty,
)


class Tag(StructuredNode):
    tag_id = UniqueIdProperty()
    name = StringProperty()


class AppTagRel(StructuredRel):
    votes = IntegerProperty()


class App(StructuredNode):
    app_id = UniqueIdProperty()
    name = StringProperty()

    tags = RelationshipTo(Tag, 'TAGGED', model=AppTagRel)


class UserAppRel(StructuredRel):
    hours_played = FloatProperty()


class User(StructuredNode):
    user_id = UniqueIdProperty()

    friends = Relationship('User', 'FRIEND')
    apps = RelationshipTo(App, 'OWNS', model=UserAppRel)
