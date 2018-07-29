import os

from flask import Flask, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

from Logic.Logic import logic
from Models.Model import Base, Asset, User, UserAssets

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'sqlite:///{}'.format(os.path.join(project_dir,
                                                   'stockMarketDB.db'))

port = int(os.environ.get('PORT', 5000))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file

db = SQLAlchemy(app)
DBSession = sessionmaker(bind=db)
session = DBSession()


# Data base creation Notes:
# 1)Uncomment the setup function to drop the database
# and put the new data
# 2)The second time you run the system you should comment the
# setup function so you won't loose yor data

@app.before_first_request
# def setup():
#     # Recreate database each time for demo
#
#     Base.metadata.drop_all(bind=db.engine)
#     Base.metadata.create_all(bind=db.engine)
#
#     # -------adding user in the database by inserting the Email---------
#
#     db.session.add(User('Email'))
#     db.session.commit()


@app.route('/', methods=['GET'])
def menu():
    return render_template('main.html')


@app.route('/assets/add', methods=['GET', 'POST'])
def addAsset():
    message = None
    if request.form:
        name = request.form.get('name')
        closingPrice = request.form.get('closingPrice')
        if closingPrice == '0':
            message = "Price can't be zero"
        elif name != '' and closingPrice != '':
            checkexistence = db.session.query(Asset).filter_by(name=name).first()
            if checkexistence:
                message = 'Asset already Exist !'
            else:
                asset = Asset(name=name, closingPrice=closingPrice)
                db.session.add(asset)
                db.session.commit()
                #view the new asset
                return render_template('asset.html', asset=asset)
        else:
            message = 'Required fields are messing'
    return render_template('newAsset.html', message=message)


@app.route("/assets", methods=["GET"])
def viewAllAssets():
    assets = db.session.query(Asset).all()
    return render_template("viewAllAssets.html", assets=assets)


@app.route('/viewasset', methods=['GET', 'POST'])
def viewAsset():
    message = None
    asset = None
    if request.form:
        name = request.form.get('name')
        if name != '':
            checkexistence = db.session.query(Asset).filter_by(name=name).first()
            if not checkexistence:
                message = 'Asset not found!'
            else:
                asset = db.session.query(Asset).filter_by(name=name).first()
        else:
            message = 'Required fields are messing'
    return render_template('viewAsset.html', asset=asset,
                           message=message)


@app.route('/updateAsset', methods=['GET', 'POST'])
def updateAsset():
    message = None
    asset = None
    if request.form:
        name = request.form.get('name')
        newPrice = request.form.get('closingPrice')
        if newPrice == '0':
            message = "New price can't be zero"
        elif name != '' and newPrice != '':
            checkexistence = db.session.query(Asset).filter_by(name=name).first()
            if not checkexistence:
                message = 'Asset not found!'
            else:
                asset = db.session.query(Asset).filter_by(name=name).first()
                asset.closingPrice = newPrice
                db.session.commit()
                return render_template('asset.html', asset=asset)
        else:
            message = 'Required fields are messing'
    return render_template('updateAsset.html', message=message)


def getAssets():
    return db.session.query(Asset).all()


@app.route('/userPortoflio', methods=['GET', 'POST'])
def createPortoflio():
    message = None
    assets = getAssets()
    if request.form:
        subject = request.form.get('subject')
        userEmail = request.form.get('email')
        selectedAssets = request.form.getlist('assets')
        amountOfInvestement = []
        numOfStocks = []
        assetsCounter = 0
        for counter in range(1, len(assets) + 1):
            assetInvestement = request.form.get('amountofinvestement' + str(counter))
            if assetInvestement != '':
                closingPrice = \
                    db.session.query(Asset).filter_by(name=selectedAssets[assetsCounter]).first().closingPrice
                stocks = int(assetInvestement) / int(closingPrice)
                amountOfInvestement.append(assetInvestement)
                numOfStocks.append(str(int(stocks)))
                assetsCounter = assetsCounter + 1
        if userEmail == '' or not selectedAssets \
                or not amountOfInvestement or \
                    len(selectedAssets) != len(amountOfInvestement):
            message = 'Required fields are messing'
        else:
            user = db.session.query(User).filter_by(email=userEmail).first()
            if user:
                userId = user.id
                checkexistence = db.session.query(UserAssets).filter_by(subject=subject,
                                                                    userID=userId).first()
                if checkexistence:
                    message = 'Portoflio Already Exist!'
                else:
                    assetsCol = logic.collectColoumnData(logic,
                                                         selectedAssets)
                    amountOfInvestementCol = logic.collectColoumnData(logic,
                                                 amountOfInvestement)
                    numOfStocksCol = logic.collectColoumnData(logic,
                                                              numOfStocks)
                    userAssetsObj = UserAssets(
                        name=assetsCol,
                        amountOfInvestemnt=amountOfInvestementCol,
                        status='',
                        userID=userId,
                        subject=subject,
                        numOfStocks=numOfStocksCol,
                    )
                    db.session.add(userAssetsObj)
                    db.session.commit()
            else:
                message = 'Email is wrong!'
    return render_template('portoflio.html', assets=assets,
                           message=message)

@app.route('/choosePortflio', methods=['GET', 'POST'])
def choosePortoflio():
    portofliosSubject = []
    message = None
    userEmail = None
    if request.form:
        userEmail = request.form.get('email')
        if userEmail != '':
            user = db.session.query(User).filter_by(email=userEmail).first()
            if user:
                userId = user.id
                userAssets =  db.session.query(UserAssets).filter_by(userID=userId)
                for asset in userAssets:
                    portofliosSubject.append(asset.subject)
            else:
                message = 'Email is wrong!'
        else:
            message = 'Required fields are messing'
    return render_template('showAllPotroflios.html',
                           portofliosSubject=portofliosSubject,
                           userEmail=userEmail, message=message)


@app.route('/portflioStatus/<portfolioSubject>/<userEmail>',
           methods=['GET', 'POST'])
def getPortfolioStatus(portfolioSubject, userEmail):
    assetsStatus = []
    user = db.session.query(User).filter_by(email=userEmail).first()
    userId = user.id
    userPortflio = db.session.query(UserAssets).filter_by(userID=userId,
                                               subject=portfolioSubject).first()
    assets = userPortflio.name
    amountOfInvestement = userPortflio.amountOfInvestemnt
    allAssets = logic.seperateColumnData(logic, assets)
    allAmountOfInvestement = logic.seperateColumnData(logic,amountOfInvestement)
    allNumOfStocks = logic.seperateColumnData(logic,userPortflio.numOfStocks)
    for assetCounter in range(len(allAssets)):
        assetClosingPrice = \
            db.session.query(Asset).filter_by(name=allAssets[assetCounter]).first().closingPrice
        assetNumOfStocks = allNumOfStocks[assetCounter]
        assetsStatus.append(str(int(assetNumOfStocks)* int(assetClosingPrice)))
    statusCol = logic.collectColoumnData(logic, assetsStatus)
    userPortflio.status = statusCol
    db.session.commit()
    return render_template('portflioStatus.html', assets=allAssets,
                           amountOfInvetement=allAmountOfInvestement,
                           assetStatus=assetsStatus)
if __name__ == '__main__':
    app.secret_key = 'some secret key'
    app.run(host='0.0.0.0', port=port)