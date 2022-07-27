from enum import unique
import re
from flask import Flask, render_template, request, redirect, flash, session, url_for
import flask
import hashlib
from flask.scaffold import F
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref, lazyload, query
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.functions import now
from database import db_session, init_db
from models import Besin, Icilen_Su, Kilo, Kisisel_Bilgiler, Ogunler, Kullanicilar,Tarif,Egzersizler,Gunluk_Aktivite,HazirDiyetler#,Besinler
from datetime import datetime, date
#from utils import verify_password


app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#app.config['SECRET_KEY'] = 'super-secret'
# Generate a nice key using secrets.token_urlsafe()
#app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')

#app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')


# Setup Flask-Security
#user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
#security = Security(app, user_datastore)



ENV = "dev"

if(ENV == "dev"):
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://postgres:12345@localhost/Dietpal'

else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = '' #burayı ayarlamayı unutma

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def password_check(passwd):
      
    SpecialSym =['$', '@', '#', '%']
    val = True
      
    if len(passwd) < 7:
        
        val = False
          
    elif len(passwd) > 20:
        
        val = False
          
    elif not any(char.isdigit() for char in passwd):
       
        val = False
          
    elif not any(char.isupper() for char in passwd):
       
        val = False
          
    elif not any(char.islower() for char in passwd):
        
        val = False
          
    elif not any(char in SpecialSym for char in passwd):
       
        val = False

    return val


@app.before_first_request
def create_user():
    init_db()
    #user_datastore.create_user(username='y', password=generate_password_hash('hash_p'))
    if db_session.query(Kullanicilar).filter(Kullanicilar.kullanici_adi == 'ozlem').count() == 0:
        data = Kullanicilar(kullanici_adi='ozlem', sifre='ozlem')
        db_session.add(data)
        db_session.commit()


    

@app.route('/')
@app.route('/index.html')
@app.route('/index')
@app.route('/index/<username>')
@app.route('/home')
def index():
    if 'username' in session:
        kisisel_bilgiler = db_session.query(Kisisel_Bilgiler).filter(Kisisel_Bilgiler.kullanici_adi == session['username']).first()
        kilo = db_session.query(Kilo).filter(Kilo.kullanici_adi == session['username'], Kilo.olusturulma_tarihi == date.today()).first()
        su_miktari = db_session.query(Icilen_Su).filter(Icilen_Su.icilme_tarihi == date.today()).count()
        alinan_kaloriler = db_session.query(Ogunler).filter(Ogunler.tarih == date.today()).all()
    
        alinan_kalori = 0
        for kalori in alinan_kaloriler:
            alinan_kalori = alinan_kalori + kalori.toplam_kalori
        return render_template('kisisel_bilgiler.html', kisisel_bilgiler=kisisel_bilgiler, session_name=session['username'], kilo=kilo, su_miktari=su_miktari, alinan_kalori=alinan_kalori)
    return render_template('login.html')

#region Register
@app.route('/register.html')
@app.route('/register')
def register2():
    return render_template('register.html')


@app.route('/register.html', methods=['POST'])
@app.route('/register', methods=['POST'])
def register():
    kullanici_adi = request.form['kullanici_adi']
    sifre = request.form['sifre']
    ad = request.form['ad']
    soyad = request.form['soyad']
    email = request.form['email']
    cinsiyet = request.form['cinsiyet']
    boy = request.form['boy']
    kilo = request.form['kilo']
    dogum_tarihi = request.form['dogum_tarihi']
    lokasyon = request.form['lokasyon']

    if db_session.query(Kullanicilar).filter(Kullanicilar.kullanici_adi == kullanici_adi).count() == 0:
        data = Kullanicilar(kullanici_adi=kullanici_adi, sifre=sifre)
        db_session.add(data)
        db_session.commit()

        data = Kisisel_Bilgiler(kullanici_adi=kullanici_adi,ad=ad, soyad=soyad, email=email, cinsiyet=cinsiyet, boy=boy, dogum_tarihi=dogum_tarihi, lokasyon=lokasyon)
        db_session.add(data)
        db_session.commit()

        data = Kilo(kullanici_adi=kullanici_adi, kg=kilo, olusturulma_tarihi=date.today())
        db_session.add(data)
        db_session.commit()

        return render_template('login.html')

    return render_template('register.html', failed="Bu kullanıcı adında bir kayıt vardır.")


#endregion

#region Login
@app.route('/login.html')
@app.route('/login')
def login2():
    session.pop('username', None)
    return render_template('login.html')

@app.route('/login.html', methods=['POST'])
@app.route('/login', methods=['POST'])
def login3():
    kullanici_adi = request.form['kullanici_adi']
    sifre = request.form['sifre']
    
    if db_session.query(Kullanicilar).filter(Kullanicilar.kullanici_adi == kullanici_adi, Kullanicilar.sifre == sifre).count() == 1:
        session['username'] = kullanici_adi

        kisisel_bilgiler = db_session.query(Kisisel_Bilgiler).filter(Kisisel_Bilgiler.kullanici_adi == session['username']).first()
        kilo = db_session.query(Kilo).filter(Kilo.kullanici_adi == session['username'], Kilo.olusturulma_tarihi == date.today()).first()
        su_miktari = db_session.query(Icilen_Su).filter(Icilen_Su.icilme_tarihi == date.today()).count()
        alinan_kaloriler = db_session.query(Ogunler).filter(Ogunler.tarih == date.today()).all()
    
        alinan_kalori = 0
        for kalori in alinan_kaloriler:
            alinan_kalori = alinan_kalori + kalori.toplam_kalori
        return render_template('kisisel_bilgiler.html', kisisel_bilgiler=kisisel_bilgiler, session_name=session['username'], kilo=kilo, su_miktari=su_miktari, alinan_kalori=alinan_kalori)

    return render_template('login.html', failed="Bilgileriniz yanlış.")


#endregion

#region Kahvaltı
@app.route('/kahvalti_ekle.html')
@app.route('/kahvalti_ekle')
def kahvalti():
    besinler = db_session.query(Besin).all()
    kahvalti = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "kahvalti", Ogunler.tarih == date.today()).all()
    return render_template('kahvalti_ekle.html', besinler=besinler, kahvalti=kahvalti, session_name=session['username'])
    
@app.route('/kahvalti_ekle', methods=['POST'])
def kahvalti_ekle():
    besinler = db_session.query(Besin).all()
    
    besin_adi = request.form['besin_adi']
    dt_string = date.today()

    besin_kalori = db_session.query(Besin).filter(Besin.besin_adi == besin_adi).first()

    data = Ogunler(kullanici_adi=session['username'],besin_adi=besin_adi, ogun_zamani="kahvalti", miktar=1, toplam_kalori=besin_kalori.kalori, tarih=dt_string)
    db_session.add(data)
    db_session.commit()
    kahvalti = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "kahvalti", Ogunler.tarih==date.today()).all()
    return render_template('kahvalti_ekle.html', besinler=besinler, kahvalti=kahvalti, session_name=session['username'], success="1")

@app.route('/kahvalti_ekle/sil', methods=['POST'])
def kahvalti_sil():
    besinler = db_session.query(Besin).all()
    
    Ogunler.query.filter(Ogunler.a_id == request.form['ogunid']).delete()
    db_session.commit()
    kahvalti = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "kahvalti", Ogunler.tarih == date.today()).all()
    return render_template('kahvalti_ekle.html', besinler=besinler, kahvalti=kahvalti, session_name=session['username'], success="1")

#endregion      

#region Öğle Yemeği
@app.route('/oglenyemegi_ekle.html')
@app.route('/oglenyemegi_ekle')
def oglenyemegi():
    besinler = db_session.query(Besin).all()
    oglenyemegi = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "oglen_yemegi", Ogunler.tarih==date.today()).all()
    return render_template('oglenyemegi_ekle.html', besinler=besinler, oglenyemegi=oglenyemegi, session_name=session['username'])
    
@app.route('/oglenyemegi_ekle', methods=['POST'])
def oglenyemegi_ekle():
    besinler = db_session.query(Besin).all()
    
    besin_adi = request.form['besin_adi']
    dt_string = date.today()

    besin_kalori = db_session.query(Besin).filter(Besin.besin_adi == besin_adi).first()

    data = Ogunler(kullanici_adi=session['username'],besin_adi=besin_adi, ogun_zamani="oglen_yemegi", miktar=1, toplam_kalori=besin_kalori.kalori, tarih=dt_string)
    db_session.add(data)
    db_session.commit()
    oglenyemegi = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "oglen_yemegi", Ogunler.tarih == date.today()).all()
    return render_template('oglenyemegi_ekle.html', besinler=besinler, oglenyemegi=oglenyemegi, session_name=session['username'], success="1")

@app.route('/oglenyemegi_ekle/sil', methods=['POST'])
def oglenyemegi_sil():
    besinler = db_session.query(Besin).all()
    
    Ogunler.query.filter(Ogunler.a_id == request.form['ogunid']).delete()
    db_session.commit()
    oglenyemegi = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "oglen_yemegi", Ogunler.tarih==date.today()).all()
    return render_template('oglenyemegi_ekle.html', besinler=besinler, oglenyemegi=oglenyemegi, session_name=session['username'], success="1")

#endregion      

#region Akşam Yemeği
@app.route('/aksamyemegi_ekle.html')
@app.route('/aksamyemegi_ekle')
def aksamyemegi():
    besinler = db_session.query(Besin).all()
    aksamyemegi = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "aksam_yemegi", Ogunler.tarih==date.today()).all()
    return render_template('aksamyemegi_ekle.html', besinler=besinler, aksamyemegi=aksamyemegi, session_name=session['username'])
    
@app.route('/aksamyemegi_ekle', methods=['POST'])
def aksamyemegi_ekle():
    besinler = db_session.query(Besin).all()
    
    besin_adi = request.form['besin_adi']
    dt_string = date.today()

    besin_kalori = db_session.query(Besin).filter(Besin.besin_adi == besin_adi).first()

    data = Ogunler(kullanici_adi=session['username'],besin_adi=besin_adi, ogun_zamani="aksam_yemegi", miktar=1, toplam_kalori=besin_kalori.kalori, tarih=dt_string)
    db_session.add(data)
    db_session.commit()
    aksamyemegi = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "aksam_yemegi", Ogunler.tarih==date.today()).all()
    return render_template('aksamyemegi_ekle.html', besinler=besinler, aksamyemegi=aksamyemegi, session_name=session['username'], success="1")

@app.route('/aksamyemegi_ekle/sil', methods=['POST'])
def aksamyemegi_sil():
    besinler = db_session.query(Besin).all()
    
    Ogunler.query.filter(Ogunler.a_id == request.form['ogunid']).delete()
    db_session.commit()
    aksamyemegi = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "aksam_yemegi", Ogunler.tarih==date.today()).all()
    return render_template('aksamyemegi_ekle.html', besinler=besinler, aksamyemegi=aksamyemegi, session_name=session['username'], success="1")

#endregion      

#region Atıştırmalık
@app.route('/atistirmalik_ekle.html')
@app.route('/atistirmalik_ekle')
def atistirmalik():
    besinler = db_session.query(Besin).all()
    atistirmalik = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "atistirmalik", Ogunler.tarih==date.today()).all()
    return render_template('atistirmalik_ekle.html', besinler=besinler, atistirmalik=atistirmalik, session_name=session['username'])
    
@app.route('/atistirmalik_ekle', methods=['POST'])
def atistirmalik_ekle():
    besinler = db_session.query(Besin).all()
    
    besin_adi = request.form['besin_adi']
    dt_string = date.today()

    besin_kalori = db_session.query(Besin).filter(Besin.besin_adi == besin_adi).first()

    data = Ogunler(kullanici_adi=session['username'],besin_adi=besin_adi, ogun_zamani="atistirmalik", miktar=1, toplam_kalori=besin_kalori.kalori, tarih=dt_string)
    db_session.add(data)
    db_session.commit()
    atistirmalik = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "atistirmalik", Ogunler.tarih==date.today()).all()
    return render_template('atistirmalik_ekle.html', besinler=besinler, atistirmalik=atistirmalik, session_name=session['username'], success="1")

@app.route('/atistirmalik_ekle/sil', methods=['POST'])
def atistirmalik_sil():
    besinler = db_session.query(Besin).all()
    
    Ogunler.query.filter(Ogunler.a_id == request.form['ogunid']).delete()
    db_session.commit()
    atistirmalik = db_session.query(Ogunler).filter(Ogunler.ogun_zamani == "atistirmalik", Ogunler.tarih==date.today()).all()
    return render_template('atistirmalik_ekle.html', besinler=besinler, atistirmalik=atistirmalik, session_name=session['username'], success="1")

#endregion      

#region Kişisel Bilgiler
@app.route('/kisisel_bilgiler.html')
@app.route('/kisisel_bilgiler')
def kisisel_bilgiler():
    if 'username' in session:
        kisisel_bilgiler = db_session.query(Kisisel_Bilgiler).filter(Kisisel_Bilgiler.kullanici_adi == session['username']).first()
        kilo = db_session.query(Kilo).filter(Kilo.kullanici_adi == session['username'], Kilo.olusturulma_tarihi == date.today()).first()
        su_miktari = db_session.query(Icilen_Su).filter(Icilen_Su.icilme_tarihi == date.today()).count()
        alinan_kaloriler = db_session.query(Ogunler).filter(Ogunler.tarih == date.today()).all()
    
        alinan_kalori = 0
        for kalori in alinan_kaloriler:
            alinan_kalori = alinan_kalori + kalori.toplam_kalori
        
        return render_template('kisisel_bilgiler.html', kisisel_bilgiler=kisisel_bilgiler, session_name=session['username'], kilo=kilo, su_miktari=su_miktari, alinan_kalori=alinan_kalori)
    return render_template('login.html')

@app.route('/kisisel_bilgiler/su', methods=['POST'])
def su_ekle():
    kisisel_bilgiler = db_session.query(Kisisel_Bilgiler).filter(Kisisel_Bilgiler.kullanici_adi == session['username']).first()
    kilo = db_session.query(Kilo).filter(Kilo.kullanici_adi == session['username'], Kilo.olusturulma_tarihi == date.today()).first()
    alinan_kaloriler = db_session.query(Ogunler).filter(Ogunler.tarih == date.today()).all()
    alinan_kalori = 0
    for kalori in alinan_kaloriler:
        alinan_kalori = alinan_kalori + kalori.toplam_kalori
    
    dt_string = date.today()

    kullanici_adi = request.form['kullanici_adi']

    data = Icilen_Su(kullanici_adi=kullanici_adi, su_miktari=1, icilme_tarihi=dt_string)
    db_session.add(data)
    db_session.commit()
    su_miktari = db_session.query(Icilen_Su).filter(Icilen_Su.icilme_tarihi == date.today()).count()
    return render_template('kisisel_bilgiler.html', kisisel_bilgiler=kisisel_bilgiler, session_name=session['username'], kilo=kilo, su_miktari=su_miktari, alinan_kalori=alinan_kalori)

@app.route('/kisisel_bilgiler-edit')
def kisiselbilgiler_duzenle():
    kisisel_bilgiler = db_session.query(Kisisel_Bilgiler).filter(Kisisel_Bilgiler.kullanici_adi == session['username']).first()
    kilo = db_session.query(Kilo).filter(Kilo.kullanici_adi == session['username'], Kilo.olusturulma_tarihi == date.today()).first()
    return render_template('kisisel_bilgiler-edit.html', kisisel_bilgiler=kisisel_bilgiler, session_name=session['username'], kilo=kilo)

@app.route('/kisisel_bilgiler-edit', methods=['POST'])
def kisiselbilgiler_duzenle2():
    kisisel_bilgiler = db_session.query(Kisisel_Bilgiler).filter(Kisisel_Bilgiler.kullanici_adi == session['username']).first()
    
    ad = request.form['ad']
    soyad = request.form['soyad']
    email = request.form['email']
    cinsiyet = request.form['cinsiyet']
    boy = request.form['boy']
    kilo = request.form['kilo']
    dogum_tarihi = request.form['dogum_tarihi']
    lokasyon = request.form['lokasyon']
    dt_string = date.today()


    kb = Kisisel_Bilgiler.query.filter_by(kullanici_adi=session['username']).first()
    kb.ad = ad
    kb.soyad = soyad
    kb.email = email
    kb.cinsiyet = cinsiyet
    kb.boy = boy
    kb.dogum_tarihi = dogum_tarihi
    kb.lokasyon = lokasyon
    db_session.commit()

    data = Kilo(kullanici_adi=session['username'], kg=kilo, olusturulma_tarihi=dt_string)
    db_session.add(data)
    db_session.commit()

    kilo = db_session.query(Kilo).filter(Kilo.kullanici_adi == session['username'], Kilo.olusturulma_tarihi == date.today()).first()
    su_miktari = db_session.query(Icilen_Su).filter(Icilen_Su.icilme_tarihi == date.today()).count()
    alinan_kaloriler = db_session.query(Ogunler).filter(Ogunler.tarih == date.today()).all()
    alinan_kalori = 0
    for kalori in alinan_kaloriler:
        alinan_kalori = alinan_kalori + kalori.toplam_kalori
    
    

    return render_template('kisisel_bilgiler.html', kisisel_bilgiler=kisisel_bilgiler, session_name=session['username'], kilo=kilo,  su_miktari=su_miktari, alinan_kalori=alinan_kalori)

#endregion      




# region Merge

@app.route('/gunlukaktiviteekle')
def gunlukaktiviteek():
    egzersizler = db_session.query(Egzersizler).all()
    gunlukaktivite = db_session.query(Gunluk_Aktivite).filter(Gunluk_Aktivite.kullanici_adi == session['username'], Gunluk_Aktivite.tarih == date.today()).all()
    return render_template('gunluk_aktivite.html', egzersiz=egzersizler, gunlukaktivite=gunlukaktivite, session_name=session['username'])
    

@app.route('/gunlukaktiviteekle', methods=['POST'])
def gunlukaktiviteekle():
    
    e_id= request.form['e_id']
    dt_string = date.today()

    egzersizler = Egzersizler.query.all()
    egzersiz = db_session.query(Egzersizler).filter(Egzersizler.e_id == e_id).first()    
    data = Gunluk_Aktivite(kullanici_adi = session['username'],e_id = e_id,tarih = dt_string,egzersiz_adi=egzersiz.egzersiz_adi)
    db_session.add(data)
    db_session.commit()
   
    gunlukaktivite = db_session.query(Gunluk_Aktivite).filter(Gunluk_Aktivite.kullanici_adi == session['username'], Gunluk_Aktivite.tarih == date.today()).all()
    return render_template('gunluk_aktivite.html', egzersiz=egzersizler, gunlukaktivite=gunlukaktivite, session_name=session['username'], success="1")



@app.route('/gunlukaktivitesil', methods=['POST'])
def kahvgunlukaktivitesil():
    
    aktivite = Gunluk_Aktivite.query.filter(Gunluk_Aktivite.e_id == request.form['e_id']).first()
    db_session.delete(aktivite)
    db_session.commit()
    gunlukaktivite = db_session.query(Gunluk_Aktivite).filter(Gunluk_Aktivite.kullanici_adi == session['username'], Gunluk_Aktivite.tarih == date.today()).all()
   
    egzersizler = db_session.query(Egzersizler).all()

    return render_template('gunluk_aktivite.html', egzersiz=egzersizler, gunlukaktivite=gunlukaktivite, session_name=session['username'], success="1")


@app.route('/tarifler')
def tarifler():
    tarifler = Tarif.query.all()
    return render_template('tarifler.html', tarifler = tarifler)


@app.route('/besinler')
def besinler():
    besinler = Besin.query.all()
    return render_template('besinler.html',besinler = besinler)



@app.route('/besinekle', methods = ['POST'])
def besinekle():
    if request.method == 'POST':
        yeni_besin = Besin (besin_adi= request.form['besin_adi'], karbonhidrat_degeri= request.form['karbonhidrat_degeri'], protein_degeri= request.form['protein_degeri'], yag_degeri= request.form['yag_degeri'], kalori=request.form['kalori']) 
        db_session.add(yeni_besin)
        db_session.commit()
        return redirect(url_for('besinler'))

@app.route('/tarifekle', methods=['POST'])
def tarifekle():
    if request.method == 'POST':
        yeni_tarif = Tarif(tarif_adi= request.form['tarif_adi'], yemek_tarifi= request.form['yemek_tarifi'], olusturulma_tarihi = date.today(), kullanici_adi = session['username'])
        db_session.add(yeni_tarif)
        db_session.commit()
        return (redirect(url_for('tarifler')))

@app.route('/tarifsil', methods= ['POST'])
def tarifsil():
    tarif_id = request.form['tarif_id']
    silinecek_tarif = Tarif.query.filter_by(tarif_id = tarif_id).first()
    db_session.delete(silinecek_tarif)
    db_session.commit()    
    return redirect(url_for('tarifler'))

@app.route('/besinsil', methods = ['POST'])
def besinsil():
    besin_adi = request.form['besin_adi']
    silinecek_besin = Besin.query.filter_by(besin_adi = besin_adi).first()
    db_session.delete(silinecek_besin)
    db_session.commit()
    return redirect(url_for('besinler'))

@app.route('/besinduzenle', methods = ['POST'])
def besinduzenle():
    besin_adi =request.form['besin_adi']
    return render_template('besinduzenle.html',besin_adi = besin_adi)

@app.route('/besinduzenle2', methods=['POST'])
def besinduzenle2():
    besin_adi = request.form['besin_adi']
    duzenlenecek_besin = Besin.query.filter_by(besin_adi=besin_adi).first()

    yeni_ad = request.form['besin_adi']
    yeni_karbonhidrat = request.form['karbonhidrat_degeri']
    yeni_protein = request.form['protein_degeri']
    yeni_yag = request.form['yag_degeri']
    yeni_kalori = request.form['kalori']

    if yeni_ad == '':
        yeni_ad = duzenlenecek_besin.besin_adi
    if yeni_karbonhidrat == '':
        yeni_karbonhidrat = duzenlenecek_besin.karbonhidrat_degeri
    if yeni_protein == '':
        yeni_protein = duzenlenecek_besin.protein_degeri
    if yeni_yag == '':
        yeni_yag = duzenlenecek_besin.yag_degeri
    if yeni_kalori == '':
        yeni_kalori=duzenlenecek_besin.kalori

    duzenlenecek_besin.besin_adi = yeni_ad
    duzenlenecek_besin.karbonhidrat_degeri = yeni_karbonhidrat
    duzenlenecek_besin.protein_degeri = yeni_protein
    duzenlenecek_besin.yag_degeri = yeni_yag
    duzenlenecek_besin.kalori = yeni_kalori

    db_session.commit()

    return redirect(url_for('besinler')) 

@app.route('/tarifduzenle',methods = ['POST'])
def tarifduzenle():
    tarif = Tarif.query.filter_by(tarif_id = request.form['tarif_id']).first()
    tarif_adi = tarif.tarif_adi
    return render_template('tarifduzenle.html', tarif_id = request.form['tarif_id'], tarif_adi = tarif_adi)


@app.route('/tarifduzenle2', methods = ['POST'])
def tarifduzenle2():
    duzenlenecek_tarif= Tarif.query.filter_by(tarif_id = request.form['tarif_id']).first()
    
    yeni_adi = request.form['tarif_adi']
    yeni_yemek_tarifi = request.form['yemek_tarifi']

    if yeni_adi == '':
        yeni_adi = duzenlenecek_tarif.tarif_adi
    if yeni_yemek_tarifi == '':
        yeni_yemek_tarifi = duzenlenecek_tarif.yemek_tarifi


    duzenlenecek_tarif.tarif_adi = yeni_adi
    duzenlenecek_tarif.yemek_tarifi = yeni_yemek_tarifi

    db_session.commit()
    return redirect(url_for('tarifler'))

#endregion

# Safa Demirhan
@app.route('/egzersizduzenle', methods = ['POST'])
def egzersizduzenle():
    egzersiz = Egzersizler.query.filter_by(e_id = request.form['e_id']).first()
    egzersiz_adi = egzersiz.egzersiz_adi
    return render_template('egzersizduzenle.html', e_id = request.form['e_id'], egzersiz_adi = egzersiz_adi)

@app.route('/egzersizduzenle2', methods=['POST'])
def egzersizduzenle2():
    duzenlenecek_egzersiz= Egzersizler.query.filter_by(e_id = request.form['e_id']).first()

    yeni_ad = request.form['egzersiz_adi']
    yeni_kalori = request.form['yakilan_kalori']

    if yeni_ad == '':
        yeni_ad = duzenlenecek_egzersiz.egzersiz_adi
    if yeni_kalori == '':
        yeni_kalori = duzenlenecek_egzersiz.yakilan_kalori

    duzenlenecek_egzersiz.egzersiz_adi = yeni_ad
    duzenlenecek_egzersiz.yakilan_kalori = yeni_kalori
    db_session.commit()
    return redirect(url_for('egzersizler'))

# Safa Demirhan
@app.route('/hazirdiyetduzenle', methods = ['POST'])
def hazirdiyetduzenle():
    #besin = Besin.query.filter_by(diyet_adi = request.form['diyet_adi'])
    diyet_adi =request.form['diyet_adi']
    return render_template('hazirdiyetduzenle.html',diyet_adi = diyet_adi)

@app.route('/hazirdiyetduzenle2', methods=['POST'])
def hazirdiyetduzenle2():
    diyet_adi = request.form['diyet_adi']
    duzenlenecek_hazirdiyet = HazirDiyetler.query.filter_by(diyet_adi=diyet_adi).first()
    
    yeni_diyet_adi = request.form['diyet_adi']
    yeni_diyet_icerigi = request.form['diyet_icerigi']
    yeni_diyet_kalori = request.form['diyet_kalori']

    if yeni_diyet_adi == '':
        yeni_diyet_adi = duzenlenecek_hazirdiyet.diyet_adi
    if yeni_diyet_icerigi == '':
        yeni_diyet_icerigi = duzenlenecek_hazirdiyet.diyet_icerigi
    if yeni_diyet_kalori == '':
        yeni_diyet_kalori = duzenlenecek_hazirdiyet.diyet_kalori

    duzenlenecek_hazirdiyet.diyet_adi = yeni_diyet_adi
    duzenlenecek_hazirdiyet.diyet_icerigi = yeni_diyet_icerigi
    duzenlenecek_hazirdiyet.diyet_kalori = yeni_diyet_kalori
    db_session.commit()
    return redirect(url_for('hazir_diyetler')) 


# Safa Demirhan
@app.route('/hazirdiyetsil', methods = ['POST'])
def hazirdiyetsil():
    diyet_adi = request.form['diyet_adi']
    silinecek_tarif = HazirDiyetler.query.filter_by(diyet_adi = diyet_adi).first()
    db_session.delete(silinecek_tarif)
    db_session.commit()
    flash('Hazır diyet silinmiştir!', 'success')
    return redirect(url_for('hazir_diyetler'))

# Safa Demirhan
@app.route('/egzersizsil', methods = ['POST'])
def egzersizsil():
    e_id = request.form['e_id']
    silinecek_egzersiz = Egzersizler.query.filter_by(e_id = e_id).first()
    db_session.delete(silinecek_egzersiz)
    db_session.commit()
    flash('Egzersiz silinmiştir!', 'success')
    return redirect(url_for('egzersizler'))



# Safa Demirhan
@app.route('/hazirdiyetekle', methods = ['POST'])
def hazirdiyetekle():
    if request.method == 'POST':
        yeni_hazir_diyet = HazirDiyetler(diyet_adi= request.form['diyet_adi'], diyet_icerigi= request.form['diyet_icerigi'], diyet_kalori= request.form['diyet_kalori']) 
        db_session.add(yeni_hazir_diyet)
        db_session.commit()
        flash('Hazır diyet eklenmiştir!', 'success')
        return redirect(url_for('hazir_diyetler'))

@app.route('/egzersizekle', methods = ['POST'])
def egzersizekle():
    if request.method == 'POST':
        yeni_egzersiz = Egzersizler(egzersiz_adi= request.form['egzersiz_adi'], yakilan_kalori= request.form['yakilan_kalori']) 
        db.session.add(yeni_egzersiz)
        db.session.commit()
        flash('Egzersiz eklenmiştir!', 'success')
        return redirect(url_for('egzersizler'))

# Safa Demirhan
@app.route('/hazir_diyetler')
def hazir_diyetler():
    hazir_diyetler = HazirDiyetler.query.all()
    return render_template('hazir_diyetler.html',hazir_diyetler = hazir_diyetler)

# Safa Demirhan
@app.route('/egzersizler')
def egzersizler():
    e_id = Egzersizler.query.all()
    return render_template('egzersizler.html',e_id = e_id)


if __name__ == '__main__':
    app.run(debug=True)

