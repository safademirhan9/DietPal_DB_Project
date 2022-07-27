from datetime import date
from enum import unique

from sqlalchemy.sql.sqltypes import Date
from database import Base
from flask_security import UserMixin
from sqlalchemy import create_engine, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, Text, Float
from werkzeug.security import generate_password_hash, check_password_hash


# class Besinler(Base):
#     __tablename__ = 'Besinler'
#     besin_adi = Column(String(255), primary_key=True)
#     karbonhidrat_degeri = Column(String(255))
#     protein_degeri = Column(String(255))
#     yag_degeri = Column(String(255))
#     kalori = Column(Integer)

class Besin(Base):
    __tablename__ = 'Besinler'
    besin_adi = Column(String,primary_key = True)
    karbonhidrat_degeri = Column(Float)
    protein_degeri = Column(Float)
    yag_degeri = Column(Float)
    kalori = Column(Integer)

class Kullanicilar(Base, UserMixin):
    __tablename__ = 'kullanicilar'
    kullanici_adi = Column(String(255), primary_key=True)
    sifre = Column(Text)
    kayit_tarihi = Column(Date)

class Ogunler(Base):
    __tablename__ = 'ogunler'
    a_id = Column(Integer, primary_key=True, autoincrement=True)
    kullanici_adi = Column(String(255), ForeignKey('kullanicilar.kullanici_adi'))
    besin_adi = Column(String(255), ForeignKey('Besinler.besin_adi'))
    ogun_zamani = Column(String(255))
    miktar = Column(Integer)
    toplam_kalori = Column(Integer)
    tarih = Column(Date)

class Kisisel_Bilgiler(Base):
    __tablename__ = 'kisisel_bilgiler'
    kullanici_adi = Column(String(255), ForeignKey('kullanicilar.kullanici_adi'), primary_key=True)
    ad = Column(String(255))
    soyad = Column(String(255))
    email = Column(String(255))
    cinsiyet = Column(String(5))
    boy = Column(String(4))
    dogum_tarihi = Column(Date)
    yas = Column(Integer)
    lokasyon = Column(String(255))
    kalori_ihtiyaci = Column(Integer)

class Icilen_Su(Base):
    __tablename__ = 'icilen_su'
    sid = Column(Integer, primary_key=True,autoincrement=True)
    kullanici_adi = Column(String(255), ForeignKey('kullanicilar.kullanici_adi'))
    su_miktari = Column(Integer)
    icilme_tarihi = Column(Date)

class Kilo(Base):
    __tablename__ = 'kilo'
    kid = Column(Integer, primary_key=True, autoincrement=True)
    kullanici_adi = Column(String(255), ForeignKey('kullanicilar.kullanici_adi'), primary_key=True)
    kg = Column(Integer)
    olusturulma_tarihi = Column(Date)
    
class Tarif(Base):
    __tablename__ = 'Tarifler'
    tarif_id = Column(Integer(),primary_key = True, autoincrement= True)
    tarif_adi = Column(String)
    yemek_tarifi = Column(String)
    olusturulma_tarihi = Column(Date)
    kullanici_adi = Column(String, ForeignKey('kullanicilar.kullanici_adi'))



class Egzersizler(Base):
    __tablename__ = 'Egzersizler'
    e_id =Column(Integer, primary_key = True)
    egzersiz_adi = Column(String())
    yakilan_kalori = Column(Integer())

class Gunluk_Aktivite(Base):
    __tablename__ = 'Gunluk_Aktivite'
    aktivite_id = Column(Integer, primary_key=True, autoincrement=True)
    e_id = Column(Integer)
    kullanici_adi = Column(String)
    egzersiz_adi = Column(String)  
    tarih = Column(Date)
    ForeignKeyConstraint(['e_id','kullanici_adi','egzersiz_adi'],['Egzersizler.e_id','kullanicilar.kullanici_adi','Egzersizler.egzersiz_adi'])


class HazirDiyetler(Base):
    __tablename__ = 'HazirDiyetler'
    diyet_adi = Column(String(), primary_key=True)
    diyet_icerigi = Column(String())
    diyet_kalori = Column(Float())

class Gonderiler(Base):
    __tablename__ = 'Gonderiler'
    gonderi_adi = Column(Integer(), primary_key=True)
    kullanici_adi = Column(String())
    # Image type kullan
    resim = Column(String)
    resim_aciklamasi = Column(String())
    olusturulma_tarihi = Column(Date())