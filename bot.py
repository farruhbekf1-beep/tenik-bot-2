#!/usr/bin/env python3
"""
TECH MAX / JARVIS Buyurtma va Uchrashuv Telegram Boti.
Python 3 standart kutubxonalarida ishlaydi (tashqi pip paketlar talab qilmaydi).
GitHub, VPS, Railway, Render va Heroku uchun tayyor.
"""
import json, os, sqlite3, time, urllib.parse, urllib.request, hmac, secrets, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timedelta
import threading

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
ADMIN_CHAT_ID = os.environ.get('TECHMAX_ADMIN_CHAT_ID', '').strip()
ADMIN_USERNAME = os.environ.get('TECHMAX_ADMIN_USERNAME', 'FARRUHBEKK1').strip()
ADMIN_PHONE = os.environ.get('TECHMAX_ADMIN_PHONE', '+998943528488').strip()
ADMIN_URL = 'https://t.me/' + ADMIN_USERNAME
ADMIN_PHONE_DIGITS = ''.join(ch for ch in ADMIN_PHONE if ch.isdigit())
HUD = '╔═══════════════════════╗\n  ◈ J.A.R.V.I.S  ▸  TECH MAX\n  ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n╚═══════════════════════╝'
LINE = '▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰'
BRIDGE_PORT = int(os.environ.get('JARVIS_BRIDGE_PORT', '8787'))
BRIDGE_HOST = os.environ.get('JARVIS_BRIDGE_HOST', '0.0.0.0')
BANNER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jarvis_banner.png')
BOT_USERNAME = ''
BANNER_FILE_ID = ''
MAX_FEATURES = 20

DB_PATH = os.environ.get('TECHMAX_DB_PATH', 'techmax_bot.sqlite3')
API = f'https://api.telegram.org/bot{TOKEN}/'

SERVICES = {
 '⚡ Elektrik xizmatlari': ['Elektr montaj ishlari','Sim yotqizish','Panel o‘rnatish','Avtomat o‘rnatish','Yoritish tizimi','Elektr jihozlarini ta’mirlash','Avariya xizmati (24/7)'],
 '🏠 Aqlli uy (Smart Home)': ['Smart yoritish (LED)','Harakat sensori','Kamera va xavfsizlik tizimi','Wi‑Fi va internet','Masofadan boshqarish','Mobil ilova orqali boshqaruv'],
 '📱 Telefon ta’mirlash': ['Ekran almashtirish','Batareya almashtirish','Zaryadlash porti','Kamera ta’miri','Dasturiy ta’mirlash','Suvdan chiqqan telefonlar','Boshqa nosozliklar'],
 '💻 Kompyuter va noutbuklar': ['Noutbuklar','Kompyuterlar','Monitorlar','Tarmoq uskunalari','Dastur o‘rnatish','Texnik xizmat','Windows o‘rnatish','SSD/xotira upgrade'],
 '💻 Dasturlash va platformalar': ['Veb saytlar','Telegram botlar','Mobil ilovalar (Android/iOS)','Desktop dasturlar','API integratsiya','CRM va boshqaruv tizimlari','O‘yin va grafik dasturlar'],
 '🤖 Telegram botlar': ['Avto javob','Buyurtma va xizmatlar','To‘lov tizimi','Foydalanuvchilar boshqaruvi','Guruh va kanal botlari','O‘yin va qiziqarli botlar'],
 '📲 Android ilovalar': ['Mobil ilova ishlab chiqish','UI/UX dizayn','Play Storega joylash','API integratsiya','Yangilash va qo‘llab-quvvatlash'],
 '🔧 Elektronika ta’miri': ['Telefon va gadjetlar','Kompyuter jihozlari','Maishiy texnika','Plata ta’miri','Sxema va modul','Dasturlash va sozlash'],
 '🎧 24/7 yordam': ['Texnik yordam','Maslahatlar','Muammolarni yechish','Tezkor javob','Onlayn qo‘llab-quvvatlash'],
 '🚗 Avtomobil xizmatlari': ['Diagnostika','Moy almashtirish','Filtrlar almashtirish','Tormoz tizimi','Xodovoy ta’miri','Konditsioner'],
 '🏡 Uy jihozlari': ['Kir yuvish mashinasi','Sovutgich','Konditsioner','Televizor','Mikroto‘lqinli pech','Boshqa maishiy texnika'],
 '🎨 Reklama va dizayn': ['Logo dizayn','Banner va poster','SMM dizayn','Video montaj','Web dizayn','Brend yaratish'],
 '🌐 Internet va aloqa': ['Wi‑Fi o‘rnatish','Internet ulanish','Router sozlash','Tarmoq xavfsizligi','IP kamera'],
 '🚰 Santexnika': ['Quvur o‘rnatish','Kran almashtirish','Sanuzel ta’miri','Issiq-suv tizimi','Suv oqishini bartaraf etish'],
 '🛡 Xavfsizlik tizimi': ['Kuzatuv kameralar','Signalizatsiya','Domofon','Access control','Masofadan boshqaruv'],
 '🧰 Boshqa xizmatlar': ['Avtoelektrik xizmatlari','Gadjet va aksessuarlar','Elektronika ta’miri','Kabel va tarmoq uskunalari','Sovutish tizimlari','Barcha turdagi texnik yordam']
}

def db():
 c=sqlite3.connect(DB_PATH); c.execute('''CREATE TABLE IF NOT EXISTS users(chat_id INTEGER PRIMARY KEY,name TEXT,phone TEXT,address TEXT)'''); c.execute('''CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,chat_id INTEGER,name TEXT,phone TEXT,address TEXT,service TEXT,detail TEXT,slot TEXT,status TEXT DEFAULT 'Yangi',created TEXT)'''); c.execute('''CREATE TABLE IF NOT EXISTS subs(chat_id INTEGER PRIMARY KEY,ads_off INTEGER DEFAULT 0)'''); c.execute('''CREATE TABLE IF NOT EXISTS admins(chat_id INTEGER PRIMARY KEY)''')
 c.execute('''CREATE TABLE IF NOT EXISTS features(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,text TEXT,url TEXT,enabled INTEGER DEFAULT 1,created TEXT)''')
 c.execute('''CREATE TABLE IF NOT EXISTS meetings(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,phone TEXT,note TEXT,source TEXT,status TEXT DEFAULT 'Yangi',created TEXT)''')
 c.execute('''CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,data TEXT,created TEXT)''')
 for col in ('last_seen TEXT','created TEXT'):
  try: c.execute('ALTER TABLE users ADD COLUMN '+col)
  except sqlite3.OperationalError: pass
 c.commit(); return c

def log_event(kind, data):
 try:
  c=db(); c.execute('INSERT INTO events(kind,data,created) VALUES(?,?,?)',(kind,json.dumps(data,ensure_ascii=False),datetime.now().isoformat(timespec='seconds'))); c.commit(); c.close()
 except Exception as e: print('Event yozilmadi:',repr(e))

def touch_user(chat):
 try:
  c=db(); c.execute('UPDATE users SET last_seen=? WHERE chat_id=?',(datetime.now().isoformat(timespec='seconds'),chat)); c.commit(); c.close()
 except Exception: pass

def api(method, data=None):
 payload=urllib.parse.urlencode({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v) for k,v in (data or {}).items()}).encode()
 req=urllib.request.Request(API+method,data=payload)
 with urllib.request.urlopen(req,timeout=40) as r: return json.loads(r.read().decode())

def send(chat,text,markup=None):
 d={'chat_id':chat,'text':text}
 if markup: d['reply_markup']=markup
 return api('sendMessage',d)

def kb(rows): return {'inline_keyboard':[[{'text':label,'callback_data':data} for label,data in row] for row in rows]}

def main_menu():
 rows=[[{'text':'◈ XIZMATLARNI KO‘RISH  ▸','callback_data':'services'}],[{'text':'▣ BUYURTMALARIM','callback_data':'myorders'},{'text':'◉ PROFIL / MA’LUMOT','callback_data':'info'}]]
 try:
  c=db(); feats=c.execute('SELECT id,title FROM features WHERE enabled=1 ORDER BY id').fetchall(); c.close()
  for i in range(0,len(feats),2): rows.append([{'text':'⬡ '+t[:30],'callback_data':'feat:'+str(fid)} for fid,t in feats[i:i+2]])
 except Exception as e: print('Funksiyalar o‘qilmadi:',repr(e))
 rows.append([{'text':'⚡ ADMIN BILAN ALOQA','url':ADMIN_URL}])
 return {'inline_keyboard':rows}

def is_admin_user(user): return (user or {}).get('username','').lstrip('@').lower() == ADMIN_USERNAME.lower()

def remember_admin(message):
 global ADMIN_CHAT_ID
 if is_admin_user(message.get('from')): ADMIN_CHAT_ID = str(message.get('chat',{}).get('id',''))

def service_menu():
 items=list(SERVICES.items()); return kb([[ (name,'cat:'+str(i)) ] for i,(name,_) in enumerate(items)]+[[('⬅️ Asosiy menyu','home')]])

def tell_admin(msg):
 if ADMIN_CHAT_ID:
  try: send(int(ADMIN_CHAT_ID),msg)
  except Exception as e: print('Admin xabari yuborilmadi:',e)

def slot_options(chat,service,detail):
 c=db(); rows=[]; now=datetime.now()
 for day in range(0,8):
  d=(now+timedelta(days=day)).date()
  for hour in range(9,19):
   dt=datetime.combine(d,datetime.min.time()).replace(hour=hour)
   if dt <= now+timedelta(minutes=30): continue
   stamp=dt.strftime('%Y-%m-%d %H:%M')
   exists=c.execute("SELECT 1 FROM orders WHERE slot=? AND status!='Bekor qilindi'",(stamp,)).fetchone()
   if not exists: key=str(len(SLOTS)+1); SLOTS[key]=(service,detail,stamp,chat); rows.append((dt.strftime('%d.%m %H:%M'),'slot:'+key))
   if len(rows)>=12: break
  if len(rows)>=12: break
 c.close()
 if not rows: send(chat,'Hozircha bo‘sh vaqt topilmadi. Keyinroq urinib ko‘ring.',main_menu()); return
 send(chat,'📅 BO‘SH VAQTLAR (Toshkent vaqti)\n'+LINE+'\nQulay vaqtni tanlang 👇',kb([rows[i:i+2] for i in range(0,len(rows),2)]+[[('⬅️ Xizmatlarga qaytish','services')]]))

def handle_message(m):
 remember_admin(m)
 chat=m['chat']['id']; touch_user(chat); text=m.get('text','').strip(); c=db()
 if admin_message(m,c): c.close(); return
 if text.startswith('/start'):
  user=c.execute('SELECT name,phone,address FROM users WHERE chat_id=?',(chat,)).fetchone()
  if not user or not all(user):
   send_banner(chat)
   send(chat,HUD+'\n\n🟢 TIZIM FAOL\nAssalomu alaykum! Men JARVIS — TECH MAX yordamchisiman 👋\n\n🛠 Texnik xizmat • Ta’mirlash • Dasturlash\n📅 Qulay vaqtni tanlang, buyurtma bering.\n\n'+LINE+'\n📝 1/3 — IDENTIFIKATSIYA\nIsm-familiyangizni kiriting:')
   STATE[chat]={'step':'name'}
  else:
   send_banner(chat); send(chat,HUD+'\n\n🟢 Xush kelibsiz, '+user[0]+'! 👋\n\nBugun sizga qanday yordam beramiz?\nQuyidagi menyudan kerakli bo‘limni tanlang 👇',main_menu())
 elif text.startswith('/cancel'):
  STATE.pop(chat,None); send(chat,'Amal bekor qilindi.',main_menu())
 elif chat in STATE:
  st=STATE[chat]; step=st['step']
  if step=='name':
   st['name']=text[:100]; st['step']='phone'; send(chat,'📱 2/3 — ALOQA KANALI\n\nBog‘lanish uchun raqamingizni kiriting.\nMasalan: +998901234567')
  elif step=='phone':
   digits=''.join(ch for ch in text if ch.isdigit() or ch=='+')
   if len(''.join(ch for ch in digits if ch.isdigit()))<9: send(chat,'Telefon raqami noto‘g‘ri ko‘rinadi. Qayta kiriting:')
   else: st['phone']=digits; st['step']='address'; send(chat,'📍 3/3 — JOYLASHUV\n\nShahar/tuman, ko‘cha va uy raqamini yozing:')
  elif step=='address':
   st['address']=text[:300]; c.execute('INSERT OR REPLACE INTO users(chat_id,name,phone,address,created,last_seen) VALUES(?,?,?,?,?,?)',(chat,st['name'],st['phone'],st['address'],datetime.now().isoformat(timespec='seconds'),datetime.now().isoformat(timespec='seconds'))); c.commit(); link_meeting(c,chat,st['name'],st['phone']); log_event('user_registered',{'chat_id':chat,'name':st['name'],'phone':st['phone']}); STATE.pop(chat,None); send(chat,'✅ IDENTIFIKATSIYA YAKUNLANDI\n'+LINE+'\nMa’lumotlaringiz saqlandi.\nEndi kerakli xizmatni tanlashingiz mumkin 👇',main_menu())
  elif step=='detail':
   service=st['service']; detail=text[:500]; STATE.pop(chat,None); slot_options(chat,service,detail)
  elif step=='edit_name':
   st['name']=text[:100]; st['step']='edit_phone'; send(chat,'Telefon raqamingizni kiriting:')
  elif step=='edit_phone':
   st['phone']=text[:40]; st['step']='edit_address'; send(chat,'Manzilingizni kiriting:')
  elif step=='edit_address':
   st['address']=text[:300]; c.execute('INSERT OR REPLACE INTO users(chat_id,name,phone,address) VALUES(?,?,?,?)',(chat,st['name'],st['phone'],st['address'])); c.commit(); STATE.pop(chat,None); send(chat,'Ma’lumotlar saqlandi.',main_menu())
 elif text.startswith('/help'): send(chat,'/start — boshlash\n/cancel — joriy amalni bekor qilish\nXizmat tanlang, bo‘sh vaqtni belgilang va buyurtmani tasdiqlang.',main_menu())
 else: send(chat,'Davom etish uchun tugmalardan foydalaning yoki /start bosing.',main_menu())
 c.close()

STATE={}
SLOTS={}

def handle_callback(q):
 global ADMIN_CHAT_ID
 if is_admin_user(q.get('from')): ADMIN_CHAT_ID = str(q.get('message',{}).get('chat',{}).get('id',''))
 chat=q['message']['chat']['id']; data=q.get('data',''); api('answerCallbackQuery',{'callback_query_id':q['id']}); touch_user(chat)
 if data.startswith('adm:'): admin_callback(q,chat,data); return
 c=db()
 if data=='home': send(chat,HUD+'\n\nSizning texnik yordam markazingiz.\nXizmat tanlang yoki buyurtmalaringizni ko‘ring 👇',main_menu())
 elif data.startswith('feat:'):
  r=c.execute('SELECT title,text,url FROM features WHERE id=? AND enabled=1',(int(data[5:] or 0),)).fetchone()
  if not r: send(chat,'Bu funksiya hozir o‘chirilgan.',main_menu())
  else:
   mk=main_menu()
   if r[2]: mk['inline_keyboard'].insert(0,[{'text':'🔗 OCHISH ▸','url':r[2]}])
   send(chat,'⬡ '+r[0]+'\n'+LINE+'\n'+r[1],mk)
 elif data=='services': send(chat,'🛠 XIZMATLAR KATALOGI\n'+LINE+'\nKerakli yo‘nalishni tanlang 👇\nHar bir bo‘lim ichida xizmat turlari bor.',service_menu())
 elif data=='info': send(chat,'ℹ️ TIZIM MA’LUMOTI\n'+LINE+'\n🛠 Texnik xizmatlar, ta’mirlash va IT yechimlari\n🕘 Ish vaqti: 09:00–19:00\n👨‍💼 Admin: @'+ADMIN_USERNAME+'\n📞 Telefon: '+ADMIN_PHONE+'\n🔕 Reklamani o‘chirish: /stop_ads\n\nBuyurtma berish uchun “Xizmatlarni ko‘rish” tugmasini bosing.',main_menu())
 elif data=='myorders':
  rows=c.execute('SELECT service,detail,slot,status FROM orders WHERE chat_id=? ORDER BY id DESC LIMIT 10',(chat,)).fetchall()
  send(chat,'📋 BUYURTMALARINGIZ\n'+LINE+'\n'+'\n'.join(f'• {a} — {b}\n  {d} | {e}' for a,b,d,e in rows) if rows else 'Hozircha buyurtmangiz yo‘q.',main_menu())
 elif data.startswith('cat:'):
  idx=int(data.split(':')[1]); service=list(SERVICES)[idx]; choices=SERVICES[service]
  send(chat,'📂 '+service+'\n'+LINE+'\nKerakli xizmat turini tanlang 👇',kb([[(x,f'svc:{idx}:{j}')] for j,x in enumerate(choices)]+[[('↩️ Barcha yo‘nalishlar','services')]]))
 elif data.startswith('svc:'):
  _, si, di = data.split(':'); service=list(SERVICES)[int(si)]; detail=SERVICES[service][int(di)]
  user=c.execute('SELECT name,phone,address FROM users WHERE chat_id=?',(chat,)).fetchone()
  if not user or not all(user):
   STATE[chat]={'step':'name'}; send(chat,'Avval ro‘yxatdan o‘tamiz. Ismingizni yozing:')
  else:
   STATE[chat]={'step':'detail','service':service+' / '+detail}; send(chat,'📝 BUYURTMA PARAMETRLARI\n'+LINE+'\nTanlangan xizmat: '+service+'\n\nMuammo yoki talabingizni qisqacha yozing.\nMasalan: telefon modeli, nosozlik yoki kerakli funksiyalar.\n\nIzoh bo‘lmasa, “yo‘q” deb yuboring.')
 elif data.startswith('slot:'):
  item=SLOTS.get(data[5:])
  if not item or item[3] != chat:
   send(chat,'Bu vaqt tanlovi eskirgan. Qaytadan tanlang.',main_menu()); c.close(); return
  service,detail,slot,_=item
  user=c.execute('SELECT name,phone,address FROM users WHERE chat_id=?',(chat,)).fetchone()
  if not user or not all(user): send(chat,'Ma’lumotlaringiz to‘liq emas. /start bosing.',main_menu())
  elif c.execute("SELECT 1 FROM orders WHERE slot=? AND status!='Bekor qilindi'",(slot,)).fetchone(): send(chat,'Bu vaqt endi band. Boshqa vaqtni tanlang.'); slot_options(chat,service,detail)
  else:
   STATE[chat]={'step':'confirm','service':service,'detail':detail,'slot':slot}
   send(chat,f'🧾 BUYURTMANI TEKSHIRING\n{LINE}\n🛠 Xizmat: {service}\n📝 Izoh: {detail}\n📅 Sana-vaqt: {slot}\n👤 Ism: {user[0]}\n📱 Telefon: {user[1]}\n📍 Manzil: {user[2]}\n\nMa’lumotlar to‘g‘ri bo‘lsa, tasdiqlang 👇',kb([[('✅ BUYURTMANI TASDIQLASH','confirm')],[('❌ Bekor qilish','home')]]))
 elif data=='confirm':
  st=STATE.pop(chat,None); user=c.execute('SELECT name,phone,address FROM users WHERE chat_id=?',(chat,)).fetchone()
  if not st or st.get('step')!='confirm': send(chat,'Buyurtma ma’lumoti topilmadi. Qaytadan boshlang.',main_menu())
  elif c.execute("SELECT 1 FROM orders WHERE slot=? AND status!='Bekor qilindi'",(st['slot'],)).fetchone(): send(chat,'Kechirasiz, bu vaqt band bo‘lib qoldi. Yangi vaqt tanlang.'); slot_options(chat,st['service'],st['detail'])
  else:
   c.execute('INSERT INTO orders(chat_id,name,phone,address,service,detail,slot,created) VALUES(?,?,?,?,?,?,?,?)',(chat,*user,st['service'],st['detail'],st['slot'],datetime.now().isoformat(timespec='minutes'))); c.commit()
   msg=f'🆕 TECH MAX buyurtmasi\nIsm: {user[0]}\nTelefon: {user[1]}\nManzil: {user[2]}\nXizmat: {st["service"]}\nIzoh: {st["detail"]}\nVaqt: {st["slot"]}\nTelegram ID: {chat}'
   log_event('order_new',{'name':user[0],'phone':user[1],'service':st['service'],'slot':st['slot']}); tell_admin(msg); send(chat,'✅ BUYURTMA QABUL QILINDI\n'+LINE+'\nRahmat, buyurtmangiz TECH MAX jamoasiga yuborildi. 🎉\nAdmin siz bilan bog‘lanadi.\n\nBoshqa xizmat kerakmi? Asosiy menyudan tanlang 👇',main_menu())
 c.close()

# ───────── ADMIN MODULI ─────────
def is_admin(user, c=None):
 if is_admin_user(user): return True
 uid=(user or {}).get('id')
 if not uid: return False
 own=c is None; c=c or db()
 try: return c.execute('SELECT 1 FROM admins WHERE chat_id=?',(uid,)).fetchone() is not None
 finally:
  if own: c.close()

def admin_menu():
 return kb([[('📊 STATISTIKA','adm:stats'),('📋 BUYURTMALAR','adm:orders')],[('🤝 UCHRASHUVLAR','adm:meet'),('🧩 FUNKSIYALAR','adm:feat')],[('📢 REKLAMA YUBORISH','adm:ad')],[('⬅️ Asosiy menyu','home')]])

def audience(c):
 rows=c.execute('SELECT chat_id FROM (SELECT chat_id FROM users UNION SELECT chat_id FROM subs) WHERE chat_id NOT IN (SELECT chat_id FROM subs WHERE ads_off=1)').fetchall()
 return [r[0] for r in rows]

def admin_panel(chat): send(chat,HUD+'\n\n🛡 ADMIN PANEL — ruxsat tasdiqlandi\n'+LINE+'\nBuyruqni tanlang 👇',admin_menu())

def admin_message(m,c):
 chat=m['chat']['id']; user=m.get('from') or {}; text=(m.get('text') or '').strip()
 if text.startswith('/start'): c.execute('INSERT OR IGNORE INTO subs(chat_id) VALUES(?)',(chat,)); c.commit()
 if text.startswith('/stop_ads'):
  c.execute('INSERT OR IGNORE INTO subs(chat_id) VALUES(?)',(chat,)); c.execute('UPDATE subs SET ads_off=1 WHERE chat_id=?',(chat,)); c.commit()
  send(chat,'🔕 Reklama o‘chirildi. Qayta yoqish: /start_ads',main_menu()); return True
 if text.startswith('/start_ads'):
  c.execute('INSERT OR IGNORE INTO subs(chat_id) VALUES(?)',(chat,)); c.execute('UPDATE subs SET ads_off=0 WHERE chat_id=?',(chat,)); c.commit()
  send(chat,'🔔 Reklama yoqildi.',main_menu()); return True
 if text.startswith('/verify'):
  send(chat,'📲 Tasdiqlash uchun pastdagi tugmani bosing.',{'keyboard':[[{'text':'📲 Raqamimni yuborish','request_contact':True}]],'resize_keyboard':True,'one_time_keyboard':True}); return True
 ct=m.get('contact')
 if ct:
  digits=''.join(ch for ch in ct.get('phone_number','') if ch.isdigit())
  if ct.get('user_id')==user.get('id') and digits==ADMIN_PHONE_DIGITS:
   c.execute('INSERT OR IGNORE INTO admins(chat_id) VALUES(?)',(user['id'],)); c.commit()
   send(chat,'✅ Admin sifatida tasdiqlandingiz.',{'remove_keyboard':True}); admin_panel(chat)
  else: send(chat,'Davom etish uchun tugmalardan foydalaning yoki /start bosing.',{'remove_keyboard':True})
  return True
 if not is_admin(user,c): return False
 if text.startswith('/admin'): admin_panel(chat); return True
 if text.startswith('/start'): send(chat,'🛡 Admin rejimi faol.',kb([[('🛡 ADMIN PANEL','adm:panel')]])); return False
 st=STATE.get(chat)
 if st and st.get('step')=='ad_text' and not text.startswith('/'):
  mid=m['message_id']; n=len(audience(c)); st.update(step='ad_confirm',mid=mid)
  send(chat,'👁 Reklama ko‘rinishi (quyida):')
  try: api('copyMessage',{'chat_id':chat,'from_chat_id':chat,'message_id':mid})
  except Exception as e: print('Preview xatosi:',repr(e))
  send(chat,f'📢 Yuboriladi: {n} ta foydalanuvchiga.\nTasdiqlaysizmi?',kb([[('✅ YUBORISH','adm:adgo')],[('❌ Bekor qilish','adm:panel')]]))
  return True
 return False

def run_broadcast(admin_chat,mid):
 c=db(); ids=audience(c); c.close(); ok=fail=0
 for uid in ids:
  try: api('copyMessage',{'chat_id':uid,'from_chat_id':admin_chat,'message_id':mid}); ok+=1
  except Exception: fail+=1
  time.sleep(0.05)
 send(admin_chat,f'📢 REKLAMA YAKUNLANDI\n{LINE}\n✅ Yetkazildi: {ok}\n⚠️ Yetmadi: {fail}',admin_menu())

def admin_callback(q,chat,data):
 if not is_admin(q.get('from')): return
 c=db(); parts=data.split(':')
 try:
  if data in ('adm:panel','adm:home'): STATE.pop(chat,None); admin_panel(chat)
  elif data=='adm:stats':
   u=c.execute('SELECT COUNT(*) FROM users').fetchone()[0]; o=c.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
   new=c.execute("SELECT COUNT(*) FROM orders WHERE status='Yangi'").fetchone()[0]; done=c.execute("SELECT COUNT(*) FROM orders WHERE status='Bajarildi'").fetchone()[0]
   send(chat,f'📊 STATISTIKA\n{LINE}\n👥 Mijozlar: {u}\n📦 Jami buyurtma: {o}\n🆕 Yangi: {new}\n✅ Bajarilgan: {done}\n📢 Reklama auditoriyasi: {len(audience(c))}',admin_menu())
  elif data=='adm:orders':
   rows=c.execute("SELECT id,name,phone,service,detail,slot FROM orders WHERE status='Yangi' ORDER BY slot LIMIT 8").fetchall()
   if not rows: send(chat,'Yangi buyurtma yo‘q.',admin_menu())
   for i,n,ph,sv,dt,sl in rows: send(chat,f'🆕 #{i}\n👤 {n}\n📱 {ph}\n🛠 {sv}\n📝 {dt}\n📅 {sl}',kb([[('✅ Bajarildi',f'adm:st:{i}:done'),('❌ Bekor',f'adm:st:{i}:cancel')]]))
  elif parts[1]=='st':
   oid=int(parts[2]); status='Bajarildi' if parts[3]=='done' else 'Bekor qilindi'
   r=c.execute('SELECT chat_id,service,slot FROM orders WHERE id=?',(oid,)).fetchone()
   if r:
    c.execute('UPDATE orders SET status=? WHERE id=?',(status,oid)); c.commit()
    send(chat,f'#{oid} holati: {status}')
    try: send(r[0],f'🔔 Buyurtmangiz holati yangilandi\n{LINE}\n🛠 {r[1]}\n📅 {r[2]}\n📌 Holat: {status}')
    except Exception as e: print('Mijozga xabar yuborilmadi:',e)
  elif data=='adm:meet':
   rows=c.execute("SELECT id,name,phone,note,source,status,created FROM meetings ORDER BY id DESC LIMIT 10").fetchall()
   if not rows: send(chat,'Uchrashuvlar bo‘limi hozircha bo‘sh.',admin_menu())
   for i,n,ph,nt,src,stt,cr in rows: send(chat,f'🤝 #{i} [{stt}]\n👤 {n}\n📱 {ph}\n📝 {nt}\n📞 Manba: {src} | {cr}')
  elif data=='adm:feat':
   rows=c.execute('SELECT id,title,enabled FROM features ORDER BY id').fetchall()
   send(chat,'🧩 QO‘SHILGAN FUNKSIYALAR\n'+LINE+'\n'+('\n'.join(f'#{i} {t} — '+('yoqilgan' if e else 'o‘chirilgan') for i,t,e in rows) if rows else 'Hali yo‘q. Jarvisga ovoz bilan ayting: “botga … funksiyasini qo‘sh”.'),admin_menu())
  elif data=='adm:ad':
   STATE[chat]={'step':'ad_text'}
   send(chat,'📢 REKLAMA\n'+LINE+'\nReklama xabarini yuboring (matn, rasm yoki video — izoh bilan).\nBekor qilish: /cancel')
  elif data=='adm:adgo':
   st=STATE.pop(chat,None)
   if not st or st.get('step')!='ad_confirm': send(chat,'Reklama topilmadi. Qaytadan boshlang.',admin_menu())
   else: send(chat,'🚀 Reklama yuborilmoqda...'); threading.Thread(target=run_broadcast,args=(chat,st['mid']),daemon=True).start()
 finally: c.close()

def multipart(fields, files):
 b='----jarvis'+uuid.uuid4().hex; out=[]
 for k,v in fields.items(): out.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'%(b,k,v)).encode())
 for k,(fn,data,ct) in files.items():
  out.append(('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: %s\r\n\r\n'%(b,k,fn,ct)).encode()+data+b'\r\n')
 out.append(('--%s--\r\n'%b).encode()); return b''.join(out),'multipart/form-data; boundary='+b

def send_banner(chat):
 global BANNER_FILE_ID
 try:
  if BANNER_FILE_ID: api('sendPhoto',{'chat_id':chat,'photo':BANNER_FILE_ID}); return
  if not os.path.exists(BANNER_PATH): return
  data=open(BANNER_PATH,'rb').read(); body,ct=multipart({'chat_id':chat},{'photo':('jarvis_banner.png',data,'image/png')})
  req=urllib.request.Request(API+'sendPhoto',data=body,headers={'Content-Type':ct})
  with urllib.request.urlopen(req,timeout=40) as r: res=json.loads(r.read().decode())
  BANNER_FILE_ID=res['result']['photo'][-1]['file_id']
 except Exception as e: print('Banner yuborilmadi:',repr(e))

def norm_phone(p): return ''.join(ch for ch in (p or '') if ch.isdigit())[-9:]

def link_meeting(c,chat,name,phone):
 n=norm_phone(phone)
 if len(n)<9: return
 hits=[]
 for mid,mph in c.execute("SELECT id,phone FROM meetings WHERE status!='Botga ulandi'").fetchall():
  if norm_phone(mph)==n: c.execute("UPDATE meetings SET status='Botga ulandi' WHERE id=?",(mid,)); hits.append(mid)
 c.commit()
 for mid in hits: log_event('meeting_linked',{'id':mid,'name':name,'phone':phone})

def bridge_key():
 k=os.environ.get('JARVIS_BRIDGE_KEY','').strip()
 if k: return k
 path=os.path.join(os.path.dirname(os.path.abspath(DB_PATH)),'jarvis_bridge.key')
 if os.path.exists(path): return open(path).read().strip()
 k=secrets.token_urlsafe(24); open(path,'w').write(k)
 try: os.chmod(path,0o600)
 except Exception: pass
 return k

BRIDGE_KEY=''
def clean_url(u):
 u=(u or '').strip()
 return u if u.startswith(('https://','http://','tg://')) and len(u)<300 and ' ' not in u else ''

class Bridge(BaseHTTPRequestHandler):
 server_version='JarvisBridge'
 def log_message(self,*a): pass
 def _send(self,code,obj):
  b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def _auth(self):
  got=self.headers.get('X-Jarvis-Key','')
  if not got or not hmac.compare_digest(got.encode(),BRIDGE_KEY.encode()): self._send(401,{'ok':False,'error':'ruxsat yo‘q'}); return False
  return True
 def _body(self):
  try: n=min(int(self.headers.get('Content-Length','0')),20000); return json.loads(self.rfile.read(n).decode() or '{}')
  except Exception: return {}
 def do_GET(self):
  if not self._auth(): return
  u=urllib.parse.urlparse(self.path); q=urllib.parse.parse_qs(u.query); c=db()
  try:
   if u.path=='/api/ping': self._send(200,{'ok':True,'bot':BOT_USERNAME,'version':'3.9'})
   elif u.path=='/api/status':
    g=lambda sql:c.execute(sql).fetchone()[0]
    self._send(200,{'ok':True,'bot':BOT_USERNAME,'users':g('SELECT COUNT(*) FROM users'),'orders':g('SELECT COUNT(*) FROM orders'),'new_orders':g("SELECT COUNT(*) FROM orders WHERE status='Yangi'"),'done_orders':g("SELECT COUNT(*) FROM orders WHERE status='Bajarildi'"),'meetings':g('SELECT COUNT(*) FROM meetings'),'features':g('SELECT COUNT(*) FROM features WHERE enabled=1'),'active_24h':g("SELECT COUNT(*) FROM users WHERE last_seen>=datetime('now','-1 day','localtime')")})
   elif u.path=='/api/users':
    rows=c.execute('SELECT chat_id,name,phone,address,created,last_seen FROM users ORDER BY COALESCE(last_seen,created) DESC LIMIT 50').fetchall()
    self._send(200,{'ok':True,'users':[dict(zip(('chat_id','name','phone','address','created','last_seen'),r)) for r in rows]})
   elif u.path=='/api/orders':
    st=(q.get('status') or ['Yangi'])[0]; rows=c.execute('SELECT id,name,phone,service,detail,slot,status FROM orders WHERE status=? ORDER BY slot LIMIT 30',(st,)).fetchall()
    self._send(200,{'ok':True,'orders':[dict(zip(('id','name','phone','service','detail','slot','status'),r)) for r in rows]})
   elif u.path=='/api/events':
    after=int((q.get('after') or ['0'])[0] or 0); rows=c.execute('SELECT id,kind,data,created FROM events WHERE id>? ORDER BY id LIMIT 50',(after,)).fetchall()
    last=c.execute('SELECT COALESCE(MAX(id),0) FROM events').fetchone()[0]
    self._send(200,{'ok':True,'last':last,'events':[{'id':i,'kind':k,'data':json.loads(d),'created':cr} for i,k,d,cr in rows]})
   elif u.path=='/api/meetings':
    rows=c.execute('SELECT id,name,phone,note,source,status,created FROM meetings ORDER BY id DESC LIMIT 30').fetchall()
    self._send(200,{'ok':True,'meetings':[dict(zip(('id','name','phone','note','source','status','created'),r)) for r in rows]})
   elif u.path=='/api/features':
    rows=c.execute('SELECT id,title,text,url,enabled FROM features ORDER BY id').fetchall()
    self._send(200,{'ok':True,'features':[dict(zip(('id','title','text','url','enabled'),r)) for r in rows]})
   else: self._send(404,{'ok':False,'error':'topilmadi'})
  finally: c.close()
 def do_POST(self):
  if not self._auth(): return
  u=urllib.parse.urlparse(self.path).path; d=self._body(); c=db()
  try:
   if u=='/api/features':
    title=str(d.get('title','')).strip()[:40]; text=str(d.get('text','')).strip()[:1500]; url=clean_url(d.get('url'))
    if not title or not text: self._send(400,{'ok':False,'error':'nom va matn kerak'}); return
    if c.execute('SELECT COUNT(*) FROM features WHERE enabled=1').fetchone()[0]>=MAX_FEATURES: self._send(400,{'ok':False,'error':'funksiyalar soni chegarada'}); return
    ex=c.execute('SELECT id FROM features WHERE lower(title)=lower(?)',(title,)).fetchone()
    if ex: c.execute('UPDATE features SET text=?,url=?,enabled=1 WHERE id=?',(text,url,ex[0])); fid=ex[0]
    else: fid=c.execute('INSERT INTO features(title,text,url,created) VALUES(?,?,?,?)',(title,text,url,datetime.now().isoformat(timespec='minutes'))).lastrowid
    c.commit(); log_event('feature_added',{'id':fid,'title':title}); self._send(200,{'ok':True,'id':fid,'title':title})
   elif u=='/api/features/remove':
    key=d.get('id') or d.get('title'); r=c.execute('SELECT id,title FROM features WHERE id=? OR lower(title)=lower(?)',(key if str(key).isdigit() else -1,str(key))).fetchone()
    if not r: self._send(404,{'ok':False,'error':'funksiya topilmadi'}); return
    c.execute('UPDATE features SET enabled=0 WHERE id=?',(r[0],)); c.commit(); log_event('feature_removed',{'id':r[0],'title':r[1]}); self._send(200,{'ok':True,'title':r[1]})
   elif u=='/api/meetings':
    name=str(d.get('name','')).strip()[:100] or 'Noma’lum'; phone=str(d.get('phone','')).strip()[:40]; note=str(d.get('note','')).strip()[:500]; src=str(d.get('source','qo‘ng‘iroq'))[:30]
    status='Botga yo‘naltirildi' if d.get('will_register') else 'Yangi'
    mid=c.execute('INSERT INTO meetings(name,phone,note,source,status,created) VALUES(?,?,?,?,?,?)',(name,phone,note,src,status,datetime.now().isoformat(timespec='minutes'))).lastrowid; c.commit()
    already=len(norm_phone(phone))>=9 and any(norm_phone(r[0])==norm_phone(phone) for r in c.execute('SELECT phone FROM users').fetchall())
    if already: c.execute("UPDATE meetings SET status='Botga ulandi' WHERE id=?",(mid,)); c.commit()
    log_event('meeting_added',{'id':mid,'name':name,'phone':phone,'note':note}); tell_admin(f'🤝 Yangi uchrashuv (Jarvis qo‘ng‘irog‘idan)\n👤 {name}\n📱 {phone}\n📝 {note}')
    self._send(200,{'ok':True,'id':mid})
   elif u=='/api/meetings/status':
    c.execute('UPDATE meetings SET status=? WHERE id=?',(str(d.get('status','Yangi'))[:30],int(d.get('id',0)))); c.commit(); self._send(200,{'ok':True})
   elif u=='/api/orders/status':
    oid=int(d.get('id',0)); stt='Bajarildi' if d.get('status')=='done' else 'Bekor qilindi'; r=c.execute('SELECT chat_id,service,slot FROM orders WHERE id=?',(oid,)).fetchone()
    if not r: self._send(404,{'ok':False,'error':'buyurtma topilmadi'}); return
    c.execute('UPDATE orders SET status=? WHERE id=?',(oid,)); c.commit()
    try: send(r[0],f'🔔 Buyurtmangiz holati yangilandi\n{LINE}\n🛠 {r[1]}\n📅 {r[2]}\n📌 Holat: {stt}')
    except Exception as e: print('Mijozga xabar yuborilmadi:',e)
    self._send(200,{'ok':True,'status':stt})
   else: self._send(404,{'ok':False,'error':'topilmadi'})
  except Exception as e: self._send(500,{'ok':False,'error':repr(e)[:120]})
  finally: c.close()

def start_bridge():
 global BRIDGE_KEY
 BRIDGE_KEY=bridge_key()
 try:
  srv=ThreadingHTTPServer((BRIDGE_HOST,BRIDGE_PORT),Bridge); threading.Thread(target=srv.serve_forever,daemon=True).start()
  print(f'JARVIS ko‘prigi: http://{BRIDGE_HOST}:{BRIDGE_PORT}  |  kalit: {BRIDGE_KEY}')
 except Exception as e: print('Ko‘prik ishga tushmadi:',repr(e))

def setup_bot():
 global BOT_USERNAME
 try: BOT_USERNAME=api('getMe').get('result',{}).get('username','')
 except Exception as e: print('getMe xatosi:',repr(e))
 try: api('setMyCommands',{'commands':[{'command':'start','description':'Boshlash'},{'command':'help','description':'Yordam'},{'command':'cancel','description':'Amalni bekor qilish'}]})
 except Exception: pass

def main():
 if not TOKEN: raise SystemExit('XATO: TELEGRAM_BOT_TOKEN muhit o‘zgaruvchisini kiriting. Tokenni kodga yozmang.')
 setup_bot(); start_bridge()
 print('TECH MAX bot ishga tushdi. To‘xtatish: Ctrl+C')
 offset=0
 while True:
  try:
   r=api('getUpdates',{'offset':offset,'timeout':25,'allowed_updates':['message','callback_query']})
   for u in r.get('result',[]):
    offset=u['update_id']+1
    try:
     if 'message' in u: handle_message(u['message'])
     elif 'callback_query' in u: handle_callback(u['callback_query'])
    except Exception as e: print('Update xatosi:',repr(e))
  except KeyboardInterrupt: break
  except Exception as e: print('Ulanish xatosi:',repr(e)); time.sleep(3)
if __name__=='__main__': main()
