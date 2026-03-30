# 🤖 Kripto Trading Botu - Teknik Analiz

Binance için Python tabanlı otomatik trading botu. RSI, MACD ve hareketli ortalamalar kullanarak alım/satım sinyalleri üretir.

## ⚠️ ÖNEMLİ UYARILAR

- **Bu bot gerçek para kaybetmenize sebep olabilir!**
- Önce TESTNET ile test edin
- Küçük miktarlarla başlayın
- Stratejinizi backtest ile kontrol edin
- 7/24 takip edin ve risk yönetimi uygulayın
- Kripto trading son derece risklidir

## 🚀 Özellikler

### Teknik Göstergeler
- **RSI (Relative Strength Index)**: Aşırı alım/satım bölgelerini tespit eder
- **MACD (Moving Average Convergence Divergence)**: Trend değişimlerini yakalar
- **MA (Moving Averages)**: 20/50 periyot hareketli ortalamalar

### Risk Yönetimi
- Stop-loss otomasyonu (%2 default)
- Take-profit otomasyonu (%4 default)
- Pozisyon boyutu kontrolü
- Gerçek zamanlı kar/zarar takibi

### Diğer Özellikler
- Testnet desteği (güvenli test ortamı)
- Backtest fonksiyonu (stratejinizi geçmişte test edin)
- Detaylı loglar ve bildirimler
- Birden fazla kripto çifti desteği

## 📋 Kurulum

### 1. Gereksinimleri Yükleyin

```bash
pip install -r bot_requirements.txt
```

veya tek tek:

```bash
pip install pandas numpy python-binance ta
```

### 2. Binance API Key Alın

#### Testnet için (ÖNERİLİR - İlk Adım):
1. https://testnet.binance.vision/ adresine gidin
2. GitHub ile giriş yapın
3. API Key ve Secret oluşturun
4. Test parası alın (ücretsiz)

#### Gerçek Binance için:
1. Binance hesabınıza giriş yapın
2. Profile > API Management
3. Yeni API key oluşturun
4. "Enable Spot & Margin Trading" seçin
5. IP whitelist ekleyin (güvenlik)

## 🎯 Kullanım

### Backtest (Stratejiyi Test Etme)

Önce stratejinizin geçmişte nasıl performans gösterdiğini test edin:

```bash
python crypto_trading_bot.py
# Seçim: 1
```

Örnek çıktı:
```
📊 BACKTEST: BTCUSDT - Son 30 gün

📈 Toplam İşlem: 8
✅ Kazanan: 5 (62.5%)
❌ Kaybeden: 3
💰 Toplam Getiri: %12.34
📊 Ortalama İşlem: %1.54
```

### Bot'u Çalıştırma

```bash
python crypto_trading_bot.py
# Seçim: 2
```

Bot şu bilgileri soracak:
- API Key
- API Secret  
- Trading çifti (BTCUSDT, ETHUSDT vb.)
- Testnet kullanılsın mı?

## ⚙️ Konfigürasyon

Bot kodunda şu parametreleri değiştirebilirsiniz:

```python
# Trading parametreleri
self.rsi_period = 14          # RSI periyodu
self.rsi_overbought = 70      # Aşırı alım seviyesi
self.rsi_oversold = 30        # Aşırı satım seviyesi
self.ma_short = 20            # Kısa MA periyodu
self.ma_long = 50             # Uzun MA periyodu

# Risk yönetimi
self.position_size = 0.01     # İşlem başına miktar
self.stop_loss_pct = 2.0      # Stop loss yüzdesi
self.take_profit_pct = 4.0    # Take profit yüzdesi
```

## 📊 Strateji Detayları

### Alış Sinyali (3/4 koşul sağlanmalı):
1. RSI < 30 (aşırı satım)
2. MACD pozitif kesişim (MACD > Signal)
3. Fiyat > 20 MA
4. Yeni kesişim (önceki barda değildi)

### Satış Sinyali (3/4 koşul sağlanmalı):
1. RSI > 70 (aşırı alım)
2. MACD negatif kesişim (MACD < Signal)
3. Fiyat < 20 MA
4. Yeni kesişim

### Risk Yönetimi:
- Her kontrolde stop-loss ve take-profit kontrol edilir
- %2 zarar → otomatik satış
- %4 kar → otomatik satış

## 🔧 Özelleştirme Örnekleri

### Farklı Kripto Çifti:
```python
bot = CryptoTradingBot(
    symbol='ETHUSDT',  # veya 'BNBUSDT', 'ADAUSDT', vb.
    # ...
)
```

### Daha Agresif Strateji:
```python
self.rsi_oversold = 35        # Daha erken al
self.rsi_overbought = 65      # Daha erken sat
self.take_profit_pct = 3.0    # Daha düşük kar hedefi
```

### Daha Konservatif:
```python
self.stop_loss_pct = 1.5      # Daha sıkı stop-loss
self.take_profit_pct = 6.0    # Daha yüksek kar hedefi
self.position_size = 0.005    # Daha küçük pozisyon
```

## 📝 Bot Çalışırken

Bot çalışırken şunları göreceksiniz:

```
============================================================
⏰ 2026-03-29 15:30:45
💰 BTCUSDT: $87,234.56
📈 RSI: 34.21 | MACD: 0.0023
📊 MA20: $86,891.23 | MA50: $85,432.10
🎯 Sinyal: BUY
📝 TEST EMRİ: BUY 0.01 BTCUSDT
✅ Emir gerçekleşti: BUY 0.01 BTCUSDT
```

## 🛡️ Güvenlik İpuçları

1. **Hiçbir zaman API keyinizi paylaşmayın**
2. **IP whitelist kullanın**
3. **"Enable Withdrawals" seçeneğini kapatın**
4. **Küçük miktarlarla başlayın**
5. **Trading izinlerini sınırlayın**
6. **Düzenli olarak API key'leri yenileyin**

## 🐛 Sorun Giderme

### "API key hatası"
- API key ve secret'i kontrol edin
- Binance'ta trading izinlerini kontrol edin
- IP whitelist ayarlarını kontrol edin

### "Yetersiz bakiye"
- position_size değerini küçültün
- Bakiyenizi kontrol edin
- Testnet'te ücretsiz para alın

### "Sinyal üretilmiyor"
- Gösterge parametrelerini ayarlayın
- Daha volatile bir çift seçin
- Zaman dilimini değiştirin (interval)

## 📚 Daha Fazla Öğrenmek İçin

- [Binance API Dokümantasyonu](https://binance-docs.github.io/apidocs/spot/en/)
- [RSI Göstergesi](https://www.investopedia.com/terms/r/rsi.asp)
- [MACD Göstergesi](https://www.investopedia.com/terms/m/macd.asp)
- [Trading Bot Stratejileri](https://www.binance.com/en/blog)

## ⚖️ Yasal Uyarı

Bu bot eğitim amaçlıdır. Kripto para ticareti yüksek risk içerir. Kendi araştırmanızı yapın ve kaybetmeyi göze alabileceğiniz miktarlarla işlem yapın. Bu bot'un kullanımından doğan kayıplardan sorumlu değiliz.

## 🤝 Katkıda Bulunma

Önerileriniz ve iyileştirmeleriniz için pull request gönderebilirsiniz!

---

**Başarılı tradeler dileriz! 🚀📈**

*Not: Bot'u durdurmak için Ctrl+C tuşlarına basın.*
