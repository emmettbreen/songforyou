from wtforms import Form, StringField, SelectField, SubmitField

class SongSearchForm(Form):
    search = StringField('')

class SongSelectForm(Form):
    select = SelectField('Search for music:', choices=[])
    add = SubmitField()
