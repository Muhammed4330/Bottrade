"""
Binance Kripto Trading Botu
Teknik Analiz (RSI, MACD, MA) ile otomatik alım/satım

UYARI: Gerçek para ile kullanmadan önce MUTLAKA test edin!
Testnet API keylerini kullanarak başlayın.
"""

import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from binance.client import Client
from binance.enums import *
import ta  # Technical Analysis library

class CryptoTradingBot:
    def __init__(self, api_key, api_secret, symbol='BTCUSDT', testnet=True):
        """
        Trading bot'u başlatır
        
        Args:
            api_key: Binance API anahtarı
            api_secret: Binance API secret
            symbol: Trading çifti (örn: 'BTCUSDT', 'ETHUSDT')
            testnet: True ise Testnet kullanır (önerilen!)
        """
        self.symbol = symbol
        self.testnet = testnet
        
        if testnet:
            # Testnet için
            self.client = Client(api_key, api_secret, testnet=True)
            self.client.API_URL = 'https://testnet.binance.vision/api'
            print("⚠️  TESTNET MODUNDA - Gerçek para kullanılmıyor")
        else:
            self.client = Client(api_key, api_secret)
            print("🔴 CANLI MOD - Gerçek para kullanılıyor!")
        
        # Trading parametreleri
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.ma_short = 20
        self.ma_long = 50
        
        # Risk yönetimi
        self.position_size = 0.01  # Her işlemde kullanılacak miktar (BTC/ETH vb.)
        self.stop_loss_pct = 2.0   # % stop loss
        self.take_profit_pct = 4.0 # % take profit
        
        # Bot durumu
        self.in_position = False
        self.entry_price = 0
        
        print(f"✅ Bot başlatıldı - Sembol: {self.symbol}")
    
    def get_historical_data(self, interval='15m', limit=100):
        """Geçmiş fiyat verilerini çeker"""
        try:
            klines = self.client.get_klines(
                symbol=self.symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['close'] = pd.to_numeric(df['close'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            return df
        except Exception as e:
            print(f"❌ Veri çekme hatası: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Teknik göstergeleri hesaplar"""
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'], 
            window=self.rsi_period
        ).rsi()
        
        # MACD
        macd = ta.trend.MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Hareketli Ortalamalar
        df['ma_short'] = ta.trend.SMAIndicator(
            close=df['close'], 
            window=self.ma_short
        ).sma_indicator()
        
        df['ma_long'] = ta.trend.SMAIndicator(
            close=df['close'], 
            window=self.ma_long
        ).sma_indicator()
        
        return df
    
    def generate_signal(self, df):
        """
        Trading sinyali üretir
        Returns: 'BUY', 'SELL', veya 'HOLD'
        """
        if len(df) < self.ma_long:
            return 'HOLD'
        
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # ALIŞ sinyali koşulları:
        buy_conditions = [
            latest['rsi'] < self.rsi_oversold,  # RSI aşırı satım bölgesinde
            latest['macd'] > latest['macd_signal'],  # MACD pozitif kesişim
            latest['close'] > latest['ma_short'],  # Fiyat kısa MA üzerinde
            previous['macd'] <= previous['macd_signal']  # Yeni kesişim
        ]
        
        # SATIŞ sinyali koşulları:
        sell_conditions = [
            latest['rsi'] > self.rsi_overbought,  # RSI aşırı alım bölgesinde
            latest['macd'] < latest['macd_signal'],  # MACD negatif kesişim
            latest['close'] < latest['ma_short'],  # Fiyat kısa MA altında
            previous['macd'] >= previous['macd_signal']  # Yeni kesişim
        ]
        
        if sum(buy_conditions) >= 3:
            return 'BUY'
        elif sum(sell_conditions) >= 3:
            return 'SELL'
        else:
            return 'HOLD'
    
    def get_account_balance(self, asset='USDT'):
        """Hesap bakiyesini kontrol eder"""
        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance['free'])
        except Exception as e:
            print(f"❌ Bakiye hatası: {e}")
            return 0
    
    def place_order(self, side, quantity):
        """Emir gönderir"""
        try:
            if self.testnet:
                print(f"📝 TEST EMRİ: {side} {quantity} {self.symbol}")
            
            order = self.client.create_order(
                symbol=self.symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            print(f"✅ Emir gerçekleşti: {side} {quantity} {self.symbol}")
            return order
        except Exception as e:
            print(f"❌ Emir hatası: {e}")
            return None
    
    def check_stop_loss_take_profit(self, current_price):
        """Stop loss ve take profit kontrolü"""
        if not self.in_position:
            return None
        
        price_change_pct = ((current_price - self.entry_price) / self.entry_price) * 100
        
        if price_change_pct <= -self.stop_loss_pct:
            print(f"🛑 STOP LOSS! %{price_change_pct:.2f} kayıp")
            return 'SELL'
        elif price_change_pct >= self.take_profit_pct:
            print(f"🎯 TAKE PROFIT! %{price_change_pct:.2f} kar")
            return 'SELL'
        
        return None
    
    def run(self, interval='15m', check_interval=60):
        """
        Bot'u çalıştırır
        
        Args:
            interval: Mum çubuğu aralığı ('1m', '5m', '15m', '1h' vb.)
            check_interval: Kontrol sıklığı (saniye)
        """
        print(f"\n🤖 Bot çalışmaya başladı...")
        print(f"📊 Göstergeler: RSI({self.rsi_period}), MA({self.ma_short}/{self.ma_long}), MACD")
        print(f"⏱️  Kontrol aralığı: {check_interval} saniye\n")
        
        try:
            while True:
                # Veri çek ve analiz et
                df = self.get_historical_data(interval=interval)
                if df is None:
                    time.sleep(check_interval)
                    continue
                
                df = self.calculate_indicators(df)
                current_price = float(df.iloc[-1]['close'])
                
                # Mevcut durum bilgisi
                latest = df.iloc[-1]
                print(f"\n{'='*60}")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"💰 {self.symbol}: ${current_price:,.2f}")
                print(f"📈 RSI: {latest['rsi']:.2f} | MACD: {latest['macd_diff']:.4f}")
                print(f"📊 MA{self.ma_short}: ${latest['ma_short']:.2f} | MA{self.ma_long}: ${latest['ma_long']:.2f}")
                
                # Stop loss / Take profit kontrolü
                if self.in_position:
                    pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100
                    print(f"📍 Pozisyonda - Giriş: ${self.entry_price:,.2f} | P/L: %{pnl_pct:.2f}")
                    
                    sl_tp_signal = self.check_stop_loss_take_profit(current_price)
                    if sl_tp_signal == 'SELL':
                        self.place_order(SIDE_SELL, self.position_size)
                        self.in_position = False
                        self.entry_price = 0
                        time.sleep(check_interval)
                        continue
                
                # Sinyal üret
                signal = self.generate_signal(df)
                print(f"🎯 Sinyal: {signal}")
                
                # İşlem yap
                if signal == 'BUY' and not self.in_position:
                    order = self.place_order(SIDE_BUY, self.position_size)
                    if order:
                        self.in_position = True
                        self.entry_price = current_price
                        
                elif signal == 'SELL' and self.in_position:
                    order = self.place_order(SIDE_SELL, self.position_size)
                    if order:
                        self.in_position = False
                        pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100
                        print(f"💵 Kar/Zarar: %{pnl_pct:.2f}")
                        self.entry_price = 0
                
                # Bekle
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Bot durduruldu (Ctrl+C)")
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")


def backtest(symbol='BTCUSDT', days=30):
    """
    Basit backtest - Stratejinin geçmiş performansını test eder
    """
    print(f"\n📊 BACKTEST: {symbol} - Son {days} gün\n")
    
    # Demo client (API key gerektirmez)
    client = Client("", "")
    
    # Veri çek
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1HOUR,
        start_str=f"{days} days ago UTC"
    )
    
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])
    
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    
    # Göstergeleri hesapla
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['ma_20'] = ta.trend.SMAIndicator(close=df['close'], window=20).sma_indicator()
    df['ma_50'] = ta.trend.SMAIndicator(close=df['close'], window=50).sma_indicator()
    
    # Basit backtest
    trades = []
    in_position = False
    entry_price = 0
    
    for i in range(50, len(df)):
        if pd.isna(df.iloc[i]['rsi']):
            continue
            
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Alış sinyali
        if not in_position:
            if (current['rsi'] < 30 and 
                current['macd'] > current['macd_signal'] and
                prev['macd'] <= prev['macd_signal']):
                in_position = True
                entry_price = current['close']
                trades.append({'type': 'BUY', 'price': entry_price, 'time': i})
        
        # Satış sinyali
        elif in_position:
            if (current['rsi'] > 70 or
                current['macd'] < current['macd_signal']):
                exit_price = current['close']
                pnl = ((exit_price - entry_price) / entry_price) * 100
                trades.append({'type': 'SELL', 'price': exit_price, 'pnl': pnl, 'time': i})
                in_position = False
    
    # Sonuçlar
    if len(trades) > 0:
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        if sell_trades:
            total_pnl = sum([t['pnl'] for t in sell_trades])
            avg_pnl = total_pnl / len(sell_trades)
            wins = len([t for t in sell_trades if t['pnl'] > 0])
            
            print(f"📈 Toplam İşlem: {len(sell_trades)}")
            print(f"✅ Kazanan: {wins} ({wins/len(sell_trades)*100:.1f}%)")
            print(f"❌ Kaybeden: {len(sell_trades)-wins}")
            print(f"💰 Toplam Getiri: %{total_pnl:.2f}")
            print(f"📊 Ortalama İşlem: %{avg_pnl:.2f}")
            print(f"\nİlk 5 İşlem:")
            for i, trade in enumerate(sell_trades[:5]):
                print(f"  {i+1}. %{trade['pnl']:.2f}")
    else:
        print("⚠️  Hiç işlem gerçekleşmedi")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         KRİPTO TRADING BOT - TEKNİK ANALİZ              ║
    ║              RSI + MACD + MA Stratejisi                  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    print("\n1️⃣  Backtest yap (geçmiş performans)")
    print("2️⃣  Bot'u çalıştır (API key gerekli)")
    print("\nSeçim: ", end="")
    
    choice = input().strip()
    
    if choice == "1":
        backtest(symbol='BTCUSDT', days=30)
    
    elif choice == "2":
        print("\n" + "="*60)
        print("⚠️  ÖNEMLI UYARILAR:")
        print("="*60)
        print("1. İlk olarak TESTNET ile test edin!")
        print("2. Küçük miktarlarla başlayın!")
        print("3. Trading risklidir - kaybedebileceğiniz parayı kullanın!")
        print("4. 7/24 izleyin ve stop-loss kullanın!")
        print("="*60)
        
        print("\n📝 Binance API ayarları:")
        print("\nTestnet API Key almak için: https://testnet.binance.vision/")
        print("Gerçek API Key için: Binance > Profile > API Management\n")
        
        api_key = input("API Key: ").strip()
        api_secret = input("API Secret: ").strip()
        symbol = input("Trading çifti (örn: BTCUSDT): ").strip().upper() or "BTCUSDT"
        
        use_testnet = input("\nTestnet kullan? (E/H) [E]: ").strip().upper() != "H"
        
        # Bot'u başlat
        bot = CryptoTradingBot(
            api_key=api_key,
            api_secret=api_secret,
            symbol=symbol,
            testnet=use_testnet
        )
        
        bot.run(interval='15m', check_interval=60)
    
    else:
        print("Geçersiz seçim!")
