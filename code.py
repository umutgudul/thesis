from datetime import datetime, timedelta
import random
toplam1 = 0
toplam2 = 0
toplam3=0

class OtobusHatti:
    class Araba:
        def __init__(self, adi, menzil):
            self.adi = adi
            self.menzil = menzil
            self.kalan_menzil = menzil
            self.sarj_durumu = 100
            self.sarj_istasyonu_gelis = None
            self.sarj_istasyonu_cikis = None
            self.garaja_gelis = None
            self.garajdan_cikis = None
            self.hatlarda_dolasanlar = []
            self.kullanilan_km = 0
            self.toplam_sarj_suresi = 0
            self.toplam_tur_sayisi = 0
            self.mevcut_hat = None

    def __init__(self, araclar, hatlar):
        self.araclar = araclar
        self.hatlar = hatlar
        self.garajdaki_araclar = []
        self.sarj_istasyonu_kapasitesi = 1
        self.sarj_istasyonu_doluluk = 0
        self.sarj_istasyonu_kuyrugu = []
        self.kullanilabilir_araclar = [arac for arac in self.araclar if arac.sarj_durumu == 100]
        self.hattin_uzunlugu = {hat["adi"]: hat["uzunluk"] for hat in hatlar}
        self.istatistik = {arac.adi: {"toplam_km": 0, "toplam_sarj_suresi":0,"toplam_tur_sayisi": 0,
                                      "hatlar": {hat["adi"]: 0 for hat in hatlar}} for arac in araclar}
        self.zaman_cizelgesi = []
        self.hat_tur_sayisi = {hat["adi"]: 0 for hat in hatlar}


    def arac_kuyruktan_sarja_gonder(self, saat, gun):
        global toplam1
        global toplam2
        global toplam3
        if self.sarj_istasyonu_kuyrugu:
            arac = self.sarj_istasyonu_kuyrugu.pop(0)
            print(f"{arac.adi} adlı araç şarj istasyonuna yönlendirildi ve şarj ediliyor.")

            if arac.adi.startswith("tip2."):
                sarj_suresi = 5 * (arac.menzil - arac.kalan_menzil) / 6
                arac.kalan_menzil += (sarj_suresi /5) * 6 # 25 dakikada 30 km menzil kazanıyor
                toplam1+=sarj_suresi
                if self.sarj_istasyonu_doluluk > self.sarj_istasyonu_kapasitesi:
                    sarj_suresi = 5 * (arac.menzil - arac.kalan_menzil) / 6
                    arac.kalan_menzil += (sarj_suresi / 5) * 6  # 25 dakikada 30 km menzil kazanıyor
                    toplam3 += sarj_suresi

            else:
                sarj_suresi = (arac.menzil - arac.kalan_menzil) / 2
                arac.kalan_menzil += sarj_suresi * 2
                toplam2 += sarj_suresi
                if self.sarj_istasyonu_doluluk > self.sarj_istasyonu_kapasitesi:
                    sarj_suresi = (arac.menzil - arac.kalan_menzil) / 2
                    arac.kalan_menzil += sarj_suresi * 2
                    toplam2 += sarj_suresi

            arac.sarj_durumu = 100
            varis_saat = saat + timedelta(minutes=sarj_suresi)
            print(f"Şarj Tamamlandı! Varış Saati: {varis_saat.strftime('%H:%M')}, Şarj Süresi: {sarj_suresi} dakika")
            arac.sarj_istasyonu_gelis = saat
            arac.sarj_istasyonu_cikis = varis_saat
            self.sarj_istasyonu_giris_cikis_ekle(arac, saat, varis_saat)
            self.kullanilabilir_araclar.append(arac)
            self.istatistik[arac.adi]["toplam_sarj_suresi"] += sarj_suresi
            self.zaman_cizelgesi.append((gun, saat, f"{arac.adi} şarj istasyonuna yönlendirildi."))
            self.zaman_cizelgesi.append((gun, varis_saat, f"{arac.adi} şarj oldu."))
            print(self.istatistik)
    def rassal_sure_hesapla(self, min_saat, max_saat):
        sure_saat = random.uniform(min_saat, max_saat)
        sure_dakika = sure_saat * 60
        return sure_dakika

    def sefer_yap(self, arac, saat, hat, gun):
        baslangic_menzili = arac.kalan_menzil
        arac.hatlarda_dolasanlar.append(hat["adi"])
        arac.mevcut_hat = hat
        kalan_menzil = baslangic_menzili - self.hattin_uzunlugu[hat["adi"]]
        arac.kalan_menzil = kalan_menzil
        sure = self.rassal_sure_hesapla(hat["min_saat"], hat["max_saat"])
        varis_saat = saat + timedelta(minutes=sure)
        print(f"{saat.strftime('%H:%M')} - {arac.adi} adlı araçla {hat['adi']} hat Sefer tamamlandı! Menzil: {arac.kalan_menzil}/{baslangic_menzili} km, Tamamlanma Süresi: {sure:.2f} dakika, Varış Saati: {varis_saat.strftime('%H:%M')}, Kalan Menzil: {kalan_menzil} km")
        self.istatistik[arac.adi]["toplam_km"] += self.hattin_uzunlugu[hat["adi"]]
        self.istatistik[arac.adi]["toplam_tur_sayisi"] += 1
        self.istatistik[arac.adi]["hatlar"][hat["adi"]] += self.hattin_uzunlugu[hat["adi"]]
        self.zaman_cizelgesi.append((gun, saat, f"{arac.adi} {hat['adi']} hattında sefere çıktı."))
        self.zaman_cizelgesi.append((gun, varis_saat, f"{arac.adi} {hat['adi']} hattında seferi tamamladı."))
        return varis_saat

    def sarj_istasyonu_giris_cikis_ekle(self, arac, gelis, cikis):
        arac.sarj_istasyonu_gelis = gelis
        arac.sarj_istasyonu_cikis = cikis

    def garaja_al(self, arac, saat, gun):
        arac.garaja_gelis = saat
        arac.garajdan_cikis = None
        self.garajdaki_araclar.append(arac)
        print(f"{saat.strftime('%H:%M')} - {arac.adi} adlı araç garaja alındı.")
        self.zaman_cizelgesi.append((gun, saat, f"{arac.adi} garaja alındı."))

    def garajdan_cikar(self, arac, saat, gun):
        if arac in self.garajdaki_araclar:
            arac.garajdan_cikis = saat
            self.kullanilabilir_araclar.append(arac)
            self.garajdaki_araclar.remove(arac)
            print(f"{saat.strftime('%H:%M')} - {arac.adi} adlı araç garajdan çıkarıldı.")
            self.zaman_cizelgesi.append((gun, saat, f"{arac.adi} garajdan çıkarıldı."))
        else:
            print(f"Hata: {arac.adi} adlı araç garajda bulunamadı.")

    def arac_garaja_geldiginde_kuyruga_gir(self, arac, saat, gun):
        arac.garaja_gelis = saat
        self.sarj_istasyonu_kuyrugu.append(arac)
        print(f"{arac.adi} adlı araç garaja geldi ve şarj istasyonu kuyruğuna alındı.")
        self.zaman_cizelgesi.append((gun, saat, f"{arac.adi} garaja geldi ve şarj istasyonu kuyruğuna girdi."))
        if self.sarj_istasyonu_doluluk < self.sarj_istasyonu_kapasitesi:
            self.arac_kuyruktan_sarja_gonder(saat, gun)


    def gunluk_cagrilar(self, gun_sayisi):
        for gun in range(gun_sayisi):
            self.hat_tur_sayisi = {hat["adi"]: 0 for hat in self.hatlar}  # Tur sayılarını sıfırla
            print(f"\nGün {gun + 1} başlıyor...")
            olaylar = []
            for hat in self.hatlar:
                baslangic_saat = hat["baslangic_saat"] + timedelta(days=gun)
                olaylar.append((baslangic_saat, "hat_baslangic", hat, gun))


            while olaylar:
                olaylar.sort(key=lambda x: x[0])
                saat, olay_tipi, veri, gun = olaylar.pop(0)

                if olay_tipi == "hat_baslangic":
                    hat = veri
                    if not self.kullanilabilir_araclar:
                        print("Kullanılabilir araçlar tükendi.")
                        break

                    arac = self.kullanilabilir_araclar.pop(0)  # FIFO: İlk sıradaki aracı al
                    if arac.kalan_menzil >= self.hattin_uzunlugu[hat["adi"]]:
                        varis_saat = self.sefer_yap(arac, saat, hat, gun)
                        olaylar.append((varis_saat + timedelta(minutes=1), "tur_bitis", arac, gun))
                        saat = varis_saat + timedelta(minutes=1)  # Bir sonraki turun başlangıç saatini güncelle
                    else:
                        print(f"{arac.adi} adlı aracın menzili yetersiz, şarj istasyonuna yönlendiriliyor.")
                        self.arac_garaja_geldiginde_kuyruga_gir(arac, saat, gun)
                        if self.kullanilabilir_araclar:  # Başka bir araç varsa
                            arac = self.kullanilabilir_araclar.pop(0)
                            if arac.kalan_menzil >= self.hattin_uzunlugu[hat["adi"]]:
                                varis_saat = self.sefer_yap(arac, saat, hat, gun)
                                olaylar.append((varis_saat + timedelta(minutes=1), "tur_bitis", arac, gun))
                                saat = varis_saat + timedelta(minutes=1)
                            else:
                                print(f"{arac.adi} adlı aracın menzili de yetersiz, şarj istasyonuna yönlendiriliyor.")
                                self.arac_garaja_geldiginde_kuyruga_gir(arac, saat, gun)

                elif olay_tipi == "tur_bitis":
                    arac = veri
                    hat = arac.mevcut_hat  # Mevcut hattı doğrudan araçtan al
                    if self.hat_tur_sayisi[hat["adi"]] < hat["tur_sayisi"]:
                        if arac.kalan_menzil >= self.hattin_uzunlugu[hat["adi"]]:
                            varis_saat = self.sefer_yap(arac, saat, hat, gun)
                            olaylar.append((varis_saat + timedelta(minutes=1), "tur_bitis", arac, gun))
                            self.hat_tur_sayisi[hat["adi"]] += 1
                        else:
                            print(f"{arac.adi} adlı aracın menzili yetersiz, şarj istasyonuna yönlendiriliyor.")
                            self.arac_garaja_geldiginde_kuyruga_gir(arac, saat, gun)
                            if self.kullanilabilir_araclar:  # Başka bir araç varsa
                                yeni_arac = self.kullanilabilir_araclar.pop(0)
                                if yeni_arac.kalan_menzil >= self.hattin_uzunlugu[hat["adi"]]:
                                    varis_saat = self.sefer_yap(yeni_arac, saat, hat, gun)
                                    olaylar.append((varis_saat + timedelta(minutes=1), "tur_bitis", yeni_arac, gun))
                                    self.hat_tur_sayisi[hat["adi"]] += 1
                                else:
                                    print(f"{yeni_arac.adi} adlı aracın menzili de yetersiz, şarj istasyonuna yönlendiriliyor.")
                                    self.arac_garaja_geldiginde_kuyruga_gir(yeni_arac, saat, gun)
                    else:
                        self.kullanilabilir_araclar.append(arac)

                # Her olay işlendikten sonra kontrol et ve yeni hat başlangıçlarını ekle
                for hat in self.hatlar:
                    if hat["baslangic_saat"].time() <= saat.time() < (
                            hat["baslangic_saat"] + timedelta(minutes=1)).time():
                        olaylar.append((saat, "hat_baslangic", hat, gun))

            # Şarj istasyonu kuyruğundaki araçları şarj et
            while self.sarj_istasyonu_kuyrugu:
                print("\nŞarj istasyonunda işlem yapılıyor:")
                self.arac_kuyruktan_sarja_gonder(datetime.now(), gun)

        if gun_sayisi==7:
            # Toplam gidilen mesafeyi hesapla
            toplam_km = sum(veriler["toplam_km"] for veriler in self.istatistik.values())

            # İstatistikleri yazdır
            print("\nAraç Kullanım İstatistikleri:")
            for arac_adi, veriler in self.istatistik.items():
                toplam_arac_km = veriler["toplam_km"]
                oran = (toplam_arac_km / toplam_km) * 100 if toplam_km > 0 else 0
                print(f"{arac_adi}: {toplam_arac_km} km, {veriler['toplam_sarj_suresi']} dakika şarj süresi, {veriler['toplam_tur_sayisi']} tur, Kullanım Oranı: %{oran:.2f}")
                for hat, km in veriler["hatlar"].items():
                    oran = (km / toplam_arac_km) * 100 if toplam_arac_km > 0 else 0
                    print(f"  {hat}: {km} km (%{oran:.2f})")



def main():
    araclar = [
        OtobusHatti.Araba("tip1.1", 180),
        OtobusHatti.Araba("tip1.1", 180),
        #OtobusHatti.Araba("tip1.1", 180),
        #OtobusHatti.Araba("tip1.1", 180),
        #OtobusHatti.Araba("tip1.1", 180),
        #OtobusHatti.Araba("tip1.1", 180),
        #OtobusHatti.Araba("tip1.11", 180),
        #OtobusHatti.Araba("tip1.2", 240),
        #OtobusHatti.Araba("tip1.2", 240),
        #OtobusHatti.Araba("tip1.2", 240),
        #OtobusHatti.Araba("tip1.2", 240),
        #OtobusHatti.Araba("tip1.2", 240),
       #OtobusHatti.Araba("tip1.2", 240),
        #OtobusHatti.Araba("tip1.3", 300),
        #OtobusHatti.Araba("tip1.31", 300),
        #OtobusHatti.Araba("tip1.32", 300),
        #OtobusHatti.Araba("tip1.33", 300),
        #OtobusHatti.Araba("tip1.34", 300),
        #OtobusHatti.Araba("tip1.35", 300),
        #OtobusHatti.Araba("tip1.4", 300),
        #OtobusHatti.Araba("tip1.4", 300),
        #OtobusHatti.Araba("tip1.4", 300),
        #OtobusHatti.Araba("tip1.4", 300),
        #OtobusHatti.Araba("tip1.4", 300),
        #OtobusHatti.Araba("tip1.4", 300),
        #OtobusHatti.Araba("tip1.5", 360),
        #OtobusHatti.Araba("tip1.5", 360),
        #OtobusHatti.Araba("tip1.5", 360),
        #OtobusHatti.Araba("tip1.5", 360),
        #OtobusHatti.Araba("tip1.5", 360),
        #OtobusHatti.Araba("tip1.6", 420),
        #OtobusHatti.Araba("tip1.6", 420),
        #OtobusHatti.Araba("tip1.6", 420),
        #OtobusHatti.Araba("tip1.6", 420),
        #OtobusHatti.Araba("tip1.6", 420),
        #OtobusHatti.Araba("tip1.6", 420),
        OtobusHatti.Araba("tip2.7", 150),
        OtobusHatti.Araba("tip2.7", 150),
        OtobusHatti.Araba("tip2.7", 150),
        OtobusHatti.Araba("tip2.7", 150),
        #OtobusHatti.Araba("tip2.7", 150),
        #OtobusHatti.Araba("tip2.7", 150),
        #OtobusHatti.Araba("tip2.76", 150),
        #OtobusHatti.Araba("tip2.77", 150),


    ]

    hatlar = [
        {"adi": "hattc", "uzunluk": 28, "min_saat": 1.83, "max_saat": 2.17, "tur_sayisi": 8,
         "baslangic_saat": datetime(2024, 4, 1, 4, 30)},
        {"adi": "hatta", "uzunluk": 123, "min_saat": 4.5, "max_saat": 5, "tur_sayisi": 2,
         "baslangic_saat": datetime(2024, 4, 1, 7, 0)},
        {"adi": "hattb", "uzunluk": 75, "min_saat": 3.33, "max_saat": 3.67, "tur_sayisi": 3,
         "baslangic_saat": datetime(2024, 4, 1, 7, 0)},
        {"adi": "hattd", "uzunluk": 87, "min_saat": 6.33, "max_saat": 6.67, "tur_sayisi": 1,
         "baslangic_saat": datetime(2024, 4, 1, 8, 30)},
    ]
    # İstatistikleri yazdır

    otobus_hatti = OtobusHatti(araclar, hatlar)
    otobus_hatti.gunluk_cagrilar(7)
    print("toplam1=tip2 şarj süresi ",toplam1)
    print("toplam2 tip 1 şarj süresi", toplam2)
    print("toplam3 tip 2 ikinci şarj aletikullanım şarj süresi", toplam3)

if __name__ == "__main__":
    main()
