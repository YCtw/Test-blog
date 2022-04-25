from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.secret_key = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Table2(db.Model):
    __tablename__ = "table2"
    id = db.Column(db.Integer, primary_key=True)
    director = db.Column(db.String(250), nullable=False)
    born_year = db.Column(db.Integer, nullable=False)
    slogan = db.Column(db.String(250), nullable=False)
    movie = relationship("Table1", back_populates="info")

# db.create_all()

class Table1(db.Model):
    __tablename__ = "table1"
    id = db.Column(db.Integer, primary_key=True)
    director = db.Column(db.String(250), nullable=False)
    movie_title = db.Column(db.String(250), nullable=False)
    #查詢的時候用這個來連接
    director_id = db.Column(db.Integer, db.ForeignKey("table2.id"))
    info = relationship("Table2", back_populates="movie")

# db.create_all()

# test_result2 = Table2(director="three", born_year=20, slogan="nife")
# db.session.add(test_result2)
# db.session.commit()
# #
# test_result1 = Table1(director= "pot", movie_title="box", director_id= 6)
# db.session.add(test_result1)
# db.session.commit()

#
# test1 = Table1(director = "Wonse", movie_title="xr")
# db.session.add(test1)
# db.session.commit()

search_result = Table2.query.get(6)
print(len(search_result.movie))


if __name__ == '__main__':
    app.run(debug=True)